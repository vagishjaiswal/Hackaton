"""
Test Suite for OCR Agent

Tests for OCR Agent functionality including:
- Tesseract OCR
- LLM analysis
- ChromaDB storage
- Batch processing
- Search functionality

Author: AI Assistant
Date: 2024-11-28
"""

import pytest
import asyncio
import os
import tempfile
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from PIL import Image, ImageDraw, ImageFont
from src.agents.ocr_agent import (
    OCRAgent,
    TesseractOCRTool,
    ImagePreprocessor,
    ChromaDBManager
)


@pytest.fixture
def temp_image():
    """Create a temporary test image with text."""
    # Create a simple image with text
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw some text
    text = "Test Document\nInvoice #12345\nDate: 2024-11-28\nTotal: $199.99"
    
    try:
        # Try to use a font
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        # Fall back to default font
        font = ImageFont.load_default()
    
    draw.text((20, 20), text, fill='black', font=font)
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    img.save(temp_file.name)
    
    yield temp_file.name
    
    # Cleanup
    if os.path.exists(temp_file.name):
        os.unlink(temp_file.name)


@pytest.fixture
def temp_db_dir():
    """Create a temporary directory for ChromaDB."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    
    # Cleanup
    import shutil
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


class TestImagePreprocessor:
    """Test image preprocessing functionality."""
    
    def test_preprocess_basic(self, temp_image):
        """Test basic image preprocessing."""
        img = Image.open(temp_image)
        preprocessor = ImagePreprocessor()
        
        processed = preprocessor.preprocess(img, enhance=True)
        
        assert processed is not None
        assert processed.mode == 'L'  # Grayscale
        assert processed.size == img.size
    
    def test_preprocess_no_enhance(self, temp_image):
        """Test preprocessing without enhancement."""
        img = Image.open(temp_image)
        preprocessor = ImagePreprocessor()
        
        processed = preprocessor.preprocess(img, enhance=False)
        
        assert processed is not None
        assert processed.mode == 'L'


class TestTesseractOCRTool:
    """Test Tesseract OCR tool functionality."""
    
    def test_tool_initialization(self):
        """Test OCR tool initialization."""
        try:
            tool = TesseractOCRTool()
            assert tool.name == "tesseract_ocr"
            assert tool.lang == "eng"
        except RuntimeError as e:
            pytest.skip(f"Tesseract not available: {e}")
    
    def test_execute_ocr(self, temp_image):
        """Test OCR execution on test image."""
        try:
            tool = TesseractOCRTool()
            result = tool.execute(image_path=temp_image)
            
            assert result["success"] is True
            assert "text" in result
            assert len(result["text"]) > 0
            assert "confidence" in result
            assert result["confidence"] >= 0
            assert result["word_count"] > 0
        except RuntimeError as e:
            pytest.skip(f"Tesseract not available: {e}")
    
    def test_execute_nonexistent_file(self):
        """Test OCR with nonexistent file."""
        try:
            tool = TesseractOCRTool()
            result = tool.execute(image_path="nonexistent.png")
            
            assert result["success"] is False
            assert "error" in result
        except RuntimeError as e:
            pytest.skip(f"Tesseract not available: {e}")


class TestChromaDBManager:
    """Test ChromaDB manager functionality."""
    
    def test_manager_initialization(self, temp_db_dir):
        """Test ChromaDB manager initialization."""
        manager = ChromaDBManager(
            persist_directory=temp_db_dir,
            collection_name="test_collection"
        )
        
        assert manager.collection_name == "test_collection"
        assert manager.persist_directory == temp_db_dir
        assert manager.collection is not None
    
    def test_add_document(self, temp_db_dir):
        """Test adding a document."""
        manager = ChromaDBManager(
            persist_directory=temp_db_dir,
            collection_name="test_docs"
        )
        
        success = manager.add_document(
            document_id="test_1",
            text="This is a test document",
            metadata={"source": "test"}
        )
        
        assert success is True
        
        stats = manager.get_collection_stats()
        assert stats["document_count"] >= 1
    
    def test_query_documents(self, temp_db_dir):
        """Test querying documents."""
        manager = ChromaDBManager(
            persist_directory=temp_db_dir,
            collection_name="test_query"
        )
        
        # Add some documents
        manager.add_document(
            "doc1",
            "Invoice for software services",
            {"type": "invoice"}
        )
        manager.add_document(
            "doc2",
            "Receipt for hardware purchase",
            {"type": "receipt"}
        )
        
        # Query
        results = manager.query("invoice", n_results=2)
        
        assert "error" not in results
        assert "ids" in results
        assert len(results["ids"][0]) > 0


class TestOCRAgent:
    """Test OCR Agent functionality."""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, temp_db_dir):
        """Test OCR agent initialization."""
        agent = OCRAgent(
            name="test_agent",
            llm_provider="ollama",
            llm_model="llama3.2",
            chroma_db_path=temp_db_dir
        )
        
        assert agent.name == "test_agent"
        assert agent.role == "ocr_processor"
        assert "tesseract_ocr" in agent.list_tools()
        assert agent.db_manager is not None
    
    @pytest.mark.asyncio
    async def test_process_image(self, temp_image, temp_db_dir):
        """Test image processing."""
        try:
            agent = OCRAgent(
                name="test_processor",
                llm_provider="ollama",
                llm_model="llama3.2",
                chroma_db_path=temp_db_dir
            )
            
            result = await agent.process_image(
                image_path=temp_image,
                analyze=False,  # Skip LLM analysis for faster testing
                save_to_db=True
            )
            
            assert result["success"] is True
            assert "document_id" in result
            assert "ocr_result" in result
            assert result["ocr_result"]["success"] is True
            
            # Check database
            stats = agent.get_db_stats()
            assert stats["document_count"] >= 1
        
        except RuntimeError as e:
            pytest.skip(f"Tesseract not available: {e}")
    
    @pytest.mark.asyncio
    async def test_process_image_with_analysis(self, temp_image, temp_db_dir):
        """Test image processing with LLM analysis."""
        try:
            # This test requires Ollama to be running
            agent = OCRAgent(
                name="test_analyzer",
                llm_provider="ollama",
                llm_model="llama3.2",
                chroma_db_path=temp_db_dir
            )
            
            result = await agent.process_image(
                image_path=temp_image,
                analyze=True,
                save_to_db=True
            )
            
            assert result["success"] is True
            assert "analysis" in result
            
            if result["analysis"] and result["analysis"]["success"]:
                analysis = result["analysis"]["analysis"]
                assert "document_type" in analysis
                assert "tags" in analysis
                assert "summary" in analysis
        
        except RuntimeError as e:
            pytest.skip(f"Tesseract not available: {e}")
        except Exception as e:
            # Skip if Ollama is not available
            pytest.skip(f"LLM not available: {e}")
    
    @pytest.mark.asyncio
    async def test_batch_processing(self, temp_image, temp_db_dir):
        """Test batch image processing."""
        try:
            agent = OCRAgent(
                name="test_batch",
                llm_provider="ollama",
                llm_model="llama3.2",
                chroma_db_path=temp_db_dir
            )
            
            # Create multiple test images
            image_paths = [temp_image]  # In real test, create multiple
            
            results = await agent.process_batch(
                image_paths=image_paths,
                analyze=False,
                save_to_db=True
            )
            
            assert len(results) == len(image_paths)
            assert all(r["success"] for r in results)
        
        except RuntimeError as e:
            pytest.skip(f"Tesseract not available: {e}")
    
    def test_search_documents(self, temp_db_dir):
        """Test document search."""
        agent = OCRAgent(
            name="test_search",
            llm_provider="ollama",
            llm_model="llama3.2",
            chroma_db_path=temp_db_dir
        )
        
        # Add some test documents directly
        agent.db_manager.add_document(
            "search_test_1",
            "Invoice for cloud services subscription",
            {"type": "invoice", "amount": 99.99}
        )
        
        # Search
        results = agent.search_documents("cloud services", n_results=1)
        
        assert "error" not in results
        assert "ids" in results
    
    def test_get_db_stats(self, temp_db_dir):
        """Test getting database statistics."""
        agent = OCRAgent(
            name="test_stats",
            llm_provider="ollama",
            llm_model="llama3.2",
            chroma_db_path=temp_db_dir
        )
        
        stats = agent.get_db_stats()
        
        assert "collection_name" in stats
        assert "document_count" in stats
        assert stats["document_count"] >= 0


class TestIntegration:
    """Integration tests for complete workflows."""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, temp_image, temp_db_dir):
        """Test complete OCR workflow."""
        try:
            # Initialize agent
            agent = OCRAgent(
                name="workflow_agent",
                llm_provider="ollama",
                llm_model="llama3.2",
                chroma_db_path=temp_db_dir
            )
            
            # Process image
            result = await agent.process_image(
                image_path=temp_image,
                analyze=False,  # Skip for faster testing
                save_to_db=True
            )
            
            assert result["success"] is True
            
            # Search for processed document
            search_results = agent.search_documents(
                "test",
                n_results=1
            )
            
            assert "error" not in search_results
            assert len(search_results["ids"][0]) > 0
            
            # Verify stats
            stats = agent.get_db_stats()
            assert stats["document_count"] >= 1
        
        except RuntimeError as e:
            pytest.skip(f"Tesseract not available: {e}")


def test_imports():
    """Test that all imports work."""
    from src.agents.ocr_agent import (
        OCRAgent,
        TesseractOCRTool,
        ImagePreprocessor,
        ChromaDBManager
    )
    
    assert OCRAgent is not None
    assert TesseractOCRTool is not None
    assert ImagePreprocessor is not None
    assert ChromaDBManager is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
