# Chat-Based Workflow with Sequence Evaluator

## 🎯 Overview

An intelligent, interactive workflow system that:
1. Takes user tasks in natural language
2. Uses LLM to analyze and generate optimal execution sequences
3. Identifies missing information and asks clarifying questions
4. Executes multi-step workflows automatically
5. Returns aggregated results to the user

## 🏗️ Architecture

```
User Task
    ↓
Sequence Evaluator Agent (LLM)
    ├→ Analyzes task
    ├→ Discovers available agents/tools
    ├→ Generates execution sequence
    └→ Identifies clarifications needed
    ↓
Chat-Based Workflow
    ├→ Asks clarifying questions (if needed)
    ├→ Waits for user answers
    ├→ Re-evaluates with new information
    └→ Executes sequence step-by-step
    ↓
Results
```

## 📁 Files Created OK

```
Code/src/agents/
├── sequence_evaluator_agent.py    # LLM-based sequence planner

Code/src/workflow/
├── chat_based_workflow.py         # Interactive workflow engine

Code/tests/workflow/
└── example_chat_workflow.py       # Examples and demos
```

## 🚀 Quick Start

### 1. Basic Usage

```python
from src.workflow.chat_based_workflow import ChatBasedWorkflow

# Create workflow
workflow = ChatBasedWorkflow(
    llm_provider="ollama",
    llm_model="llama3.2"
)

# User provides task
response = await workflow.process_message(
    "Analyze the sales data from Q4 2024"
)

print(response)
```

### 2. Handling Clarifications

```python
# If workflow needs clarification
if workflow.needs_clarification():
    clarifications = workflow.get_clarifications()
    
    # Show questions to user
    for c in clarifications:
        print(f"Q: {c['question']}")
    
    # User answers
    answers = {
        "csv_file": "sales_q4.csv",
        "analysis_type": "summary"
    }
    
    # Provide answers
    response = await workflow.process_message(json.dumps(answers))
```

### 3. Check Workflow State

```python
state = workflow.get_state()

print(f"Status: {state['status']}")
print(f"Current Step: {state['current_step']}/{state['total_steps']}")
print(f"Needs Clarification: {state['needs_clarification']}")
```

## 📊 Features

### 1. Sequence Evaluator Agent

**Capabilities**:
- Analyzes user tasks
- Discovers available agents and tools
- Generates optimal execution sequences
- Identifies missing information
- Provides reasoning for decisions

**Example**:
```python
from src.agents.sequence_evaluator_agent import SequenceEvaluatorAgent

evaluator = SequenceEvaluatorAgent()

# Register available resources
evaluator.register_available_agent(
    "DataAnalyst",
    "Analyzes CSV data and provides insights"
)
evaluator.register_available_tool(
    "CSVLoader",
    "Loads and validates CSV files"
)

# Evaluate a task
result = await evaluator.evaluate_sequence(
    task="Analyze customer data and find trends",
    context={"has_csv": True}
)

# result contains:
# - sequence: List of steps
# - clarifications: Questions for user
# - reasoning: Why this sequence
# - can_execute: True/False
```

### 2. Chat-Based Workflow

**Capabilities**:
- Interactive conversation
- Dynamic sequence generation
- Clarification handling
- Step-by-step execution
- Result aggregation
- Error recovery

**Example**:
```python
workflow = ChatBasedWorkflow()

# Process messages
response = await workflow.process_message("Help me analyze data")

# Workflow asks questions
# User answers
response = await workflow.process_message("The file is sales.csv")

# Workflow executes and returns results
```

### 3. Agent & Tool Registry

**Built-in Agents**:
- `DataAnalyst`: CSV data analysis
- `Researcher`: Information gathering
- `SimpleExecutor`: General task execution

**Built-in Tools**:
- `CSVLoader`: CSV file operations

**Register Custom Agents**:
```python
workflow.register_agent(
    name="CustomAgent",
    description="Does custom tasks",
    agent_class=MyCustomAgent
)
```

