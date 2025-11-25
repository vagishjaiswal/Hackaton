# Hackathon AI Agent System

A flexible multi-agent AI system built with LangChain and LangGraph, designed for rapid adaptation during hackathons.

## Quick Start

1. **Create and activate a Python virtual environment:**
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```
2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```
3. **Copy and edit environment variables:**
   ```powershell
   copy .env.example .env
   # Edit .env with your API keys
   ```
4. **Run the application:**
   - For Streamlit UI:
     ```powershell
     streamlit run ui/app.py
     ```
   - For Flask UI (optional):
     ```powershell
     python ui/app.py
     ```
5. **Run tests:**
   ```powershell
   pytest tests/
   ```

## Project Structure

See `hackathon_requirements.md` for full details. Key folders:
- `src/` - Core Python modules
- `config/` - JSON configs
- `data/input/` - CSV data files
- `data/output/` - Results
- `ui/` - Web UI (Streamlit/Flask)
- `tests/` - Unit tests

## Configuration
- Edit `config/agents_config.json` and `config/workflow_config.json` to define agents and workflows.
- Place CSV files in `data/input/`.

## Environment Variables
- Set API keys and options in `.env`.

## Adaptation Guide
1. Define agents in `agents_config.json`
2. Add CSV data to `data/input/`
3. Update prompts/configs as needed
4. Run workflow and view results in UI

## Dependencies
See `requirements.txt` for all required packages.

## More Info
- See `hackathon_requirements.md` for requirements and implementation details.
- See `progress_tracker.md` for current status and next steps.
