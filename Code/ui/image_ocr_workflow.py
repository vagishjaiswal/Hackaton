import streamlit as st
import sys
from pathlib import Path

# Add project root to sys.path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agents.ocr_agent import OCRAgent

st.set_page_config(page_title="Image OCR & Vision Workflow", layout="centered")
st.title("🖼️ Image OCR & Vision Workflow")

st.write("""
Upload or enter the path to an image file. The image will be processed (OCR + Vision LLM) and the results will be stored in ChromaDB.
""")

# --- Input ---
uploaded_file = st.file_uploader("Upload an image file", type=["png", "jpg", "jpeg", "bmp", "tiff", "gif"])
file_path = st.text_input("Or enter image file path (absolute or relative to Code directory):")
provider = st.selectbox("Select Vision Provider", ["openai", "ollama"])

def save_uploaded_file(uploaded_file):
    temp_dir = Path("temp_uploads")
    temp_dir.mkdir(exist_ok=True)
    temp_path = temp_dir / uploaded_file.name
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(temp_path)

if st.button("Process Image"):
    image_to_process = None
    if uploaded_file is not None:
        image_to_process = save_uploaded_file(uploaded_file)
    elif file_path and Path(file_path).exists():
        image_to_process = file_path
    else:
        st.error("Please upload a file or enter a valid image file path.")
    if image_to_process:
        st.info(f"Processing {image_to_process} with {provider}...")
        agent = OCRAgent(provider=provider)
        chunks = agent.process_document(image_to_process)
        st.success(f"Processed and stored {len(chunks)} chunk(s) in ChromaDB.")
        for i, chunk in enumerate(chunks, 1):
            st.write(f"--- Chunk {i} ---")
            st.write("Text:", chunk["text"])
            st.write("Metadata:", chunk["metadata"])
