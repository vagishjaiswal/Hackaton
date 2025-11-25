# Ollama Provider - Local LLM Setup Guide

## 🎯 Overview

Ollama lets you run powerful open-source LLMs locally on your machine, completely free and private. Perfect for:
- **Development & Testing** - No API costs
- **Privacy** - Data never leaves your machine
- **Offline Work** - No internet required
- **Experimentation** - Try different models easily

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Ollama

**macOS / Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from https://ollama.ai/download

**Verify Installation:**
```bash
ollama --version
```

### Step 2: Pull a Model

```bash
# Recommended for beginners (fast, good quality)
ollama pull llama2

# Or try other models
ollama pull mistral        # Fast 7B model
ollama pull codellama      # Specialized for coding
ollama pull phi            # Very fast 2.7B model
```

### Step 3: Test with Python

```python
from src.llm import create_llm_provider

# Create provider
provider = create_llm_provider("ollama", "llama2")

# Generate response
response = await provider.generate("What is AI?")
print(response)
```

That's it! You're running LLMs locally. 🎉

---

## 📦 Available Models

### Recommended Models

| Model | Size | Speed | Use Case |
|-------|------|-------|----------|
| **phi** | 2.7B | ⚡⚡⚡ Very Fast | Quick responses, testing |
| **llama2** | 7B | ⚡⚡ Fast | General purpose, balanced |
| **mistral** | 7B | ⚡⚡ Fast | Great quality, efficient |
| **codellama** | 7B/13B | ⚡⚡ Fast | Code generation |
| **neural-chat** | 7B | ⚡⚡ Fast | Conversational AI |
| **llama2** | 13B | ⚡ Moderate | Higher quality |
| **mixtral** | 8x7B | ⚡ Moderate | Best quality |

### Pull Models

```bash
# List available models
ollama list

# Pull a specific model
ollama pull llama2

# Pull specific version
ollama pull llama2:13b

# Remove a model
ollama rm llama2
```

---

## 💻 Usage Examples

### Basic Generation

```python
from src.llm import OllamaProvider, LLMConfig

# Create configuration
config = LLMConfig(
    model="llama2",
    temperature=0.7,
    max_tokens=500
)

# Initialize provider
provider = OllamaProvider(config)

# Generate
response = await provider.generate(
    prompt="Explain quantum computing",
    system_prompt="You are a physics professor"
)
```

### Using the Factory (Recommended)

```python
from src.llm import LLMProviderFactory

# Quick creation
provider = LLMProviderFactory.create_provider(
    provider_type="ollama",
    model="llama2",
    temperature=0.7
)

# From config dict
config = {
    "llm_provider": "ollama",
    "model": "mistral",
    "temperature": 0.5
}
provider = LLMProviderFactory.create_from_config(config)

# From agents_config.json
provider = LLMProviderFactory.create_from_json_config(
    config_path="config/agents_config.json",
    agent_id="agent_1"
)
```

### Streaming Responses

```python
# Great for UI/real-time output
for chunk in provider.stream_generate("Tell me a story"):
    print(chunk, end="", flush=True)
```

### Conversation History

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "What is Python?"},
]

response = await provider.generate_with_messages(messages)
```

### Model Management

```python
# List available models
models = provider.list_available_models()
print(f"Available: {models}")

# Validate model
is_valid = provider.validate_model()

# Get model info
info = provider.get_model_info()

# Estimate speed
speed = provider.estimate_speed()
print(f"Speed: {speed}")

# Pull new model
success = provider.pull_model("mistral")
```

---

## 🔧 Configuration

### Basic Configuration

```python
config = LLMConfig(
    model="llama2",
    temperature=0.7,       # Creativity (0.0-2.0)
    max_tokens=1000,       # Response length
    top_p=0.9,            # Nucleus sampling
    timeout=60            # Request timeout
)
```

### Temperature Guide

```python
# Deterministic (consistent, factual)
config = LLMConfig(model="llama2", temperature=0.1)

# Balanced (general purpose)
config = LLMConfig(model="llama2", temperature=0.7)

# Creative (varied, explorative)
config = LLMConfig(model="llama2", temperature=0.9)
```

### Custom Base URL

```python
# If Ollama is on different host/port
provider = OllamaProvider(
    config,
    base_url="http://192.168.1.100:11434"
)
```

---

## 🎨 Integration with Agents

### Example: Data Analyst Agent

```python
from src.llm import create_llm_provider

class DataAnalystAgent:
    def __init__(self):
        self.llm = create_llm_provider(
            provider_type="ollama",
            model="llama2",
            temperature=0.3  # Low for consistent analysis
        )
    
    async def analyze(self, data: str):
        return await self.llm.generate(
            prompt=f"Analyze this data: {data}",
            system_prompt="You are a data analyst. Be concise."
        )
```

### Example: Code Generator Agent

```python
class CodeGeneratorAgent:
    def __init__(self):
        self.llm = create_llm_provider(
            provider_type="ollama",
            model="codellama",  # Specialized for code
            temperature=0.2
        )
    
    async def generate_code(self, description: str):
        return await self.llm.generate(
            prompt=f"Write Python code: {description}",
            system_prompt="You are an expert Python developer."
        )
```

### Example: Multi-Agent System

```python
# agents_config.json
{
  "agents": [
    {
      "id": "analyst",
      "llm_provider": "ollama",
      "model": "llama2",
      "temperature": 0.3
    },
    {
      "id": "writer",
      "llm_provider": "ollama",
      "model": "mistral",
      "temperature": 0.8
    }
  ]
}

