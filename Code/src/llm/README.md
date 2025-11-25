# LLM Provider System Documentation

## Overview

The LLM Provider system provides a unified interface for interacting with different language model providers (OpenAI, Google Gemini, etc.). It handles configuration, error handling, retries, and both synchronous and asynchronous operations.

## Architecture

```
src/llm/
├── base_llm_provider.py    # Abstract base class
├── openai_provider.py      # OpenAI implementation
├── gemini_provider.py      # Gemini implementation (coming soon)
└── __init__.py            # Module exports
```

## Quick Start

### 1. Basic Usage

```python
from src.llm import OpenAIProvider, LLMConfig

# Create configuration
config = LLMConfig(
    model="gpt-4",
    temperature=0.7,
    max_tokens=1000
)

# Initialize provider
provider = OpenAIProvider(config, api_key="sk-...")

# Generate response (async)
response = await provider.generate(
    prompt="What is artificial intelligence?",
    system_prompt="You are a helpful assistant."
)

# Generate response (sync)
response = provider.generate_sync("What is AI?")
```

### 2. Conversation with Message History

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "What is Python?"},
    {"role": "assistant", "content": "Python is a programming language"},
    {"role": "user", "content": "Tell me more"}
]

response = await provider.generate_with_messages(messages)
```

### 3. Streaming Responses

```python
for chunk in provider.stream_generate("Tell me a story"):
    print(chunk, end="", flush=True)
```

## Configuration

### LLMConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | str | Required | Model identifier (e.g., "gpt-4") |
| `temperature` | float | 0.7 | Sampling temperature (0.0-2.0) |
| `max_tokens` | int | None | Maximum tokens in response |
| `top_p` | float | None | Nucleus sampling (0.0-1.0) |
| `frequency_penalty` | float | None | Frequency penalty (-2.0 to 2.0) |
| `presence_penalty` | float | None | Presence penalty (-2.0 to 2.0) |
| `timeout` | int | 60 | Request timeout in seconds |
| `max_retries` | int | 3 | Maximum retry attempts |

### Example Configurations

**Conservative (Deterministic)**
```python
config = LLMConfig(
    model="gpt-4",
    temperature=0.1,
    max_tokens=500
)
```

**Creative (Exploratory)**
```python
config = LLMConfig(
    model="gpt-4",
    temperature=0.9,
    top_p=0.95,
    max_tokens=2000
)
```

**Balanced (General Purpose)**
```python
config = LLMConfig(
    model="gpt-3.5-turbo",
    temperature=0.7,
    max_tokens=1000
)
```

## Error Handling & Retries

The provider includes automatic retry logic with exponential backoff:

- **Rate Limits (429)**: Automatically retries with increasing delays
- **Transient Errors**: Network issues, timeouts
- **Maximum Attempts**: 3 retries by default (configurable)

```python
# Retry behavior:
# Attempt 1: Immediate
# Attempt 2: Wait 2 seconds
# Attempt 3: Wait 4 seconds
# Attempt 4: Wait 8 seconds (max 10 seconds)
```

## OpenAI Provider

### Supported Models

- `gpt-4` - Most capable model
- `gpt-4-turbo` - Faster GPT-4 variant
- `gpt-3.5-turbo` - Fast and cost-effective
- `gpt-3.5-turbo-16k` - Extended context window

### Methods

#### `generate(prompt, system_prompt=None, **kwargs)`
Async generation with optional system prompt.

#### `generate_with_messages(messages, **kwargs)`
Async generation from conversation history.

#### `generate_sync(prompt, system_prompt=None, **kwargs)`
Synchronous version for non-async contexts.

#### `stream_generate(prompt, system_prompt=None, **kwargs)`
Stream tokens as they're generated.

#### `get_token_count(text)`
Estimate token count for a text string.

#### `validate_model()`
Check if configured model is supported.

## Integration with Agents

The LLM providers are designed to work seamlessly with the agent system:

```python
from src.llm import OpenAIProvider, LLMConfig
from src.agents import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self, config: dict):
        # Create LLM provider from config
        llm_config = LLMConfig(
            model=config["model"],
            temperature=config["temperature"]
        )
        self.llm = OpenAIProvider(
            llm_config, 
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    async def execute(self, task: str) -> str:
        return await self.llm.generate(
            prompt=task,
            system_prompt=self.system_prompt
        )
```

## Loading from JSON Config

```python
from src.utils.config_loader import ConfigLoader
from src.llm import OpenAIProvider, LLMConfig

# Load agent config
config_loader = ConfigLoader()
agents_config = config_loader.load_config("config/agents_config.json")

# Get agent config
agent_conf = agents_config["agents"][0]

# Create LLM provider
llm_config = LLMConfig(
    model=agent_conf["model"],
    temperature=agent_conf["temperature"]
)

provider_type = agent_conf["llm_provider"]
api_key = config_loader.get_env_variable(f"{provider_type.upper()}_API_KEY")

if provider_type == "openai":
    provider = OpenAIProvider(llm_config, api_key)
```

## Testing

Run the test suite:

```bash
cd Code
python -m pytest tests/test_openai_provider.py -v

# Or run manual test
python tests/test_openai_provider.py
```

### Test Coverage

- ✅ Basic text generation
- ✅ Conversation with messages
- ✅ Synchronous generation
- ✅ Streaming generation
- ✅ Configuration updates
- ✅ Error handling
- ✅ Retry logic

## Best Practices

### 1. Use Async When Possible
```python
# Good - Non-blocking
response = await provider.generate(prompt)

# Okay - Blocking (use in Streamlit, sync contexts)
response = provider.generate_sync(prompt)
```

### 2. Set Appropriate Timeouts
```python
# For long-running tasks
config = LLMConfig(model="gpt-4", timeout=120)

# For quick responses
config = LLMConfig(model="gpt-3.5-turbo", timeout=30)
```

### 3. Handle Token Limits
```python
# Estimate tokens before sending
token_count = provider.get_token_count(long_text)
if token_count > 4000:
    # Truncate or split text
    text = long_text[:16000]  # ~4000 tokens
```

### 4. Use System Prompts
```python
# Define behavior clearly
response = await provider.generate(
    prompt="Analyze this data: ...",
    system_prompt="You are a data analyst. Provide concise, actionable insights."
)
```

### 5. Stream for Better UX
```python
# In UI applications
print("AI: ", end="", flush=True)
for chunk in provider.stream_generate(prompt):
    print(chunk, end="", flush=True)
print()  # Newline at end
```

## Troubleshooting

### Issue: "API key cannot be empty"
**Solution**: Ensure your `.env` file has `OPENAI_API_KEY=sk-...`

### Issue: Rate limit errors
**Solution**: The provider automatically retries. If persistent, reduce request frequency.

### Issue: Timeout errors
**Solution**: Increase timeout in config: `LLMConfig(timeout=120)`

### Issue: Model not found
**Solution**: Check model name spelling and your API access level.

## Next Steps

1. Implement Gemini provider (Phase 1.4)
2. Add provider factory pattern for easy switching
3. Integrate with agent system (Phase 2)
4. Add token counting utilities
5. Implement cost tracking

## Contributing

When adding a new provider:

1. Inherit from `BaseLLMProvider`
2. Implement all abstract methods
3. Add retry logic with `tenacity`
4. Add comprehensive docstrings
5. Create test cases
6. Update this documentation
