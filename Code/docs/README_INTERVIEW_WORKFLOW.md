# 🎯 Interview Question Generator - Complete Workflow

> A production-ready workflow that combines CSV Filter Agent and LLM agents to generate personalized interview questions based on user profiles.

[![Status](https://img.shields.io/badge/status-production--ready-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)]()
[![LLM](https://img.shields.io/badge/LLM-Ollama-orange)]()

## 📖 Overview

This workflow automatically:
1. ✅ Fetches user profiles from CSV files
2. ✅ Analyzes skills, experience, and job role
3. ✅ Generates tailored interview questions using AI
4. ✅ Returns structured JSON with categorized questions

## 🚀 Quick Start (30 Seconds)

```bash
# 1. Test the workflow
cd Code
python test_interview_workflow.py

# 2. Generate questions
python generate_interview_questions.py --user-id 1 --pretty

# 3. Use in your code
python -c "
from interview_question_workflow import InterviewQuestionWorkflow
workflow = InterviewQuestionWorkflow()
result = workflow.generate_interview_questions(user_id=1)
print(result['user_profile']['name'])
print(f'Generated {len(result[\"interview_questions\"])} questions')
"
```

## 📦 What's Included

### 🔧 Core Files
- **`interview_question_workflow.py`** - Main workflow implementation
- **`generate_interview_questions.py`** - CLI tool
- **`test_interview_workflow.py`** - Comprehensive tests
- **`data/input/test-agent.csv`** - Sample user data (10 profiles)

### 📚 Documentation
- **`docs/interview_workflow_guide.md`** - Complete guide (650+ lines)
- **`QUICKSTART_INTERVIEW_WORKFLOW.md`** - Quick reference
- **`INTERVIEW_WORKFLOW_SUMMARY.md`** - Full summary

## 💡 Usage Examples

### Command Line

```bash
# Generate 5 questions for user ID 1
python generate_interview_questions.py --user-id 1 --pretty

# Generate by name
python generate_interview_questions.py --name "John Doe" --pretty

# Generate 10 questions and save to file
python generate_interview_questions.py --user-id 1 --questions 10 --output results.json

# Batch processing
python generate_interview_questions.py --batch --user-ids 1 2 3 4 5
```

### Python API

```python
from interview_question_workflow import InterviewQuestionWorkflow

# Initialize workflow
workflow = InterviewQuestionWorkflow(
    csv_file="test-agent.csv",
    data_dir="data/input",
    num_questions=5
)

# Single user
result = workflow.generate_interview_questions(user_id=1)

# By name
result = workflow.generate_interview_questions(name="Jane Smith")

# Batch processing
results = workflow.generate_questions_batch(user_ids=[1, 2, 3])
```

## 📊 Input/Output

### Input (Python)
```python
workflow.generate_interview_questions(user_id=1)
```

### Input (CLI)
```bash
python generate_interview_questions.py --user-id 1
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
      "question": "Can you explain the bias-variance tradeoff...",
      "category": "Technical",
      "difficulty": "Medium",
      "focus_area": "Machine Learning"
    }
  ],
  "metadata": {
    "total_questions": 5,
    "llm_provider": "ollama",
    "llm_model": "llama3.2"
  }
}
```

## 🏗️ Architecture

```
User Input → CSV Filter Agent → Profile Analysis → LLM Agent → JSON Output
   (ID/Name)     (Fetch User)    (Extract Data)    (Generate)   (Questions)
```

**Components:**
- **CSV Filter Agent**: Filters and retrieves user profiles
- **Sync Executor Agent**: Manages LLM communication
- **Ollama LLM**: Generates contextual interview questions
- **JSON Parser**: Structures output with metadata

## 🎯 Features

- ✅ **Profile-Aware Questions** - Tailored to skills and experience
- ✅ **Multiple Categories** - Technical, Behavioral, Problem-Solving
- ✅ **Difficulty Levels** - Easy, Medium, Hard
- ✅ **Batch Processing** - Generate for multiple users
- ✅ **Active/Inactive Filtering** - Control which users to process
- ✅ **Error Handling** - Graceful failures with clear messages
- ✅ **CLI & API** - Use via command line or Python
- ✅ **Structured Output** - Consistent JSON format

## 📋 Sample Data

The workflow includes `test-agent.csv` with 10 sample users:

| user_id | name | job_role | skills | experience | active |
|---------|------|----------|--------|------------|--------|
| 1 | John Doe | Data Scientist | Python,ML,Data Analysis | 5 | TRUE |
| 2 | Jane Smith | Backend Engineer | Java,Spring Boot | 7 | TRUE |
| 3 | Alice Johnson | Frontend Developer | React,TypeScript | 3 | FALSE |
| ... | ... | ... | ... | ... | ... |

## 🔧 Configuration

### Workflow Setup
```python
workflow = InterviewQuestionWorkflow(
    csv_file="test-agent.csv",      # CSV file name
    data_dir="data/input",           # Data directory
    llm_provider="ollama",           # LLM provider
    llm_model="llama3.2",            # Model name
    num_questions=5                  # Questions to generate
)
```

### CLI Options
```bash
Options:
  --user-id, -u      User ID to generate for
  --name, -n         User name to generate for
  --batch, -b        Batch mode
  --user-ids         List of user IDs for batch
  --questions, -q    Number of questions (default: 5)
  --output, -o       Output file path
  --pretty, -p       Pretty print JSON
  --include-inactive Include inactive users
```

## 🔗 Integration Examples

### Flask API
```python
from flask import Flask, jsonify
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

### FastAPI
```python
from fastapi import FastAPI
app = FastAPI()
workflow = InterviewQuestionWorkflow()

@app.get("/questions/{user_id}")
async def get_questions(user_id: int):
    return workflow.generate_interview_questions(user_id=user_id)
```

## 🧪 Testing

### Run All Tests
```bash
python test_interview_workflow.py
```

**Tests include:**
- ✅ Workflow initialization
- ✅ User profile fetching (by ID and name)
- ✅ Question generation
- ✅ Active/inactive user handling
- ✅ Batch processing
- ✅ Error handling
- ✅ JSON parsing

### Manual Testing
```bash
# Single user
python generate_interview_questions.py --user-id 1 --pretty

# Batch
python generate_interview_questions.py --batch --user-ids 1 2 3

# Inactive user
python generate_interview_questions.py --user-id 3 --include-inactive
```

## 🎓 Use Cases

### 1. HR Recruitment
```python
# Generate questions for all active candidates
results = workflow.generate_questions_batch(user_ids=None, active_only=True)
```

### 2. Interview Preparation
```bash
# Save questions for interview prep
python generate_interview_questions.py --user-id 1 --questions 10 --output prep.json
```

### 3. Web Portal
```python
# Integrate with web application
@app.route('/api/questions/<int:user_id>')
def generate_questions(user_id):
    result = workflow.generate_interview_questions(user_id=user_id)
    return jsonify(result)
```

### 4. Batch Reports
```python
# Generate report for multiple candidates
results = workflow.generate_questions_batch(user_ids=[1,2,3,4,5])
create_pdf_report(results, "interview_questions.pdf")
```

## ⚠️ Troubleshooting

### User Not Found
```python
# Check user exists
workflow.csv_agent.preview_csv("test-agent.csv")
```

### LLM Connection Error
```bash
# Verify Ollama is running
ollama list

# Pull model if needed
ollama pull llama3.2
```

### Slow Response
- Use faster model
- Reduce `num_questions`
- Ensure Ollama has resources

## 📈 Performance

- **Single User**: 10-30 seconds (LLM dependent)
- **Batch (10 users)**: 2-5 minutes (sequential)
- **CSV Lookup**: <1 second

## ✅ Prerequisites

Before running:
- [ ] Python 3.8+
- [ ] Ollama installed and running
- [ ] Model available (`ollama pull llama3.2`)
- [ ] CSV file in `data/input/`
- [ ] Dependencies installed (`pip install -r requirements.txt`)

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Full Guide](docs/interview_workflow_guide.md) | Complete documentation (650+ lines) |
| [Quick Start](QUICKSTART_INTERVIEW_WORKFLOW.md) | Quick reference guide |
| [Summary](INTERVIEW_WORKFLOW_SUMMARY.md) | Full implementation summary |

## 🚀 Next Steps

1. **Run Tests**: `python test_interview_workflow.py`
2. **Try Examples**: `python generate_interview_questions.py --user-id 1 --pretty`
3. **Integrate**: Add to your application using the Python API
4. **Customize**: Modify number of questions, LLM model, etc.
5. **Deploy**: Use in production with Flask, FastAPI, or Streamlit

## 🤝 Contributing

This is part of a hackathon project. Feel free to:
- Add more question categories
- Improve LLM prompts
- Add async batch processing
- Create templates by job role
- Add multi-language support

## 📄 License

Part of the Hackathon project.

## 👨‍💻 Author

**AI Assistant**  
Date: November 27, 2024  
Status: Production Ready

---

## 🎉 Ready to Use!

Start generating interview questions now:

```bash
python generate_interview_questions.py --user-id 1 --pretty
```

**Questions? Issues?** Check the documentation or run the tests!