# Load agents
from src.llm import LLMProviderFactory

analyst = LLMProviderFactory.create_from_json_config(
    "config/agents_config.json", "analyst"
)
writer = LLMProviderFactory.create_from_json_config(
    "config/agents_config.json", "writer"
)
```

---

## 🚀 Performance Tips

### 1. Choose the Right Model Size

```python
# Fast iteration (development)
provider = create_llm_provider("ollama", "phi")  # 2.7B - very fast

# Balanced (production)
provider = create_llm_provider("ollama", "llama2")  # 7B - good speed

# High quality (when speed is less critical)
provider = create_llm_provider("ollama", "llama2:13b")  # 13B - slower
```

### 2. Optimize Temperature

```python
# For consistent, factual responses
config = LLMConfig(model="llama2", temperature=0.1)

# For creative writing
config = LLMConfig(model="llama2", temperature=0.9)
```

### 3. Use Streaming for Better UX

```python
# User sees progress immediately
print("AI: ", end="", flush=True)
for chunk in provider.stream_generate(prompt):
    print(chunk, end="", flush=True)
print()
```

### 4. Set Appropriate Token Limits

```python
# Short answers (faster)
config = LLMConfig(model="llama2", max_tokens=100)

# Detailed responses
config = LLMConfig(model="llama2", max_tokens=2000)
```

### 5. Batch Processing

```python
# Process multiple prompts
prompts = ["Question 1", "Question 2", "Question 3"]

responses = []
for prompt in prompts:
    response = await provider.generate(prompt)
    responses.append(response)
```

---

## 🔍 Troubleshooting

### Error: "Cannot connect to Ollama"

**Solution 1: Check if Ollama is running**
```bash
# Start Ollama service
ollama serve

# In another terminal
ollama list
```

**Solution 2: Check port**
```python
# Try different port
provider = OllamaProvider(config, base_url="http://localhost:11434")
```

### Error: "Model not found"

**Solution: Pull the model**
```bash
ollama pull llama2
```

### Slow Generation

**Solution 1: Use smaller model**
```bash
ollama pull phi  # 2.7B - much faster
```

**Solution 2: Reduce max_tokens**
```python
config = LLMConfig(model="llama2", max_tokens=200)
```

**Solution 3: Check system resources**
```bash
# Monitor GPU/CPU usage
top  # or htop on Linux

# Check Ollama logs
ollama logs
```

### Memory Issues

**Solution: Use smaller model or quantized version**
```bash
# Smaller models use less RAM
ollama pull phi           # ~2GB RAM
ollama pull llama2        # ~4GB RAM
ollama pull llama2:13b    # ~8GB RAM
```

---

## 🆚 Ollama vs OpenAI

| Feature | Ollama | OpenAI |
|---------|--------|--------|
| **Cost** | Free | Pay per token |
| **Privacy** | 100% local | Data sent to API |
| **Speed** | Hardware dependent | Very fast |
| **Quality** | Good | Excellent |
| **Offline** | Yes | No |
| **Setup** | Install once | API key needed |
| **Best For** | Development, privacy | Production, scale |

### When to Use Each

**Use Ollama for:**
- Development and testing
- Privacy-sensitive applications
- Offline environments
- Cost-sensitive projects
- Learning and experimentation

**Use OpenAI for:**
- Production applications
- Highest quality responses
- Consistent performance
- Advanced features (GPT-4)
- Global scale

### Hybrid Approach (Recommended)

```python
import os

# Use Ollama for development
if os.getenv("ENVIRONMENT") == "development":
    provider = create_llm_provider("ollama", "llama2")
# Use OpenAI for production
else:
    provider = create_llm_provider("openai", "gpt-4")
```

---

## 📊 Benchmarks

### Generation Speed (tokens/sec)

On M1 MacBook Pro:
- **phi (2.7B)**: ~80 tokens/sec
- **llama2 (7B)**: ~40 tokens/sec
- **mistral (7B)**: ~35 tokens/sec
- **llama2 (13B)**: ~20 tokens/sec

On RTX 3080 (Linux):
- **phi (2.7B)**: ~120 tokens/sec
- **llama2 (7B)**: ~60 tokens/sec
- **llama2 (13B)**: ~30 tokens/sec

### Quality Comparison

For coding tasks:
1. **codellama** - Best for code
2. **mistral** - Good general coding
3. **llama2** - Decent

For creative writing:
1. **mistral** - Most creative
2. **llama2:13b** - Good quality
3. **llama2** - Good balance

For factual Q&A:
1. **llama2:13b** - Most accurate
2. **mistral** - Good accuracy
3. **llama2** - Good balance

---

## 🎓 Learning Resources

### Official Documentation
- Ollama Website: https://ollama.ai
- Model Library: https://ollama.ai/library
- GitHub: https://github.com/ollama/ollama

### Recommended Models to Try
1. **llama2** - Start here
2. **mistral** - Try next
3. **codellama** - For coding
4. **phi** - For speed tests

### Example Projects
See `examples/` directory for:
- Simple chatbot
- Code generator
- Data analyzer
- Multi-agent workflow

---

## 🎉 Next Steps

Now that you have Ollama working:

1. ✅ **Test with different models** - Find your favorite
2. ✅ **Integrate with agents** (Phase 2) - Build AI agents
3. ✅ **Create workflows** (Phase 3) - Chain multiple agents
4. ✅ **Add to UI** (Phase 4) - Build user interface

**Ready to build amazing AI applications!** 🚀
