# 🚀 Hackathon AI Agent System - Quick Reference

## Testing Commands

### Run All Tests
```bash
# Option 1: Bash script (Mac/Linux)
bash run_tests.sh

# Option 2: Python script (Cross-platform)
python run_tests.py

# Option 3: Specific tests
python run_tests.py --ollama    # Only Ollama tests
python run_tests.py --openai    # Only OpenAI tests
python run_tests.py --verbose   # Verbose output

# Option 4: Direct test execution
python tests/test_ollama_provider.py
python tests/test_openai_provider.py
```

---

## Setup Commands

### Initial Setup
```bash
# 1. Navigate to project
cd Code

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 4. Install dependencies
pip install -r requirements.txt

# 5. Setup environment
cp .env.example .env
# Edit .env with your API keys (optional for Ollama)
```

### Ollama Setup (Local LLMs)
```bash
# 1. Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh  # Mac/Linux
# Or download from: https://ollama.ai/download  # Windows

# 2. Pull a model
ollama pull llama2      # General purpose
ollama pull phi         # Fast, small model
ollama pull mistral     # High quality
ollama pull codellama   # For coding

# 3. Verify
ollama list

# 4. Test
python tests/test_ollama_provider.py
```

---

## LLM Provider Usage

### Quick Start (Ollama - Local)
```python
from src.llm import create_llm_provider

# Create provider
llm = create_llm_provider("ollama", "llama2")

# Generate (async)
response = await llm.generate("What is AI?")

# Generate (sync)
response = llm.generate_sync("What is AI?")

# Stream
for chunk in llm.stream_generate("Tell me a story"):
    print(chunk, end="", flush=True)
```

### OpenAI (Cloud)
```python
from src.llm import create_llm_provider

# Requires OPENAI_API_KEY in .env
llm = create_llm_provider("openai", "gpt-4")

response = await llm.generate("What is AI?")
```

### Factory Pattern (Recommended)
```python
from src.llm import LLMProviderFactory

# From config dict
config = {
    "llm_provider": "ollama",
    "model": "llama2",
    "temperature": 0.7
}
provider = LLMProviderFactory.create_from_config(config)

# From JSON file
provider = LLMProviderFactory.create_from_json_config(
    "config/agents_config.json",
    "agent_1"
)
```

---

## Configuration

### .env File
```bash
# OpenAI (optional)
OPENAI_API_KEY=sk-...

# Ollama (optional, defaults shown)
OLLAMA_BASE_URL=http://localhost:11434

# Default provider
DEFAULT_LLM_PROVIDER=ollama
LOG_LEVEL=INFO
```

### agents_config.json
```json
{
  "agents": [
    {
      "id": "local_agent",
      "llm_provider": "ollama",
      "model": "llama2",
      "temperature": 0.7,
      "max_tokens": 1000
    },
    {
      "id": "cloud_agent",
      "llm_provider": "openai",
      "model": "gpt-4",
      "temperature": 0.7
    }
  ]
}
```

---

## Common Patterns

### Pattern 1: Simple Chat
```python
from src.llm import create_llm_provider

llm = create_llm_provider("ollama", "llama2")

while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        break
    
    response = llm.generate_sync(user_input)
    print(f"AI: {response}\n")
```

### Pattern 2: Agent with LLM
```python
from src.llm import create_llm_provider

class MyAgent:
    def __init__(self, provider="ollama", model="llama2"):
        self.llm = create_llm_provider(provider, model)
    
    async def process(self, task):
        return await self.llm.generate(
            prompt=task,
            system_prompt="You are a helpful assistant"
        )
```

### Pattern 3: Multi-Provider
```python
from src.llm import create_llm_provider

class SmartAgent:
    def __init__(self):
        self.fast_llm = create_llm_provider("ollama", "phi")
        self.quality_llm = create_llm_provider("ollama", "llama2:13b")
    
    async def process(self, task, quality="normal"):
        if quality == "high":
            return await self.quality_llm.generate(task)
        return await self.fast_llm.generate(task)
```

