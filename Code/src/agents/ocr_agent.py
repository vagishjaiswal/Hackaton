"""
OCR Agent - Image Processing with Tesseract and LLM

This module implements an agent that:
1. Reads image files from given paths
2. Performs OCR using Tesseract
3. Uses LLM to understand and enhance the extracted text
4. Stores results in ChromaDB vector database

Features:
- Multi-format image support (PNG, JPG, JPEG, TIFF, BMP)
- Automatic image preprocessing for better OCR results
- LLM-powered text understanding and enhancement
- ChromaDB integration for semantic search
- Batch processing support
- Comprehensive error handling

Author: AI Assistant
Date: 2024-11-28
"""

import os
import logging
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import hashlib
import json

try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
except ImportError:
    raise ImportError(
        "Required packages not installed. Please run: "
        "pip install pytesseract Pillow"
    )

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    raise ImportError(
        "ChromaDB not installed. Please run: pip install chromadb"
    )

from src.agents.base_agent import BaseAgent, BaseTool


# Configure logging
logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """
    Image preprocessing utilities for better OCR results.
    
    Applies various image enhancement techniques to improve
    text recognition accuracy.
    """
    
    @staticmethod
    def preprocess(image: Image.Image, enhance: bool = True) -> Image.Image:
        """
        Preprocess image for better OCR.
        
        Args:
            image: PIL Image object
            enhance: Apply enhancement filters
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')
        
        if enhance:
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
            
            # Apply denoising
            image = image.filter(ImageFilter.MedianFilter(size=3))
        
        return image
    
    @staticmethod
    def auto_rotate(image: Image.Image) -> Image.Image:
        """
        Auto-rotate image based on text orientation.
        
        Args:
            image: PIL Image object
            
        Returns:
            Rotated image
        """
        try:
            # Get OSD (Orientation and Script Detection)
            osd = pytesseract.image_to_osd(image)
            
            # Parse rotation angle
            rotation_angle = 0
            for line in osd.split('\n'):
                if 'Rotate:' in line:
                    rotation_angle = int(line.split(':')[1].strip())
                    break
            
            # Rotate if needed
            if rotation_angle != 0:
                image = image.rotate(rotation_angle, expand=True)
                logger.info(f"Auto-rotated image by {rotation_angle} degrees")
        
        except Exception as e:
            logger.warning(f"Could not auto-rotate: {e}")
        
        return image


class TesseractOCRTool(BaseTool):
    """
    Tool for performing OCR using Tesseract.
    
    Supports multiple languages and custom configurations.
    """
    
    def __init__(
        self,
        name: str = "tesseract_ocr",
        description: str = "Extract text from images using Tesseract OCR",
        tesseract_cmd: Optional[str] = None,
        lang: str = "eng",
        config: str = "--psm 6"
    ):
        """
        Initialize Tesseract OCR tool.
        
        Args:
            name: Tool name
            description: Tool description
            tesseract_cmd: Path to tesseract executable (optional)
            lang: Language(s) for OCR (e.g., 'eng', 'eng+fra')
            config: Tesseract configuration string
        """
        super().__init__(name, description)
        
        # Set tesseract command if provided
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        self.lang = lang
        self.config = config
        self.preprocessor = ImagePreprocessor()
        
        # Verify tesseract is available
        try:
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract version: {version}")
        except Exception as e:
            logger.error(f"Tesseract not found: {e}")
            raise RuntimeError(
                "Tesseract not installed. Please install it:\n"
                "- Windows: Download from GitHub and add to PATH\n"
                "- Linux: sudo apt-get install tesseract-ocr\n"
                "- macOS: brew install tesseract"
            )
    
    def execute(
        self,
        image_path: str,
        preprocess: bool = True,
        auto_rotate: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Extract text from an image.
        
        Args:
            image_path: Path to image file
            preprocess: Apply preprocessing
            auto_rotate: Auto-rotate based on text orientation
            **kwargs: Additional tesseract parameters
            
        Returns:
            Dictionary with OCR results
        """
        try:
            # Load image
            image = Image.open(image_path)
            logger.info(f"Loaded image: {image_path} ({image.size})")
            
            # Auto-rotate if enabled
            if auto_rotate:
                image = self.preprocessor.auto_rotate(image)
            
            # Preprocess if enabled
            if preprocess:
                image = self.preprocessor.preprocess(image)
            
            # Perform OCR
            text = pytesseract.image_to_string(
                image,
                lang=self.lang,
                config=self.config
            )
            
            # Get detailed data (with bounding boxes)
            data = pytesseract.image_to_data(
                image,
                lang=self.lang,
                config=self.config,
                output_type=pytesseract.Output.DICT
            )
            
            # Calculate confidence
            confidences = [
                float(conf) for conf in data['conf']
                if conf != '-1'
            ]
            avg_confidence = (
                sum(confidences) / len(confidences)
                if confidences else 0.0
            )
            
            return {
                "success": True,
                "text": text.strip(),
                "confidence": avg_confidence,
                "word_count": len(text.split()),
                "char_count": len(text),
                "image_path": image_path,
                "image_size": image.size,
                "detailed_data": data
            }
        
        except FileNotFoundError:
            logger.error(f"Image file not found: {image_path}")
            return {
                "success": False,
                "error": f"File not found: {image_path}"
            }
        
        except Exception as e:
            logger.error(f"OCR failed for {image_path}: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class ChromaDBManager:
    """
    Manager for ChromaDB operations.
    
    Handles collection creation, document insertion, and querying.
    """
    
    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "ocr_documents"
    ):
        """
        Initialize ChromaDB manager.
        
        Args:
            persist_directory: Directory to persist database
            collection_name: Name of the collection
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "OCR extracted documents"}
        )
        
        logger.info(
            f"ChromaDB initialized: {persist_directory}/{collection_name}"
        )
    
    def add_document(
        self,
        document_id: str,
        text: str,
        metadata: Dict[str, Any],
        embedding: Optional[List[float]] = None
    ) -> bool:
        """
        Add a document to the collection.
        
        Args:
            document_id: Unique document ID
            text: Document text
            metadata: Document metadata
            embedding: Optional pre-computed embedding
            
        Returns:
            True if successful
        """
        try:
            # Add to collection
            self.collection.add(
                ids=[document_id],
                documents=[text],
                metadatas=[metadata],
                embeddings=[embedding] if embedding else None
            )
            
            logger.info(f"Added document: {document_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            return False
    
    def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Query the collection.
        
        Args:
            query_text: Query string
            n_results: Number of results to return
            where: Optional metadata filter
            
        Returns:
            Query results
        """
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where
            )
            
            return results
        
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return {"error": str(e)}
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get collection statistics.
        
        Returns:
            Statistics dictionary
        """
        count = self.collection.count()
        
        return {
            "collection_name": self.collection_name,
            "document_count": count,
            "persist_directory": self.persist_directory
        }
    
    def delete_collection(self) -> bool:
        """
        Delete the collection.
        
        Returns:
            True if successful
        """
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            return False


class OCRAgent(BaseAgent):
    """
    OCR Agent for intelligent image-to-text processing.
    
    This agent combines Tesseract OCR with LLM understanding to:
    - Extract text from images
    - Understand and enhance extracted content
    - Categorize and tag documents
    - Store results in ChromaDB for semantic search
    
    Example:
        ```python
        agent = OCRAgent(
            name="ocr_processor",
            llm_provider="ollama",
            llm_model="llama3.2",
            chroma_db_path="./ocr_db"
        )
        
        result = await agent.process_image(
            "invoice.png",
            analyze=True
        )
        ```
    """
    
    def __init__(
        self,
        name: str = "ocr_agent",
        system_prompt: str = None,
        llm_provider: str = "ollama",
        llm_model: str = "llama3.2",
        llm_config: Optional[Dict[str, Any]] = None,
        tesseract_cmd: Optional[str] = None,
        tesseract_lang: str = "eng",
        chroma_db_path: str = "./chroma_db",
        chroma_collection: str = "ocr_documents",
        **kwargs
    ):
        """
        Initialize OCR Agent.
        
        Args:
            name: Agent name
            system_prompt: Custom system prompt (optional)
            llm_provider: LLM provider name
            llm_model: LLM model name
            llm_config: LLM configuration
            tesseract_cmd: Path to tesseract executable
            tesseract_lang: Tesseract language(s)
            chroma_db_path: ChromaDB persistence directory
            chroma_collection: ChromaDB collection name
            **kwargs: Additional BaseAgent arguments
        """
        # Default system prompt for OCR understanding
        if system_prompt is None:
            system_prompt = """You are an intelligent OCR assistant. Your role is to:
1. Analyze text extracted from images by Tesseract OCR
2. Correct any OCR errors (like 'O' vs '0', 'l' vs '1')
3. Understand the document type and purpose
4. Extract key information (dates, names, amounts, etc.)
5. Provide a structured summary of the content
6. Generate relevant tags for categorization

Always be precise and maintain the original meaning while improving clarity."""
        
        # Initialize base agent
        super().__init__(
            name=name,
            role="ocr_processor",
            system_prompt=system_prompt,
            llm_provider=llm_provider,
            llm_model=llm_model,
            llm_config=llm_config,
            **kwargs
        )
        
        # Initialize OCR tool
        self.ocr_tool = TesseractOCRTool(
            tesseract_cmd=tesseract_cmd,
            lang=tesseract_lang
        )
        self.register_tool(self.ocr_tool)
        
        # Initialize ChromaDB
        self.db_manager = ChromaDBManager(
            persist_directory=chroma_db_path,
            collection_name=chroma_collection
        )
        
        logger.info(f"OCR Agent '{name}' initialized successfully")
    
    def _generate_document_id(self, image_path: str) -> str:
        """
        Generate unique document ID from image path.
        
        Args:
            image_path: Path to image
            
        Returns:
            Unique document ID
        """
        # Use hash of absolute path + timestamp
        abs_path = os.path.abspath(image_path)
        timestamp = datetime.now().isoformat()
        content = f"{abs_path}_{timestamp}"
        
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    async def _analyze_text_with_llm(
        self,
        ocr_text: str,
        image_path: str
    ) -> Dict[str, Any]:
        """
        Analyze OCR text using LLM.
        
        Args:
            ocr_text: Text extracted by OCR
            image_path: Original image path
            
        Returns:
            Analysis results
        """
        # Create analysis prompt
        prompt = f"""Analyze the following text extracted from an image:

IMAGE PATH: {image_path}

EXTRACTED TEXT:
{ocr_text}

Please provide a JSON response with:
1. "corrected_text": Text with OCR errors corrected
2. "document_type": Type of document (e.g., invoice, receipt, letter, form, etc.)
3. "key_information": Dictionary of important extracted data
4. "summary": Brief summary of the content
5. "tags": List of relevant tags for categorization
6. "confidence": Your confidence in the analysis (0-100)

Respond ONLY with valid JSON, no additional text."""
        
        try:
            # Generate response
            response = await self._generate_response(prompt, use_history=False)
            
            # Try to parse JSON
            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            analysis = json.loads(response)
            
            return {
                "success": True,
                "analysis": analysis
            }
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"Response was: {response}")
            
            # Return fallback analysis
            return {
                "success": False,
                "error": "JSON parsing failed",
                "raw_response": response,
                "analysis": {
                    "corrected_text": ocr_text,
                    "document_type": "unknown",
                    "key_information": {},
                    "summary": "Failed to analyze",
                    "tags": ["unprocessed"],
                    "confidence": 0
                }
            }
        
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def process_image(
        self,
        image_path: str,
        analyze: bool = True,
        save_to_db: bool = True,
        preprocess: bool = True,
        auto_rotate: bool = True
    ) -> Dict[str, Any]:
        """
        Process an image: OCR + LLM analysis + ChromaDB storage.
        
        Args:
            image_path: Path to image file
            analyze: Use LLM to analyze text
            save_to_db: Save results to ChromaDB
            preprocess: Apply image preprocessing
            auto_rotate: Auto-rotate image
            
        Returns:
            Processing results
        """
        logger.info(f"Processing image: {image_path}")
        
        # Step 1: Perform OCR
        ocr_result = self.ocr_tool.execute(
            image_path=image_path,
            preprocess=preprocess,
            auto_rotate=auto_rotate
        )
        
        if not ocr_result["success"]:
            return {
                "success": False,
                "error": ocr_result.get("error", "OCR failed")
            }
        
        extracted_text = ocr_result["text"]
        
        if not extracted_text or len(extracted_text.strip()) == 0:
            return {
                "success": False,
                "error": "No text extracted from image"
            }
        
        # Step 2: Analyze with LLM (if enabled)
        analysis_result = None
        if analyze:
            analysis_result = await self._analyze_text_with_llm(
                extracted_text,
                image_path
            )
        
        # Step 3: Save to ChromaDB (if enabled)
        document_id = self._generate_document_id(image_path)
        
        if save_to_db:
            # Prepare metadata
            metadata = {
                "image_path": image_path,
                "ocr_confidence": ocr_result["confidence"],
                "word_count": ocr_result["word_count"],
                "processed_at": datetime.now().isoformat(),
                "document_id": document_id
            }
            
            # Add analysis metadata if available
            if analysis_result and analysis_result.get("success"):
                analysis = analysis_result["analysis"]
                metadata.update({
                    "document_type": analysis.get("document_type", "unknown"),
                    "tags": json.dumps(analysis.get("tags", [])),
                    "analysis_confidence": analysis.get("confidence", 0)
                })
            
            # Save to ChromaDB
            text_to_store = (
                analysis_result["analysis"]["corrected_text"]
                if analysis_result and analysis_result.get("success")
                else extracted_text
            )
            
            self.db_manager.add_document(
                document_id=document_id,
                text=text_to_store,
                metadata=metadata
            )
        
        # Return complete result
        return {
            "success": True,
            "document_id": document_id,
            "ocr_result": ocr_result,
            "analysis": analysis_result if analyze else None,
            "stored_in_db": save_to_db
        }
    
    async def process_batch(
        self,
        image_paths: List[str],
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Process multiple images in batch.
        
        Args:
            image_paths: List of image paths
            **kwargs: Arguments for process_image
            
        Returns:
            List of processing results
        """
        results = []
        
        for i, image_path in enumerate(image_paths, 1):
            logger.info(f"Processing image {i}/{len(image_paths)}: {image_path}")
            
            result = await self.process_image(image_path, **kwargs)
            results.append(result)
        
        return results
    
    def search_documents(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Search processed documents in ChromaDB.
        
        Args:
            query: Search query
            n_results: Number of results
            filter_metadata: Optional metadata filter
            
        Returns:
            Search results
        """
        return self.db_manager.query(
            query_text=query,
            n_results=n_results,
            where=filter_metadata
        )
    
    def get_db_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Statistics dictionary
        """
        return self.db_manager.get_collection_stats()
    
    async def execute(self, task: str, **kwargs) -> str:
        """
        Execute a task (required by BaseAgent).
        
        Args:
            task: Task description
            **kwargs: Task parameters
            
        Returns:
            Task result
        """
        # Parse task
        if "image_path" in kwargs:
            result = await self.process_image(
                image_path=kwargs["image_path"],
                **{k: v for k, v in kwargs.items() if k != "image_path"}
            )
            return json.dumps(result, indent=2)
        
        elif "image_paths" in kwargs:
            results = await self.process_batch(
                image_paths=kwargs["image_paths"],
                **{k: v for k, v in kwargs.items() if k != "image_paths"}
            )
            return json.dumps(results, indent=2)
        
        else:
            return json.dumps({
                "error": "No image_path or image_paths provided"
            })
