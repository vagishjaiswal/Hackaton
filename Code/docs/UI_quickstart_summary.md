# Dual Streamlit UI - Quick Start

Get your dual UI system up and running in 5 minutes!

## 📁 Step 1: Create File Structure

Create a `ui` folder in your project root:

```
your_project/
├── Code/                    # Your existing code
│   ├── src/
│   │   └── workflow/
│   │       └── langgraph_interview_workflow.py
│   └── data/
│       └── input/
│           └── test-agent.csv
│
└── ui/                      # NEW: Create this
    ├── workflow_state_manager.py
    ├── admin_monitor_ui.py
    ├── user_interface_ui.py
    └── launch_uis.py
```

## 📝 Step 2: Create the Files

Copy and create these 4 files in your `ui/` folder:

1. **workflow_state_manager.py** - State management (from artifact #1)
2. **admin_monitor_ui.py** - Admin/Monitor interface (from artifact #2)
3. **user_interface_ui.py** - End user interface (from artifact #3)
4. **launch_uis.py** - Launcher script (from artifact #5)

## 🔧 Step 3: Install Dependencies

```bash
pip install streamlit
```

## 🚀 Step 4: Launch!

### Option A: Use Launcher (Recommended)

```bash
cd ui
python launch_uis.py
```

### Option B: Manual Launch (Two Terminals)

**Terminal 1:**
```bash
cd ui
streamlit run admin_monitor_ui.py --server.port 8501
```

**Terminal 2:**
```bash
cd ui
streamlit run user_interface_ui.py --server.port 8502
```

## 🌐 Step 5: Access UIs

Two browser tabs will open automatically:

- **Admin Monitor**: http://localhost:8501
- **End User**: http://localhost:8502

## 🎯 Step 6: Test It!

1. Open **End User UI** (http://localhost:8502)
2. Enter User ID: `1`
3. Select CSV file
4. Click "🚀 Generate Interview Questions"
5. Switch to **Admin Monitor UI** (http://localhost:8501)
6. Watch real-time progress!

## 📊 What You'll See

### Admin Monitor UI
- ✅ Real-time workflow execution
- ✅ Step-by-step progress bars
- ✅ Live logs streaming
- ✅ Execution statistics
- ✅ History of all runs

### End User UI
- ✅ Simple input form
- ✅ Beautiful results display
- ✅ Category badges
- ✅ Difficulty levels
- ✅ JSON download

## 🔧 Optional: Integration

To add real-time monitoring to your workflow:

1. Add execution_id to your workflow state
2. Import WorkflowStateManager in your workflow
3. Add logging at each step

See `WORKFLOW_INTEGRATION_GUIDE.md` for details.

## 💡 Tips

- Keep both UIs open in separate browser tabs
- Enable auto-refresh in Admin UI
- Use Admin UI to debug issues
- Download results from End User UI

## 🐛 Troubleshooting

**Port already in use?**
```bash
# Change port in launch command
streamlit run admin_monitor_ui.py --server.port 8503
```

**UIs not syncing?**
- Click "🔄 Refresh Data" in Admin UI
- Enable "Auto-refresh" toggle

**Workflow not running?**
- Check CSV file exists in `Code/data/input/`
- Verify LLM provider configuration

## 📚 Documentation

- **DUAL_UI_SETUP_GUIDE.md** - Complete setup guide
- **WORKFLOW_INTEGRATION_GUIDE.md** - Integration with your workflow
- **launch_uis.py** - Automated launcher script

## 🎉 You're Done!

Your dual UI system is ready. Start generating interview questions and monitoring execution in real-time!

---

**Need help?** Check the Admin Monitor UI logs for detailed execution information.