**Register Custom Tools**:
```python
workflow.register_tool(
    name="CustomTool",
    description="Custom functionality",
    tool_function=my_tool_function
)
```

## 🎓 How It Works

### Step 1: Task Analysis

User: "Analyze sales data from Q4"

Sequence Evaluator:
1. Identifies this requires CSV analysis
2. Checks available agents/tools
3. Generates sequence:
   - Load CSV with CSVLoader
   - Analyze with DataAnalyst
   - Format results

### Step 2: Clarification

Evaluator identifies missing info:
- Which CSV file?
- What kind of analysis?

Workflow asks user:
```
I need some clarification:
1. Which CSV file should I analyze?
2. What type of analysis? (summary/detailed/trends)
```

### Step 3: Execution

Once clarified:
```
Execution Plan:
1. Load CSV file
   Using: CSVLoader
   Action: Load sales_q4.csv

2. Analyze data
   Using: DataAnalyst
   Action: Generate summary statistics

3. Format results
   Using: SimpleExecutor
   Action: Create readable report
```

### Step 4: Results

```
✓ Execution completed!

Completed 3 steps:
✓ Step 1: Load CSV file
✓ Step 2: Analyze data
✓ Step 3: Format results

--- Final Result ---
[Analysis results here]
```

## 🔧 Configuration

### LLM Provider

```python
# Use Ollama (local)
workflow = ChatBasedWorkflow(
    llm_provider="ollama",
    llm_model="llama3.2"
)

# Use OpenAI (cloud)
workflow = ChatBasedWorkflow(
    llm_provider="openai",
    llm_model="gpt-4"
)
```

### Data Directory

```python
workflow = ChatBasedWorkflow(
    data_dir="path/to/data"
)
```

### Verbose Logging

```python
workflow = ChatBasedWorkflow(
    verbose=True  # Enable detailed logs
)
```

## 📝 Examples

### Example 1: Simple Question

```python
workflow = ChatBasedWorkflow()

response = await workflow.process_message(
    "What is the capital of France?"
)
# Response: "Paris"
```

### Example 2: Data Analysis

```python
workflow = ChatBasedWorkflow()

# User task
response = await workflow.process_message(
    "Load sample-csv.csv and count the rows"
)

# Workflow may ask: "Which directory is the file in?"
response = await workflow.process_message(
    '{"data_dir": "data/input"}'
)

# Workflow executes and returns result
```

### Example 3: Multi-Step Task

```python
workflow = ChatBasedWorkflow()

response = await workflow.process_message(
    "Find all products in the Electronics category and calculate average price"
)

# Clarifications if needed
# Then execution of:
# 1. Load CSV
# 2. Filter by category
# 3. Calculate average
# 4. Format result
```

## 🧪 Testing

### Run Examples

```bash
cd Code
python tests/workflow/example_chat_workflow.py
```

### Interactive Mode

```python
from src.workflow.chat_based_workflow import ChatBasedWorkflow
import asyncio

async def chat():
    workflow = ChatBasedWorkflow()
    
    while True:
        user_input = input("YOU: ")
        if user_input == "quit":
            break
        
        response = await workflow.process_message(user_input)
        print(f"ASSISTANT: {response}\n")

asyncio.run(chat())
```

## 🎨 Advanced Usage

### Custom Sequence Validation

```python
evaluator = SequenceEvaluatorAgent()

# Generate sequence
result = await evaluator.evaluate_sequence(task)

# Validate
is_valid, errors = evaluator.validate_sequence(result['sequence'])

if not is_valid:
    print(f"Sequence has errors: {errors}")
```

### Context Management

```python
workflow = ChatBasedWorkflow()

# Add context before task
workflow.state.context = {
    "user_name": "Alice",
    "default_csv": "sales.csv",
    "preferences": {"format": "detailed"}
}

# Task will use this context
response = await workflow.process_message("Analyze the default file")
```

### Step-by-Step Execution

```python
# Generate sequence but don't execute
evaluation = await workflow.evalu