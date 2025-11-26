# Interview Question Generator Workflow

A comprehensive workflow that combines CSV Filter Agent and LLM agents to generate personalized interview questions based on user profiles.

## Overview

This workflow:
1. **Fetches user profiles** from CSV using CSVFilterAgent
2. **Analyzes the profile** (skills, experience, job role)
3. **Generates tailored interview questions** using Ollama LLM
4. **Returns structured JSON** with questions and metadata

## Architecture

```
┌─────────────────┐
│   User Input    │ (user_id or name)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ CSV Filter      │ Fetch user profile from test-agent.csv
│ Agent           │ 
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Profile         │ Extract: name, skills, experience, role
│ Analysis        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Prompt          │ Build tailored prompt for LLM
│ Generation      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ LLM Agent       │ Generate interview questions (Ollama)
│ (Ollama)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ JSON Response   │ Structured output with questions
└─────────────────┘
```

## Files Created

### 1. Core Workflow
- **`interview_question_workflow.py`** - Main workflow implementation
  - `InterviewQuestionWorkflow` class
  - Single and batch processing
  - Error handling and logging

### 2. User Data
- **`data/input/test-agent.csv`** - Sample user profiles
  - 10 sample users with various roles
  - Fields: user_id, name, skills, experience_years, job_role, active

### 3. CLI Tool
- **`generate_interview_questions.py`** - Standalone command-line tool
  - Easy command-line interface
  - Batch processing support
  - File output options

### 4. Test Script
- **`test_interview_workflow.py`** - Comprehensive tests
  - Tests all workflow features
  - Validates error handling
  - Demonstrates usage

## Installation

No additional dependencies required beyond existing project requirements.

## Quick Start

### 1. Test the Workflow
```bash
cd Code
python test_interview_workflow.py
```

### 2. Generate Questions for a User
```bash
python generate_interview_questions.py --user-id 1 --pretty
```

### 3. Use in Python Code
```python
from interview_question_workflow import InterviewQuestionWorkflow

# Initialize
workflow = InterviewQuestionWorkflow(
    csv_file="test-agent.csv",
    data_dir="data/input"
)

# Generate questions
result = workflow.generate_interview_questions(user_id=1)
print(json.dumps(result, indent=2))
```

## Sample CSV Data

The workflow uses `test-agent.csv`:

```csv
user_id,name,skills,experience_years,job_role,active
1,John Doe,"Python,Machine Learning,Data Analysis",5,Data Scientist,TRUE
2,Jane Smith,"Java,Spring Boot,Microservices",7,Backend Engineer,TRUE
3,Alice Johnson,"React,TypeScript,CSS",3,Frontend Developer,FALSE
...
```

## Usage Examples

### Example 1: Generate Questions by User ID

```python
from interview_question_workflow import InterviewQuestionWorkflow

workflow = InterviewQuestionWorkflow()
result = workflow.generate_interview_questions(user_id=1)
```

**Output:**
```json
{
  "status": "success",
  "user_profile": {
    "user_id": 1,
    "name": "John Doe",
    "job_role": "Data Scientist",
    "skills": "Python,Machine Learning,Data Analysis",
    "experience_years": 5,
    "active": true
  },
  "interview_questions": [
    {
      "question": "Can you explain the bias-variance tradeoff in machine learning?",
      "category": "Technical",
      "difficulty": "Medium",
      "focus_area": "Machine Learning"
    },
    {
      "question": "Describe a challenging data analysis project you've worked on...",
      "category": "Behavioral",
      "difficulty": "Medium",
      "focus_area": "Data Analysis"
    }
  ],
  "metadata": {
    "total_questions": 5,
    "requested_questions": 5,
    "llm_provider": "ollama",
    "llm_model": "llama3.2"
  }
}
```

### Example 2: Generate Questions by Name

```python
result = workflow.generate_interview_questions(name="Jane Smith")
```

### Example 3: Customize Number of Questions

```python
workflow = InterviewQuestionWorkflow(num_questions=10)
result = workflow.generate_interview_questions(user_id=2)
```

### Example 4: Batch Processing

```python
results = workflow.generate_questions_batch(user_ids=[1, 2, 3])

for result in results:
    print(f"User: {result['user_profile']['name']}")
    print(f"Questions: {len(result['interview_questions'])}")
```

### Example 5: Include Inactive Users

```python
result = workflow.generate_interview_questions(
    user_id=3,
    active_only=False  # Include inactive users
)
```

## Command-Line Usage

### Basic Usage

```bash
# Generate questions for user ID 1
python generate_interview_questions.py --user-id 1

# Generate questions by name
python generate_interview_questions.py --name "John Doe"

# Pretty print output
python generate_interview_questions.py --user-id 1 --pretty
```

### Advanced Usage

```bash
# Generate 10 questions
python generate_interview_questions.py --user-id 1 --questions 10

# Save to file
python generate_interview_questions.py --user-id 1 --output questions.json --pretty

# Use specific model
python generate_interview_questions.py --user-id 1 --model llama3.2

# Include inactive users
python generate_interview_questions.py --user-id 3 --include-inactive
```

### Batch Processing

```bash
# Generate for multiple users
python generate_interview_questions.py --batch --user-ids 1 2 3 4

# Batch with file output
python generate_interview_questions.py --batch --user-ids 1 2 3 --output batch_results.json
```

