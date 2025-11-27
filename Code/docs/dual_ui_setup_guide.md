# Dual Streamlit UI Setup Guide

This guide explains how to set up and run two separate Streamlit UIs for monitoring and controlling your LangGraph workflow.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    DUAL UI ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐           ┌──────────────────┐       │
│  │   Admin/Monitor  │           │   End User UI    │       │
│  │   UI (Port 8501) │           │   (Port 8502)    │       │
│  │                  │           │                  │       │
│  │  - View workflow │           │  - Input data    │       │
│  │  - Monitor steps │           │  - View results  │       │
│  │  - Check logs    │           │  - Simple UI     │       │
│  │  - Statistics    │           │                  │       │
│  └────────┬─────────┘           └─────────┬────────┘       │
│           │                               │                │
│           └───────────┬───────────────────┘                │
│                       │                                    │
│              ┌────────▼─────────┐                          │
│              │  State Manager   │                          │
│              │  (File-based)    │                          │
│              │                  │                          │
│              │  - Current exec  │                          │
│              │  - History       │                          │
│              │  - Logs          │                          │
│              └────────┬─────────┘                          │
│                       │                                    │
│              ┌────────▼─────────┐                          │
│              │ LangGraph        │                          │
│              │ Workflow         │                          │
│              │                  │                          │
│              │ - Fetch profile  │                          │
│              │ - Validate       │                          │
│              │ - Generate Qs    │                          │
│              │ - Parse & Format │                          │
│              └──────────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

## File Structure

Create this structure in your project:

```
your_project/
├── Code/                           # Your existing code
│   ├── src/
│   │   └── workflow/
│   │       └── langgraph_interview_workflow.py
│   └── data/
│       └── input/
│           └── test-agent.csv
│
├── ui/                             # NEW: UI folder
│   ├── workflow_state_manager.py   # Shared state management
│   ├── admin_monitor_ui.py         # Admin/Monitor UI
│   ├── user_interface_ui.py        # End User UI
│   └── launch_uis.py               # Launcher script
│
└── workflow_state/                 # Auto-created for state storage
    ├── executions.json
    └── current_execution.json
```

## Installation Steps

### 1. Install Required Packages

```bash
pip install streamlit
```

Make sure you have all your existing requirements installed:
```bash
pip install -r Code/requirements.txt
```

### 2. Create the UI Folder

```bash
mkdir ui
cd ui
```

### 3. Create the Three UI Files

Save the three artifacts I provided:
- `workflow_state_manager.py` - State management
- `admin_monitor_ui.py` - Admin/monitor interface
- `user_interface_ui.py` - End user interface

## Running the UIs

### Method 1: Run Separately (Recommended for Development)

Open **two separate terminal windows**:

**Terminal 1 - Admin Monitor UI:**
```bash
cd ui
streamlit run admin_monitor_ui.py --server.port 8501
```

**Terminal 2 - End User UI:**
```bash
cd ui
streamlit run user_interface_ui.py --server.port 8502
```

### Method 2: Use Launcher Script (Recommended for Production)

Create a launcher script:

**For Windows (`ui/launch_uis.bat`):**
```batch
@echo off
echo Starting LangGraph Dual UIs...
echo.
echo Admin Monitor UI will open on: http://localhost:8501
echo End User UI will open on: http://localhost:8502
echo.
start cmd /k "streamlit run admin_monitor_ui.py --server.port 8501"
start cmd /k "streamlit run user_interface_ui.py --server.port 8502"
echo.
echo Both UIs are starting...
echo Press any key to exit
pause
```

**For Linux/Mac (`ui/launch_uis.sh`):**
```bash
#!/bin/bash
echo "Starting LangGraph Dual UIs..."
echo ""
echo "Admin Monitor UI will open on: http://localhost:8501"
echo "End User UI will open on: http://localhost:8502"
echo ""

# Start both UIs in background
streamlit run admin_monitor_ui.py --server.port 8501 &
streamlit run user_interface_ui.py --server.port 8502 &

echo ""
echo "Both UIs are running!"
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
wait
```

Then run:
```bash
# Windows
cd ui
launch_uis.bat

# Linux/Mac
cd ui
chmod +x launch_uis.sh
./launch_uis.sh
```

## Usage Workflow

### For End Users:

