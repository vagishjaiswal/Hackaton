# 🚀 Quick Start: 0 to Local LLM in 5 Minutes

## Step 1: Install Ollama (2 minutes)

### macOS
```bash
brew install ollama
```

### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Windows
Download installer from: https://ollama.ai/download

---

## Step 2: Pull a Model (2 minutes)

```bash
# Fast and good quality (recommended to start)
ollama pull llama2

# OR very fast for testing
ollama pull phi

# Verify it worked
ollama list
```

---

## Step 3: Test in Python (1 minute)

Create `test_local_llm.py`:

```python
import asyncio
from src.llm import create_llm_provider

async def main():
    # Create provider
    llm = create_llm_provider("ollama", "llama2")
    
    # Generate response
    response = await llm.generate("What is artificial intelligence?")
    
    print(f"AI: {response}")

# Run it
asyncio.run(main())
```

Run it:
```bash
python test_local_llm.py
```

**Expected output:**
```
AI: Artificial intelligence (AI) is the simulation of human intelligence 
in machines that are programmed to think and learn like humans...
```

---

## 🎉 You're Done!

You now have a local LLM running. No API key needed!

---

## What Next?

### Try Different Models
```bash
ollama pull mistral    # High quality
ollama pull codellama  # For coding
ollama pull phi        # Very fast
```

### Try Streaming
```python
from src.llm import create_llm_provider

llm = create_llm_provider("ollama", "llama2")

print("AI: ", end="", flush=True)
for chunk in llm.stream_generate("Tell me a short story"):
    print(chunk, end="", flush=True)
print()
```

### Use in Sync Code (Streamlit, etc.)
```python
from src.llm import create_llm_provider

llm = create_llm_provider("ollama", "llama2")

# Sync generation
response = llm.generate_sync("What is Python?")
print(response)
```

### Compare with OpenAI (Optional)
```python
# Set your API key first
export OPENAI_API_KEY=sk-...

# Then compare
from src.llm import create_llm_provider

ollama_llm = create_llm_provider("ollama", "llama2")
openai_llm = create_llm_provider("openai", "gpt-3.5-turbo")

prompt = "What is AI? Answer in one sentence."

ollama_resp = ollama_llm.generate_sync(prompt)
openai_resp = openai_llm.generate_sync(prompt)

print(f"Ollama: {ollama_resp}")
print(f"OpenAI: {openai_resp}")
```

---

## Troubleshooting

### "Cannot connect to Ollama"
```bash
# Start Ollama service
ollama serve
```

### "Model not found"
```bash
# Pull the model first
ollama pull llama2
```

### Slow generation
```bash
# Use faster model
ollama pull phi
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

### Pattern 2: With History
```python
from src.llm import create_llm_provider

llm = create_llm_provider("ollama", "llama2")

messages = [
    {"role": "system", "content": "You are a helpful assistant"}
]

while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        break
    
    messages.append({"role": "user", "content": user_input})
    
    import asyncio
    response = asyncio.run(llm.generate_with_messages(messages))
    print(f"AI: {response}\n")
```

### Pattern 3: Agent with LLM
```python
from src.llm import create_llm_provider

class MyAgent:
    def __init__(self):
        self.llm = create_llm_provider("ollama", "llama2")
    
    def process(self, task):
        return self.llm.generate_sync(
            f"Complete this task: {task}",
            system_prompt="You are a helpful assistant"
        )

agent = MyAgent()
result = agent.process("Write a haiku about AI")
print(result)
```

---

## 🎓 Learning Path

**Day 1:** Basic generation (you are here!)
**Day 2:** Try different models and temperatures
**Day 3:** Build a simple agent
**Day 4:** Create multi-agent workflow
**Day 5:** Add UI with Streamlit

---

## 📚 Resources

- **Ollama Docs**: https://ollama.ai
- **Model Library**: https://ollama.ai/library
- **This Project**: See `docs/` folder
- **Examples**: See `examples/` folder

---

## 🎉 Welcome to Local AI!

You're now running AI models on your own computer, for free!

**No API keys. No costs. No limits. Just AI.** 🚀
