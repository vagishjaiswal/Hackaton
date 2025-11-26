# Interview Question Generator - Quick Reference

## 🚀 Quick Start (60 seconds)

### Step 1: Test the Workflow
```bash
cd Code
python test_interview_workflow.py
```

### Step 2: Generate Questions
```bash
# For user ID 1
python generate_interview_questions.py --user-id 1 --pretty

# For user by name
python generate_interview_questions.py --name "John Doe" --pretty
```

### Step 3: Use in Python
```python
from interview_question_workflow import InterviewQuestionWorkflow

workflow = InterviewQuestionWorkflow()
result = workflow.generate_interview_questions(user_id=1)
print(json.dumps(result, indent=2))
```

## 📋 Common Commands

```bash
# Basic usage
python generate_interview_questions.py --user-id 1

# Generate 10 questions
python generate_interview_questions.py --user-id 1 --questions 10

# Save to file
python generate_interview_questions.py --user-id 1 --output questions.json

# Batch processing
python generate_interview_questions.py --batch --user-ids 1 2 3

# Pretty print
python generate_interview_questions.py --user-id 1 --pretty
```

## 💡 Python API Examples

### Example 1: Single User
```python
from interview_question_workflow import InterviewQuestionWorkflow

workflow = InterviewQuestionWorkflow()
result = workflow.generate_interview_questions(user_id=1)

# Access results
print(f"User: {result['user_profile']['name']}")
print(f"Questions: {len(result['interview_questions'])}")

for q in result['interview_questions']:
    print(f"- {q['question']}")
```

### Example 2: By Name
```python
result = workflow.generate_interview_questions(name="Jane Smith")
```

### Example 3: Batch Processing
```python
results = workflow.generate_questions_batch(user_ids=[1, 2, 3])

for r in results:
    if r['status'] == 'success':
        print(f"{r['user_profile']['name']}: {len(r['interview_questions'])} questions")
```

### Example 4: Custom Configuration
```python
workflow = InterviewQuestionWorkflow(
    csv_file="test-agent.csv",
    data_dir="data/input",
    llm_provider="ollama",
    llm_model="llama3.2",
    num_questions=10
)

result = workflow.generate_interview_questions(user_id=1)
```

## 📊 Input/Output Format

### Input (Python)
```python
# Method 1: By User ID
workflow.generate_interview_questions(user_id=1)

# Method 2: By Name
workflow.generate_interview_questions(name="John Doe")

# Method 3: Include Inactive Users
workflow.generate_interview_questions(user_id=3, active_only=False)
```

### Output (JSON)
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
      "question": "Explain the bias-variance tradeoff...",
      "category": "Technical",
      "difficulty": "Medium",
      "focus_area": "Machine Learning"
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

## 🔧 Configuration Options

### Workflow Configuration
```python
workflow = InterviewQuestionWorkflow(
    csv_file="test-agent.csv",      # CSV file name
    data_dir="data/input",           # Data directory
    llm_provider="ollama",           # LLM provider
    llm_model="llama3.2",            # Model name
    num_questions=5                  # Number of questions
)
```

### Command-Line Options
```bash
--user-id, -u      User ID to generate questions for
--name, -n         User name to generate questions for
--batch, -b        Batch mode for multiple users
--user-ids         List of user IDs for batch
--questions, -q    Number of questions (default: 5)
--csv-file         CSV file name
--data-dir         Data directory
--provider         LLM provider (default: ollama)
--model            LLM model (default: llama3.2)
--output, -o       Output file path
--pretty, -p       Pretty print JSON
--include-inactive Include inactive users
```

## 📁 Sample Data (test-agent.csv)

```csv
user_id,name,skills,experience_years,job_role,active
1,John Doe,"Python,Machine Learning,Data Analysis",5,Data Scientist,TRUE
2,Jane Smith,"Java,Spring Boot,Microservices",7,Backend Engineer,TRUE
3,Alice Johnson,"React,TypeScript,CSS",3,Frontend Developer,FALSE
```

## ⚠️ Error Handling

```python
try:
    result = workflow.generate_interview_questions(user_id=999)
except ValueError as e:
    print(f"Error: {e}")  # User not found
```

Common errors:
- **User not found**: Check user_id exists in CSV
- **Inactive user**: Set `active_only=False` to include
- **CSV file missing**: Verify file path and name
- **LLM error**: Ensure Ollama is running

## 🎯 Use Cases

### 1. Generate Questions for Active Candidates
```python
# Get all active users
workflow = InterviewQuestionWorkflow()
results = workflow.generate_questions_batch(
    user_ids=None,  # All users
    active_only=True
)
```

### 2. Prepare Interview Questions for Specific Role
```python
# Filter by job role in your code
result = workflow.generate_interview_questions(user_id=1)
if result['user_profile']['job_role'] == 'Data Scientist':
    # Process data science questions
    pass
```

### 3. Save Questions to Database
```python
result = workflow.generate_interview_questions(user_id=1)

# Save to database
save_to_db(
    user_id=result['user_profile']['user_id'],
    questions=result['interview_questions'],
    timestamp=datetime.now()
)
```

## 🧪 Testing

```bash
# Run comprehensive tests
python test_interview_workflow.py

# Test specific user
python generate_interview_questions.py --user-id 1 --pretty

# Test batch processing
python generate_interview_questions.py --batch --user-ids 1 2
```

## 📚 Documentation

- **Full Guide**: `docs/interview_workflow_guide.md`
- **Workflow Code**: `interview_question_workflow.py`
- **CLI Tool**: `generate_interview_questions.py`
- **Tests**: `test_interview_workflow.py`

## 🔗 Integration

### Flask API
```python
from flask import Flask, jsonify, request
app = Flask(__name__)
workflow = InterviewQuestionWorkflow()

@app.route('/questions/<int:user_id>')
def get_questions(user_id):
    result = workflow.generate_interview_questions(user_id=user_id)
    return jsonify(result)
```

### Streamlit App
```python
import streamlit as st
workflow = InterviewQuestionWorkflow()

user_id = st.number_input("User ID", min_value=1)
if st.button("Generate"):
    result = workflow.generate_interview_questions(user_id=user_id)
    st.json(result)
```

## ✅ Checklist

Before running:
- [ ] Ollama is installed and running
- [ ] Model is available (`ollama pull llama3.2`)
- [ ] CSV file exists in `data/input/`
- [ ] Python dependencies installed

## 🎉 Ready to Use!

The workflow is production-ready. Start generating interview questions now!

```bash
python generate_interview_questions.py --user-id 1 --pretty
```

---

**Need Help?** See `docs/interview_workflow_guide.md` for detailed documentation.
