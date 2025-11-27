"""
Example: Using the OCR Agent

This script demonstrates how to use the OCR Agent to:
1. Extract text from images using Tesseract
2. Analyze the content with LLM
3. Store results in ChromaDB
4. Search through processed documents

Author: AI Assistant
Date: 2024-11-28
"""

import asyncio
import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agents.ocr_agent import OCRAgent


async def example_single_image():
    """Example: Process a single image."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Processing Single Image")
    print("="*60)
    
    # Initialize OCR Agent
    agent = OCRAgent(
        name="my_ocr_agent",
        llm_provider="ollama",  # or "openai"
        llm_model="llama3.2",   # or "gpt-4"
        chroma_db_path="./ocr_database",
        chroma_collection="my_documents"
    )
    
    # Path to your image (update this!)
    image_path = "path/to/your/image.png"
    
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        print("Please update the image_path in this script!")
        return
    
    # Process the image
    print(f"\n📸 Processing: {image_path}")
    result = await agent.process_image(
        image_path=image_path,
        analyze=True,      # Use LLM for analysis
        save_to_db=True,   # Save to ChromaDB
        preprocess=True,   # Apply image preprocessing
        auto_rotate=True   # Auto-rotate based on text
    )
    
    # Display results
    if result["success"]:
        print("\n✅ Processing successful!")
        print(f"Document ID: {result['document_id']}")
        
        # OCR Results
        ocr = result["ocr_result"]
        print(f"\n📝 OCR Results:")
        print(f"  Confidence: {ocr['confidence']:.2f}%")
        print(f"  Word Count: {ocr['word_count']}")
        print(f"  Text Preview: {ocr['text'][:200]}...")
        
        # LLM Analysis
        if result["analysis"] and result["analysis"]["success"]:
            analysis = result["analysis"]["analysis"]
            print(f"\n🤖 LLM Analysis:")
            print(f"  Document Type: {analysis.get('document_type', 'N/A')}")
            print(f"  Tags: {', '.join(analysis.get('tags', []))}")
            print(f"  Summary: {analysis.get('summary', 'N/A')}")
            print(f"  Confidence: {analysis.get('confidence', 0)}%")
            
            if analysis.get('key_information'):
                print(f"\n📊 Key Information:")
                for key, value in analysis['key_information'].items():
                    print(f"  {key}: {value}")
    else:
        print(f"\n❌ Processing failed: {result.get('error', 'Unknown error')}")


async def example_batch_processing():
    """Example: Process multiple images in batch."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Batch Processing Multiple Images")
    print("="*60)
    
    # Initialize agent
    agent = OCRAgent(
        name="batch_ocr_agent",
        llm_provider="ollama",
        llm_model="llama3.2"
    )
    
    # List of images to process (update these!)
    image_paths = [
        "path/to/image1.png",
        "path/to/image2.jpg",
        "path/to/image3.tiff"
    ]
    
    # Filter only existing files
    existing_paths = [p for p in image_paths if os.path.exists(p)]
    
    if not existing_paths:
        print("❌ No images found. Please update the image_paths list!")
        return
    
    print(f"\n📸 Processing {len(existing_paths)} images...")
    
    # Process batch
    results = await agent.process_batch(
        image_paths=existing_paths,
        analyze=True,
        save_to_db=True
    )
    
    # Display summary
    successful = sum(1 for r in results if r["success"])
    print(f"\n✅ Processed {successful}/{len(results)} images successfully")
    
    for i, result in enumerate(results, 1):
        status = "✅" if result["success"] else "❌"
        print(f"{status} Image {i}: {existing_paths[i-1]}")


async def example_search_documents():
    """Example: Search processed documents."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Searching Processed Documents")
    print("="*60)
    
    # Initialize agent (connects to existing database)
    agent = OCRAgent(
        name="search_agent",
        llm_provider="ollama",
        llm_model="llama3.2",
        chroma_db_path="./ocr_database"
    )
    
    # Get database stats
    stats = agent.get_db_stats()
    print(f"\n📊 Database Stats:")
    print(f"  Collection: {stats['collection_name']}")
    print(f"  Documents: {stats['document_count']}")
    
    if stats['document_count'] == 0:
        print("\n⚠️  No documents in database. Process some images first!")
        return
    
    # Search examples
    search_queries = [
        "invoice",
        "receipt",
        "date 2024",
        "total amount"
    ]
    
    for query in search_queries:
        print(f"\n🔍 Searching for: '{query}'")
        results = agent.search_documents(query, n_results=3)
        
        if "error" not in results:
            found = len(results["ids"][0]) if results["ids"] else 0
            print(f"  Found {found} results")
            
            # Display top result
            if found > 0:
                top_doc = results["documents"][0][0]
                top_metadata = results["metadatas"][0][0]
                print(f"  Top Result:")
                print(f"    Type: {top_metadata.get('document_type', 'N/A')}")
                print(f"    Preview: {top_doc[:100]}...")
        else:
            print(f"  ❌ Search failed: {results['error']}")


async def example_custom_configuration():
    """Example: Advanced configuration options."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Custom Configuration")
    print("="*60)
    
    # Custom LLM configuration
    llm_config = {
        "temperature": 0.3,  # Lower = more focused
        "max_tokens": 2000,
        "timeout": 120
    }
    
    # Initialize with custom settings
    agent = OCRAgent(
        name="custom_ocr_agent",
        llm_provider="ollama",
        llm_model="llama3.2",
        llm_config=llm_config,
        tesseract_lang="eng+fra",  # English + French
        chroma_db_path="./custom_ocr_db",
        system_prompt="""You are a specialized invoice analyzer.
        Extract all financial information, dates, and vendor details.
        Focus on accuracy and structure."""
    )
    
    print("✅ Agent initialized with custom configuration")
    print(f"  LLM Config: {llm_config}")
    print(f"  Languages: eng+fra")
    print(f"  Custom system prompt applied")


async def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("OCR AGENT - EXAMPLES")
    print("="*60)
    print("\nThis script demonstrates the OCR Agent capabilities.")
    print("Make sure to:")
    print("  1. Install dependencies: pip install pytesseract Pillow chromadb")
    print("  2. Install Tesseract OCR on your system")
    print("  3. Update image paths in the examples")
    print("  4. Have Ollama running (or configure OpenAI)")
    
    # Run examples
    try:
        await example_single_image()
        await example_batch_processing()
        await example_search_documents()
        await example_custom_configuration()
        
        print("\n" + "="*60)
        print("All examples completed!")
        print("="*60)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
