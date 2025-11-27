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
        provider="ollama",  # or "openai"
        chroma_db_path="./ocr_database",
        chroma_collection="my_documents"
    )
    
    # Path to your image (update this!)
    image_path = "data/input/image.png"
    
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
        
        # Vision Analysis
        if result["vision_data"]:
            vision = result["vision_data"]
            print(f"\n👁️ Vision Analysis:")
            print(f"  Description: {vision.get('overall_description', 'N/A')[:200]}...")
            if vision.get('objects'):
                print(f"  Objects: {', '.join([obj.get('name', '') for obj in vision['objects'][:5]])}")
            if vision.get('colors', {}).get('dominant_colors'):
                print(f"  Colors: {', '.join(vision['colors']['dominant_colors'])}")
        
        # Combined Analysis
        if result["combined_analysis"] and result["combined_analysis"]["success"]:
            analysis = result["combined_analysis"]["analysis"]
            print(f"\n🤖 Combined Analysis:")
            print(f"  Document Type: {analysis.get('document_type', 'N/A')}")
            print(f"  Tags: {', '.join(analysis.get('tags', []))}")
            print(f"  Summary: {analysis.get('comprehensive_summary', 'N/A')[:200]}...")
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
        provider="ollama"
    )
    
    # List of images to process (update these!)
    image_paths = [
        "data/input/200w.gif",
        "data/input/image.png"
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
        details = ""
        if result.get("processing_summary"):
            summary = result["processing_summary"]
            details = f" - OCR: {summary.get('ocr_success')}, Vision: {summary.get('vision_success')}, Analysis: {summary.get('analysis_success')}"
        print(f"{status} Image {i}: {existing_paths[i-1]}{details}")


async def example_search_documents():
    """Example: Search processed documents."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Searching Processed Documents")
    print("="*60)
    
    # Initialize agent (connects to existing database)
    agent = OCRAgent(
        provider="ollama",
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
            
            # Display top results
            if found > 0:
                for j in range(min(2, found)):
                    top_doc = results["documents"][0][j]
                    top_metadata = results["metadatas"][0][j]
                    print(f"  Result {j+1}:")
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
        provider="ollama",
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


async def example_openai_usage():
    """Example: Process an image using OpenAI as the LLM and Vision provider."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Using OpenAI as LLM and Vision Provider")
    print("="*60)

    # Initialize OCR Agent with OpenAI for both LLM and Vision
    agent = OCRAgent(
        provider="openai",
        chroma_db_path="./ocr_database_openai",
        chroma_collection="openai_documents"
    )

    # Path to your image (update this!)
    image_path = "data/input/image.png"

    # Check if file exists
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        print("Please update the image_path in this script!")
        return

    # Process the image
    print(f"\n📸 Processing: {image_path}")
    result = await agent.process_image(
        image_path=image_path,
        use_vision=True,   # Use vision analysis
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
        print("\n📝 OCR Results:")
        print(f"  Confidence: {ocr['confidence']:.2f}%")
        print(f"  Word Count: {ocr['word_count']}")
        print(f"  Text Preview: {ocr['text'][:200]}..." if ocr['text'] else "  No text found")

        # Vision Analysis (from OpenAI)
        if result["vision_data"]:
            vision = result["vision_data"]
            print("\n👁️ OpenAI Vision Analysis:")
            print(f"  Description: {vision.get('overall_description', 'N/A')[:200]}...")
            if vision.get('objects'):
                obj_names = [obj.get('name', '') for obj in vision['objects'][:5]]
                print(f"  Objects: {', '.join(obj_names)}")
            if vision.get('colors', {}).get('dominant_colors'):
                print(f"  Colors: {', '.join(vision['colors']['dominant_colors'])}")
            if vision.get('people'):
                print(f"  People detected: {len(vision['people'])}")

        # Combined Analysis (from OpenAI LLM)
        if result["combined_analysis"] and result["combined_analysis"]["success"]:
            analysis = result["combined_analysis"]["analysis"]
            print("\n🤖 OpenAI LLM Analysis:")
            print(f"  Document Type: {analysis.get('document_type', 'N/A')}")
            print(f"  Tags: {', '.join(analysis.get('tags', []))}")
            print(f"  Summary: {analysis.get('comprehensive_summary', 'N/A')[:200]}...")
            print(f"  Confidence: {analysis.get('confidence', 0)}%")

            if analysis.get('key_information'):
                print("\n📊 Key Information:")
                for key, value in analysis['key_information'].items():
                    print(f"  {key}: {value}")
    else:
        print(f"\n❌ Processing failed: {result.get('error', 'Unknown error')}")


# --- Simple test for OpenAI and Ollama image analysis ---
async def test_simple_image_analysis():
    print("\n" + "="*60)
    print("TEST: Simple Image Analysis (OpenAI & Ollama)")
    print("="*60)
    image_path = "data/input/image.png"  # Update as needed
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return

    # OpenAI Vision
    agent_openai = OCRAgent(provider="openai")
    print(f"\n🔬 OpenAI Vision Analysis for '{image_path}':")
    openai_result = agent_openai._process_image(image_path)
    print(f"OpenAI Result:\n{openai_result}\n")

    # Ollama Vision
    agent_ollama = OCRAgent(provider="ollama")
    print(f"\n🔬 Ollama Vision Analysis for '{image_path}':")
    ollama_result = agent_ollama._process_image(image_path)
    print(f"Ollama Result:\n{ollama_result}\n")


async def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("OCR AGENT - SIMPLE IMAGE ANALYSIS")
    print("="*60)
    await test_simple_image_analysis()

if __name__ == "__main__":
    asyncio.run(main())
