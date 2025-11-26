# LangGraph Interview Workflow Implementation

## Overview

A complete multi-step LangGraph workflow for generating interview questions based on candidate profiles.

## Files Created

### 1. **langgraph_interview_workflow.py**
   Main workflow implementation with 6 processing steps:
   
   - **Step 1: Fetch User Profile** - Retrieves candidate data from CSV using CSVFilterAgent
   - **Step 2: Validate Profile** - Extracts and validates relevant candidate fields
   - **Step 3: Build Prompt** - Creates a tailored prompt for the LLM based on candidate info
   - **Step 4: Generate Questions** - Calls the LLM (Ollama/OpenAI) to generate questions
   - **Step 5: Parse Response** - Extracts and validates JSON from LLM response
   - **Step 6: Format Output** - Structures the final output with metadata

### 2. **test_langgraph_workflow.py**
   Test suite that validates workflow steps (1-3 work without LLM):
   
   - Test fetching user profile from CSV
   - Test profile validation
   - Test prompt building
   - Test workflow compilation

## Workflow Architecture

```
Initial State
    |
    v
Fetch User Profile (CSV Agent)
    |
    v
Validate Profile (Field extraction)
    |
    v
Build Prompt (Context-aware prompt)
    |
    v
Generate Questions (LLM Call - Ollama/OpenAI)
    |
    v
Parse Response (JSON extraction)
    |
    v
Format Output (Final structure)
    |
    v
Return Result
```

## State Management

The workflow uses a dictionary-based state with:

```python
{
    "user_id": int,
    "csv_file": str,
    "data_dir": str,
    "num_questions": int,
    "user_profile": dict,
    "prompt": str,
    "raw_response": str,
    "interview_questions": list,
    "status": str,
    "error": str,
    "step_count": int
}
```

## Usage Examples

### Basic Usage (Python)

```python
from langgraph_interview_workflow import create_interview_workflow

# Create workflow
workflow = create_interview_workflow(
    llm_provider="ollama",
    llm_model="llama3.2"
)

# Run workflow
result = workflow.invoke({
    "user_id": 1,
    "csv_file": "test-agent.csv",
    "data_dir": "../../data/input",
    "num_questions": 5,
    "llm_provider": "ollama",
    "llm_model": "llama3.2"
})

print(result["final_output"])
```

### Command Line

```bash
# Run the workflow directly
python langgraph_interview_workflow.py

# Run tests
python test_langgraph_workflow.py
```

## Features

✅ **Multi-step Processing** - 6 sequential steps with state management
✅ **Error Handling** - Comprehensive try-catch at each step
✅ **Flexible LLM Support** - Works with Ollama and OpenAI
✅ **Data Integration** - Uses CSV Filter Agent for candidate data
✅ **JSON Parsing** - Automatic extraction of questions from LLM response
✅ **Metadata Tracking** - Logs step count, processing status, errors
✅ **Logging** - Detailed logs for debugging

## Test Results

```
[TEST 1] Fetch User Profile - [PASSED]
[TEST 2] Validate User Profile - [PASSED]
[TEST 3] Build Question Prompt - [PASSED]
[TEST 4] Create LangGraph Workflow - [PASSED]

All workflow steps verified successfully!
```

## Key Implementation Details

### 1. State-based Processing
Each node receives and returns the complete state dictionary, allowing for error handling and state tracking.

### 2. Async LLM Integration
```python
# Generate questions asynchronously
response = asyncio.run(llm.generate(prompt))
```

### 3. JSON Parsing with Error Handling
```python
json_start = raw_response.find('{')
json_end = raw_response.rfind('}') + 1
json_str = raw_response[json_start:json_end]
parsed = json.loads(json_str)
```

### 4. Conditional Routing
Workflow automatically skips to output formatting on errors for graceful failure handling.

## Output Format

Success Response:
```json
{
  "status": "success",
  "user_profile": {
    "name": "John Doe",
    "job_role": "Data Scientist",
    "skills": "Python, ML, Data Analysis",
    "experience_years": 5
  },
  "interview_questions": [
    {
      "question": "...",
      "category": "technical|behavioral|problem-solving",
      "difficulty": "junior|mid|senior",
      "rationale": "..."
    }
  ],
  "metadata": {
    "total_questions": 3,
    "user_name": "John Doe",
    "job_role": "Data Scientist",
    "steps_completed": 6
  }
}
```

Error Response:
```json
{
  "status": "error",
  "error": "Error message",
  "user_profile": null,
  "interview_questions": []
}
```

## Dependencies

- `langgraph` - Workflow orchestration
- `src.agents.csv_filter_agent` - CSV data retrieval
- `src.llm.llm_provider_factory` - LLM provider factory
- Standard library: `json`, `logging`, `asyncio`, `dataclasses`

## Future Enhancements

1. Add caching for frequently requested profiles
2. Support batch processing of multiple users
3. Add question validation/quality checks
4. Implement retry logic for LLM failures
5. Add support for custom question templates
6. Store generated questions in database
