# OCR Agent - Quick Reference

## Installation (One Command)
```bash
pip install pytesseract Pillow chromadb
```

Then install Tesseract:
- **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
- **Linux**: `sudo apt-get install tesseract-ocr`
- **macOS**: `brew install tesseract`

---

## Minimal Working Example

```python
import asyncio
from src.agents.ocr_agent import OCRAgent

async def main():
    agent = OCRAgent(name="ocr", llm_provider="ollama", llm_model="llama3.2")
    result = await agent.process_image("image.png")
    print(result["ocr_result"]["text"])

asyncio.run(main())
```

---

## Common Operations

### Process Single Image
```python
result = await agent.process_image(
    image_path="document.png",
    analyze=True,       # Use LLM
    save_to_db=True     # Save to ChromaDB
)
```

### Process Multiple Images
```python
results = await agent.process_batch(
    image_paths=["img1.png", "img2.jpg"],
    analyze=True
)
```

### Search Documents
```python
results = agent.search_documents("invoice 2024", n_results=5)
```

### Get Database Stats
```python
stats = agent.get_db_stats()
print(f"Documents: {stats['document_count']}")
```

---

## Configuration Options

```python
agent = OCRAgent(
    name="my_agent",
    llm_provider="ollama",           # or "openai"
    llm_model="llama3.2",            # or "gpt-4"
    llm_config={                     # Optional
        "temperature": 0.3,
        "max_tokens": 2000
    },
    tesseract_cmd=None,              # Path to tesseract (Windows)
    tesseract_lang="eng",            # or "eng+fra+spa"
    chroma_db_path="./ocr_db",
    chroma_collection="documents",
    system_prompt="Custom prompt"    # Optional
)
```

---

## Result Structure

```python
{
    "success": True,
    "document_id": "abc123",
    "ocr_result": {
        "text": "Extracted text...",
        "confidence": 95.5,
        "word_count": 150
    },
    "analysis": {
        "document_type": "invoice",
        "tags": ["finance", "2024"],
        "summary": "...",
        "key_information": {...}
    }
}
```

---

## Common Patterns

### Invoice Processing
```python
agent = OCRAgent(
    system_prompt="Extract: vendor, invoice #, date, amount, line items"
)
result = await agent.process_image("invoice.png", analyze=True)
```

### Receipt Scanner
```python
result = await agent.process_image("receipt.jpg")
total = result["analysis"]["analysis"]["key_information"].get("total")
```

### Batch Document Classifier
```python
files = ["doc1.png", "doc2.jpg", "doc3.tiff"]
results = await agent.process_batch(files, analyze=True)

for r in results:
    doc_type = r["analysis"]["analysis"]["document_type"]
    print(f"Type: {doc_type}")
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Tesseract not found | Set `tesseract_cmd=r"C:\...\tesseract.exe"` |
| Low confidence | Enable `preprocess=True` and `auto_rotate=True` |
| LLM fails | Check Ollama is running: `ollama list` |
| Slow processing | Set `analyze=False` for faster OCR-only |

---

## Performance Tips

✅ Use `preprocess=True` for better OCR accuracy  
✅ Batch process 10-50 images at once  
✅ Set `analyze=False` if you don't need LLM  
✅ Use `temperature=0.2` for consistent results  
✅ High-res images (300 DPI) work best  

---

## File Locations

- **Agent Code**: `src/agents/ocr_agent.py`
- **Examples**: `tests/workflow/example_ocr_agent.py`
- **Tests**: `tests/test_ocr_agent.py`
- **Full Guide**: `docs/OCR_AGENT_GUIDE.md`

---

## API Summary

| Method | Purpose | Async |
|--------|---------|-------|
| `process_image()` | Process single image | ✅ Yes |
| `process_batch()` | Process multiple images | ✅ Yes |
| `search_documents()` | Search ChromaDB | ❌ No |
| `get_db_stats()` | Get database info | ❌ No |

---

## Integration Examples

### Flask API
```python
from flask import Flask, request, jsonify
app = Flask(__name__)
agent = OCRAgent(name="api")

@app.route('/ocr', methods=['POST'])
def ocr():
    file = request.files['file']
    file.save("temp.png")
    result = asyncio.run(agent.process_image("temp.png"))
    return jsonify(result)
```

### Streamlit
```python
import streamlit as st
uploaded = st.file_uploader("Upload Image")
if uploaded:
    result = asyncio.run(agent.process_image(uploaded.name))
    st.text_area("Text", result["ocr_result"]["text"])
```

---

## Dependencies

```txt
pytesseract>=0.3.10
Pillow>=10.0.0
chromadb>=0.4.0
```

Plus your existing agent framework dependencies.

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Run example: `python tests/workflow/example_ocr_agent.py`
3. ✅ Read full guide: `docs/OCR_AGENT_GUIDE.md`
4. ✅ Run tests: `pytest tests/test_ocr_agent.py`
5. ✅ Adapt for your use case!

---

**Need Help?** Check the full guide in `docs/OCR_AGENT_GUIDE.md`
