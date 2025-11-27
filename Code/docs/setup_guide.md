# Quick Setup & Testing Guide - OpenAI Provider

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Dependencies
```bash
cd Code
pip install langchain langchain-openai tenacity pydantic python-dotenv
```

### Step 2: Set Up Environment Variables
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API key
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
```

### Step 3: Test the Implementation
```bash
# Run the test suite
python tests/test_openai_provider.py
```

Expected output:
```
============================================================
OPENAI PROVIDER TEST SUITE
============================================================
$env:OPENAI_API_KEY = "";
sk-proj--
Temp: AfbVfuYLOBUWEcjhtJGZP8vdhHh0edYf2m18JfNtz_8bYkJARxVsm9JGKmonoAJFkSKAwHIVqT3BlbkFJeLShc2HoeBdHbGhvhSObOzcbGwYM8LmW38QlPWRrcX6FB_9Q_CzC3f_USBiak2U_BVp0EqiCMA
============================================================
TEST 1: Basic Text Generation
============================================================
Provider: OpenAIProvider(provider=openai, model=gpt-3.5-turbo, temperature=0.7)

Generating response...

Response: Artificial intelligence is the simulation of human intelligence...

✅ Test passed!

... [more tests]

============================================================
✅ ALL TESTS PASSED!
============================================================
```

---

## 📝 Manual Testing

### Test 1: Simple Generation
```python
import asyncio
import os
from src.llm import OpenAIProvider, LLMConfig

async def test():
    config = LLMConfig(model="gpt-3.5-turbo", temperature=0.7)
    provider = OpenAIProvider(config, os.getenv("OPENAI_API_KEY"))
    
    response = await provider.generate("What is AI?")
    print(response)

asyncio.run(test())
```

### Test 2: Sync Generation (for Streamlit)
```python
import os
from src.llm import OpenAIProvider, LLMConfig

config = LLMConfig(model="gpt-3.5-turbo", temperature=0.7)
provider = OpenAIProvider(config, os.getenv("OPENAI_API_KEY"))

response = provider.generate_sync("What is machine learning?")
print(response)
```

### Test 3: Streaming
```python
import os
from src.llm import OpenAIProvider, LLMConfig

config = LLMConfig(model="gpt-3.5-turbo", temperature=0.8)
provider = OpenAIProvider(config, os.getenv("OPENAI_API_KEY"))

print("AI: ", end="", flush=True)
for chunk in provider.stream_generate("Tell me a short story"):
    print(chunk, end="", flush=True)
print()
```

---

## 🔧 Troubleshooting

### Error: "No module named 'src'"
**Solution:**
```bash
# Make sure you're in the Code directory
cd Code

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Error: "OPENAI_API_KEY not found"
**Solution:**
```bash
# Check if .env exists
ls -la .env

# Verify contents
cat .env | grep OPENAI_API_KEY

# Load manually for testing
export OPENAI_API_KEY="sk-..."
```

### Error: "Rate limit exceeded"
**Solution:** The provider will automatically retry. If persistent:
```python
# Increase retry delay
config = LLMConfig(
    model="gpt-3.5-turbo",
    max_retries=5  # Increase retries
)
```

### Error: "Timeout"
**Solution:**
```python
config = LLMConfig(
    model="gpt-4",
    timeout=120  # Increase timeout to 2 minutes
)
```

---

## 📊 Verify Installation

Run this quick verification script:

```python
# verify_setup.py
import sys

def check_imports():
    """Check if all required packages are installed."""
    packages = {
        "langchain": "langchain",
        "langchain_openai": "langchain-openai",
        "tenacity": "tenacity",
        "pydantic": "pydantic",
        "dotenv": "python-dotenv"
    }
    
    print("Checking package installations...\n")
    all_ok = True
    
    for module, package in packages.items():
        try:
            __import__(module)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Run: pip install {package}")
            all_ok = False
    
    return all_ok

def check_env():
    """Check if .env file exists and has API key."""
    import os
    from pathlib import Path
    
    print("\nChecking environment setup...\n")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("   Run: cp .env.example .env")
        return False
    
    print("✅ .env file exists")
    
    # Try to load
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not set in .env")
        return False
    
    if api_key.startswith("your_"):
        print("❌ OPENAI_API_KEY still has placeholder value")
        print("   Edit .env and add your real API key")
        return False
    
    print("✅ OPENAI_API_KEY is set")
    return True

def check_structure():
    """Check if project structure is correct."""
    from pathlib import Path
    
    print("\nChecking project structure...\n")
    
    required_files = [
        "src/llm/__init__.py",
        "src/llm/base_llm_provider.py",
        "src/llm/openai_provider.py",
        "src/utils/config_loader.py",
    ]
    
    all_ok = True
    for file in required_files:
        path = Path(file)
        if path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - Missing!")
            all_ok = False
    
    return all_ok

if __name__ == "__main__":
    print("=" * 60)
    print("SETUP VERIFICATION")
    print("=" * 60 + "\n")
    
    checks = [
        ("Packages", check_imports()),
        ("Environment", check_env()),
        ("Structure", check_structure())
    ]
    
    print("\n" + "=" * 60)
    if all(result for _, result in checks):
        print("✅ ALL CHECKS PASSED - Ready to test!")
    else:
        print("❌ SOME CHECKS FAILED - Fix the issues above")
    print("=" * 60 + "\n")
```

Run it:
```bash
python verify_setup.py
```

---

## 🎯 Next Steps After Testing

Once all tests pass:

1. **Implement Gemini Provider** (Phase 1.4)
   - Copy OpenAI provider structure
   - Replace with Gemini API calls
   - Test with Google API key

2. **Create Provider Factory** (Phase 1.4)
   - Factory to create providers from config
   - Automatic provider selection

3. **Build CSV Tools** (Phase 1.5)
   - CSV loader with validation
   - Data access for agents

4. **Start Agent System** (Phase 2)
   - Base agent class
   - Agent factory
   - Tool integration

---

## 💡 Usage Examples

### Example 1: Data Analysis Agent
```python
config = LLMConfig(
    model="gpt-4",
    temperature=0.3,  # Low for consistent analysis
    max_tokens=1000
)
provider = OpenAIProvider(config, api_key)

response = await provider.generate(
    prompt=f"Analyze this data: {csv_data}",
    system_prompt="You are a data analyst. Provide insights."
)
```

### Example 2: Creative Writing Agent
```python
config = LLMConfig(
    model="gpt-4",
    temperature=0.9,  # High for creativity
    max_tokens=2000
)
provider = OpenAIProvider(config, api_key)

response = await provider.generate(
    prompt="Write a short sci-fi story",
    system_prompt="You are a creative writer."
)
```

### Example 3: Research Agent
```python
config = LLMConfig(
    model="gpt-3.5-turbo",  # Cost-effective
    temperature=0.5,
    max_tokens=500
)
provider = OpenAIProvider(config, api_key)

response = await provider.generate(
    prompt="Research topic: Quantum computing",
    system_prompt="You are a research assistant."
)
```

---

## 📈 Performance Tips

1. **Use gpt-3.5-turbo for speed**: 10x faster than GPT-4
2. **Stream for better UX**: Users see progress immediately
3. **Lower temperature for consistency**: 0.1-0.3 for factual tasks
4. **Higher temperature for creativity**: 0.7-1.0 for creative tasks
5. **Set max_tokens**: Prevent unexpectedly long/expensive responses

---

**Ready to build agents!** 🎉