## API Reference

### InterviewQuestionWorkflow Class

#### `__init__(csv_file, data_dir, llm_provider, llm_model, num_questions)`

Initialize the workflow.

**Parameters:**
- `csv_file` (str): CSV file name (default: "test-agent.csv")
- `data_dir` (str): Data directory (default: "data/input")
- `llm_provider` (str): LLM provider (default: "ollama")
- `llm_model` (str): Model name (default: "llama3.2")
- `num_questions` (int): Number of questions to generate (default: 5)

#### `fetch_user_profile(user_id, name, active_only)`

Fetch user profile from CSV.

**Parameters:**
- `user_id` (int): User ID to search for
- `name` (str): User name to search for
- `active_only` (bool): Only return active users (default: True)

**Returns:** User profile dictionary

#### `generate_interview_questions(user_id, name, active_only)`

Generate interview questions for a user.

**Parameters:**
- `user_id` (int): User ID
- `name` (str): User name
- `active_only` (bool): Only process active users

**Returns:** Dictionary with user profile and questions

#### `generate_questions_batch(user_ids, active_only)`

Generate questions for multiple users.

**Parameters:**
- `user_ids` (List[int]): List of user IDs (None = all users)
- `active_only` (bool): Only process active users

**Returns:** List of results

## Output Format

The workflow returns a structured JSON response:

```json
{
  "status": "success",
  "user_profile": {
    "user_id": 1,
    "name": "John Doe",
    "job_role": "Data Scientist",
    "skills": "Python,Machine Learning,Data Analysis",
    "experience_years": 5,
    "active": true
  },
  "interview_questions": [
    {
      "question": "Question text here",
      "category": "Technical/Behavioral/Problem-Solving",
      "difficulty": "Easy/Medium/Hard",
      "focus_area": "Specific skill area"
    }
  ],
  "metadata": {
    "total_questions": 5,
    "requested_questions": 5,
    "llm_provider": "ollama",
    "llm_model": "llama3.2"
  }
}
```

## Configuration

### LLM Configuration

Change LLM provider and model:

```python
workflow = InterviewQuestionWorkflow(
    llm_provider="openai",  # or "ollama"
    llm_model="gpt-4"       # or "llama3.2"
)
```

### Question Configuration

Adjust number of questions:

```python
workflow = InterviewQuestionWorkflow(
    num_questions=10  # Generate 10 questions
)
```

### Data Configuration

Use different CSV file:

```python
workflow = InterviewQuestionWorkflow(
    csv_file="my_users.csv",
    data_dir="path/to/data"
)
```

## Error Handling

The workflow handles common errors gracefully:

### User Not Found
```python
try:
    result = workflow.generate_interview_questions(user_id=999)
except ValueError as e:
    print(f"Error: {e}")  # "No user found with user_id=999"
```

### Inactive User
```python
result = workflow.generate_interview_questions(
    user_id=3,
    active_only=True  # Will fail if user is inactive
)
```

### CSV File Missing
```python
workflow = InterviewQuestionWorkflow(csv_file="missing.csv")
# Raises FileNotFoundError
```

## Integration Examples

### Web API Integration

```python
from flask import Flask, jsonify, request
from interview_question_workflow import InterviewQuestionWorkflow

app = Flask(__name__)
workflow = InterviewQuestionWorkflow()

@app.route('/generate-questions', methods=['POST'])
def generate_questions():
    data = request.json
    user_id = data.get('user_id')
    
    result = workflow.generate_interview_questions(user_id=user_id)
    return jsonify(result)
```

### Streamlit App Integration

```python
import streamlit as st
from interview_question_workflow import InterviewQuestionWorkflow

st.title("Interview Question Generator")

workflow = InterviewQuestionWorkflow()
user_id = st.number_input("User ID", min_value=1)

if st.button("Generate Questions"):
    result = workflow.generate_interview_questions(user_id=user_id)
    
    if result["status"] == "success":
        st.write(f"**User:** {result['user_profile']['name']}")
        st.write(f"**Role:** {result['user_profile']['job_role']}")
        
        for i, q in enumerate(result['interview_questions'], 1):
            st.write(f"{i}. {q['question']}")
```

## Troubleshooting

### Issue: LLM Response Not Parsing

The workflow handles JSON parsing errors automatically. If the LLM returns non-JSON, it wraps the response in a default structure.

### Issue: No Questions Generated

Check that:
1. Ollama is running: `ollama list`
2. Model is available: `ollama pull llama3.2`
3. User exists in CSV and is active

### Issue: Slow Response

LLM generation can take 10-30 seconds. Consider:
- Using a faster model
- Reducing `num_questions`
- Implementing async processing

## Performance

- **Single User:** ~10-30 seconds (depends on LLM)
- **Batch (10 users):** ~2-5 minutes
- **CSV Lookup:** <1 second

## Future Enhancements

Potential improvements:
1. **Async batch processing** - Process multiple users in parallel
2. **Question caching** - Cache questions for similar profiles
3. **Question templates** - Pre-defined templates for common roles
4. **Difficulty adjustment** - Auto-adjust based on experience level
5. **Multi-language support** - Generate questions in different languages

## License

Part of the Hackathon project.

## Author

AI Assistant  
Date: 2024-11-27