---

## Model Selection Guide

### Speed Priority
```python
# Very Fast (~80 tokens/sec)
llm = create_llm_provider("ollama", "phi")

# Fast (~40 tokens/sec)
llm = create_llm_provider("ollama", "llama2")

# Balanced
llm = create_llm_provider("openai", "gpt-3.5-turbo")
```

### Quality Priority
```python
# Good Quality (local)
llm = create_llm_provider("ollama", "llama2:13b")

# High Quality (local)
llm = create_llm_provider("ollama", "mixtral")

# Best Quality (cloud)
llm = create_llm_provider("openai", "gpt-4")
```

### Cost Priority
```python
# Free (local)
llm = create_llm_provider("ollama", "llama2")

# Cheap (cloud)
llm = create_llm_provider("openai", "gpt-3.5-turbo")
```

### Specialized Models
```python
# Code generation
llm = create_llm_provider("ollama", "codellama")

# Conversation
llm = create_llm_provider("ollama", "neural-chat")

# General purpose
llm = create_llm_provider("ollama", "mistral")
```

---

## Troubleshooting

### "Cannot connect to Ollama"
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Or restart Ollama service
```

### "Model not found"
```bash
# Pull the model
ollama pull llama2

# List available models
ollama list
```

### "OPENAI_API_KEY not found"
```bash
# Add to .env file
echo "OPENAI_API_KEY=sk-..." >> .env

# Or export temporarily
export OPENAI_API_KEY=sk-...
```

### "Module not found"
```bash
# Install dependencies
pip install -r requirements.txt

# Or install specific package
pip install langchain langchain-community langchain-openai
```

---

## File Structure

```
Code/
├── src/
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── base_llm_provider.py          # Base class
│   │   ├── openai_provider.py            # OpenAI
│   │   ├── ollama_provider.py            # Ollama
│   │   └── llm_provider_factory.py       # Factory
│   ├── utils/
│   │   └── config_loader.py              # Config loading
│   └── tools/
│       └── csv_tools.py                  # CSV tools (next)
├── tests/
│   ├── test_ollama_provider.py           # Ollama tests
│   └── test_openai_provider.py           # OpenAI tests
├── config/
│   ├── agents_config.json                # Agent configs
│   └── workflow_config.json              # Workflow configs
├── requirements.txt
├── .env.example
├── run_tests.py                          # Test runner
└── run_tests.sh                          # Test runner (bash)
```

---

## Progress Status

**Phase 1:** 80% Complete (4/5 tasks)
- ✅ Project Structure
- ✅ Environment Config
- ✅ OpenAI Provider
- ✅ Ollama + Factory
- ⏳ CSV Tools (next)

**Overall:** 52% Complete (11/21 tasks)

---

## Next Steps

1. **Test the implementations**
   ```bash
   python run_tests.py
   ```

2. **Implement CSV Tools** (Phase 1.5)
   - CSV loader with validation
   - Data access for agents

3. **Start Agent System** (Phase 2)
   - Base agent class
   - Agent factory
   - Specific agent types

4. **Build Workflows** (Phase 3)
   - LangGraph integration
   - State management

5. **Create UI** (Phase 4)
   - Streamlit interface
   - Workflow visualization

---

## Useful Links

- **Ollama**: https://ollama.ai
- **OpenAI**: https://platform.openai.com
- **LangChain**: https://python.langchain.com
- **This Project**: See `docs/` folder

---

## Quick Commands Cheat Sheet

```bash
# Setup
pip install -r requirements.txt
cp .env.example .env

# Ollama
ollama pull llama2
ollama list
ollama serve

# Testing
python run_tests.py
python run_tests.py --ollama
python run_tests.py --verbose

# Development
python -m pytest tests/ -v
black src/
ruff check src/
```

---

**🎉 You're ready to build AI agents!**