import os
from pathlib import Path
from typing import List, Dict
import base64
from openai import OpenAI
from PyPDF2 import PdfReader
from docx import Document
from PIL import Image
import io
import fitz  # PyMuPDF
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
import requests

load_dotenv()

class OCRAgent:
    def __init__(self, provider: str = 'openai', chroma_db_path: str = './chroma_db', chroma_collection: str = 'ocr_documents'):
        self.provider = provider.lower()
        self.chunk_size = 1000
        self.chunk_overlap = 200
        self.chroma_db_path = chroma_db_path
        self.chroma_collection = chroma_collection
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY')) if self.provider == 'openai' else None
        self.chroma_client = chromadb.PersistentClient(
            path=chroma_db_path,
            settings=Settings(anonymized_telemetry=False, allow_reset=True)
        )
        self.chroma_collection_obj = self.chroma_client.get_or_create_collection(
            name=chroma_collection,
            metadata={"description": "OCR document chunks with vision analysis"}
        )
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'llava-phi3')
        self.openai_model = os.getenv('OPENAI_VISION_MODEL', 'gpt-4o')

    def process_document(self, file_path: str) -> List[Dict]:
        ext = Path(file_path).suffix.lower()
        if ext == '.pdf':
            chunks = self._process_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            chunks = self._process_docx(file_path)
        elif ext == '.txt':
            chunks = self._process_txt(file_path)
        elif ext in ['.png', '.jpg', '.jpeg']:
            chunks = self._process_image(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
        for chunk in chunks:
            self._store_in_chromadb(chunk)
        return chunks

    def _process_pdf(self, file_path: str) -> List[Dict]:
        chunks = []
        reader = PdfReader(file_path)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"
        if full_text.strip():
            chunks.extend(self._chunk_text(full_text, {"source": file_path, "type": "text"}))
        doc = fitz.open(file_path)
        for page_num, page in enumerate(doc):
            images = page.get_images()
            for img_idx, img in enumerate(images):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_description = self._analyze_image(image_bytes)
                    if image_description:
                        chunk = {
                            "text": f"[IMAGE DESCRIPTION] {image_description}",
                            "metadata": {
                                "source": file_path,
                                "page": page_num + 1,
                                "type": "image"
                            }
                        }
                        chunks.append(chunk)
                except Exception as e:
                    print(f"Error processing image: {e}")
        return chunks

    def _process_docx(self, file_path: str) -> List[Dict]:
        chunks = []
        doc = Document(file_path)
        full_text = "\n".join([para.text for para in doc.paragraphs])
        if full_text.strip():
            chunks.extend(self._chunk_text(full_text, {"source": file_path, "type": "text"}))
        for rel in doc.part.rels.values():
            if "image" in rel.target_ref:
                try:
                    image_data = rel.target_part.blob
                    image_description = self._analyze_image(image_data)
                    if image_description:
                        chunk = {
                            "text": f"[IMAGE DESCRIPTION] {image_description}",
                            "metadata": {
                                "source": file_path,
                                "type": "image"
                            }
                        }
                        chunks.append(chunk)
                except Exception as e:
                    print(f"Error processing image: {e}")
        return chunks

    def _process_txt(self, file_path: str) -> List[Dict]:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        return self._chunk_text(text, {"source": file_path, "type": "text"})

    def _process_image(self, file_path: str) -> List[Dict]:
        with open(file_path, 'rb') as f:
            image_data = f.read()
        description = self._analyze_image(image_data)
        if description:
            chunk = {
                "text": f"[IMAGE DESCRIPTION] {description}",
                "metadata": {
                    "source": file_path,
                    "type": "image"
                }
            }
            return [chunk]
        return []

    def _analyze_image(self, image_bytes: bytes) -> str:
        if self.provider == 'openai':
            try:
                base64_image = base64.b64encode(image_bytes).decode('utf-8')
                response = self.openai_client.chat.completions.create(
                    model=self.openai_model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Describe this image in detail, including any text, diagrams, charts, or important visual elements."
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=500
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"Error analyzing image (OpenAI): {e}")
                return ""
        elif self.provider == 'ollama':
            try:
                from PIL import Image as PILImage
                from io import BytesIO
                image = PILImage.open(BytesIO(image_bytes))
                buf = BytesIO()
                image.save(buf, format="JPEG")
                base64_image = base64.b64encode(buf.getvalue()).decode('utf-8')
                prompt = "Describe this image in detail, including any text, diagrams, charts, or important visual elements."
                payload = {
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "images": [base64_image],
                    "stream": False,
                    "options": {"temperature": 0.3, "num_predict": 1024}
                }
                response = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=120)
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")
            except Exception as e:
                print(f"Error analyzing image (Ollama): {e}")
                return ""
        else:
            print(f"Unknown provider: {self.provider}")
            return ""

    def _chunk_text(self, text: str, metadata: Dict) -> List[Dict]:
        chunks = []
        words = text.split()
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            if chunk_text.strip():
                chunks.append({
                    "text": chunk_text,
                    "metadata": metadata.copy()
                })
        return chunks

    def _store_in_chromadb(self, chunk: Dict):
        try:
            self.chroma_collection_obj.add(
                ids=[str(hash(chunk['text'] + str(chunk['metadata'])))],
                documents=[chunk['text']],
                metadatas=[chunk['metadata']]
            )
        except Exception as e:
            print(f"Error storing in ChromaDB: {e}")