1. Open **http://localhost:8502** (End User UI)
2. Enter candidate information:
   - Choose User ID or User Name
   - Select CSV file
   - Choose number of questions (1-10)
3. Click "🚀 Generate Interview Questions"
4. Wait for results to appear
5. Download results as JSON if needed

### For Admins/Monitors:

1. Open **http://localhost:8501** (Admin Monitor UI)
2. View real-time execution:
   - Current workflow status
   - Step-by-step progress
   - Live logs
   - Execution details
3. Monitor statistics:
   - Total executions
   - Success rate
   - Error counts
4. Review execution history

## Features

### Admin/Monitor UI Features:
- ✅ Real-time workflow monitoring
- ✅ Step-by-step progress tracking
- ✅ Live log streaming
- ✅ Execution statistics
- ✅ History viewer
- ✅ Auto-refresh (5-second intervals)
- ✅ Manual refresh control
- ✅ Clear current execution

### End User UI Features:
- ✅ Simple, clean interface
- ✅ Flexible input (ID or Name)
- ✅ CSV file selection
- ✅ Customizable question count
- ✅ LLM provider selection
- ✅ Beautiful result display
- ✅ JSON download
- ✅ Category badges (Technical, Behavioral, Problem-solving)
- ✅ Difficulty levels (Junior, Mid, Senior)

## State Management

The system uses **file-based state management** for simplicity:

- `workflow_state/executions.json` - Stores execution history
- `workflow_state/current_execution.json` - Stores current active execution

Both UIs read from these files, allowing real-time synchronization.

## Customization

### Change Ports

Edit the port numbers in your run commands or launcher scripts:
```bash
streamlit run admin_monitor_ui.py --server.port YOUR_PORT
```

### Modify Refresh Rate

In `admin_monitor_ui.py`, change the sleep duration:
```python
if auto_refresh:
    time.sleep(5)  # Change to your preferred seconds
    st.rerun()
```

### Add More Workflow Steps

In `workflow_state_manager.py`, update `create_execution`:
```python
total_steps=6  # Change to your workflow's step count
```

### Customize UI Colors

Edit the CSS in the `st.markdown()` sections of each UI file.

## Troubleshooting

### Issue: Port Already in Use
**Solution:** Change the port number or kill the existing process:
```bash
# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8501 | xargs kill -9
```

### Issue: State Files Not Found
**Solution:** The `workflow_state/` folder is auto-created. If issues persist:
```bash
mkdir workflow_state
```

### Issue: Workflow Not Running
**Solution:** Check that:
1. CSV file exists in `Code/data/input/`
2. LLM provider is configured correctly
3. Check logs in Admin Monitor UI

### Issue: UIs Not Syncing
**Solution:** 
1. Click "🔄 Refresh Data" in Admin UI
2. Enable "Auto-refresh" toggle
3. Check file permissions on `workflow_state/` folder

## Advanced Configuration

### Use Database Instead of Files

Replace `WorkflowStateManager` with a database backend:
```python
# In workflow_state_manager.py
# Replace file operations with SQLite/PostgreSQL queries
```

### Add Authentication

Add Streamlit authentication:
```python
# At top of UI files
import streamlit_authenticator as stauth

authenticator = stauth.Authenticate(...)
authenticator.login('Login', 'main')
```

### Deploy to Cloud

Deploy both UIs using Streamlit Cloud, Heroku, or Docker:
```dockerfile
# Dockerfile
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501 8502
CMD ["bash", "launch_uis.sh"]
```

## Best Practices

1. **Always start Admin UI first** - To monitor from the beginning
2. **Use auto-refresh in Admin UI** - For real-time monitoring
3. **Keep UIs on separate screens** - Side-by-side monitoring
4. **Download results regularly** - JSON backup of generated questions
5. **Check logs for debugging** - Admin UI shows detailed logs
6. **Clear old executions** - Keep state files clean

## Next Steps

1. ✅ Set up the file structure
2. ✅ Create the three Python files
3. ✅ Run both UIs
4. ✅ Test with sample data
5. ✅ Customize styling if needed
6. ✅ Deploy to production

## Support

For issues or questions:
1. Check the logs in Admin Monitor UI
2. Verify CSV data format
3. Test LLM connectivity
4. Review execution history

---

**Ready to use!** 🚀

Open two browser tabs:
- Admin Monitor: http://localhost:8501
- End User: http://localhost:8502
