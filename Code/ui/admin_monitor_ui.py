"""
Admin/Monitor UI for LangGraph Workflow with TinyDB Audit System
Run with: streamlit run admin_monitor_ui.py --server.port 8501
"""

import streamlit as st
import sys
import time
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ui.workflow_state_manager import WorkflowStateManager, WorkflowStatus
from src.tools.audit_manager import TinyDBAuditManager

# Page configuration
st.set_page_config(
    page_title="LangGraph Workflow Monitor with Audit",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-card {
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid;
        margin-bottom: 1rem;
    }
    .status-idle { border-color: #94a3b8; background-color: #f1f5f9; }
    .status-running { border-color: #3b82f6; background-color: #dbeafe; }
    .status-completed { border-color: #10b981; background-color: #d1fae5; }
    .status-error { border-color: #ef4444; background-color: #fee2e2; }
    .log-entry {
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        padding: 0.5rem;
        background-color: #f8fafc;
        border-radius: 4px;
        margin-bottom: 0.25rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .audit-table {
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize managers
@st.cache_resource
def get_managers():
    state_mgr = WorkflowStateManager()
    audit_mgr = TinyDBAuditManager()
    return state_mgr, audit_mgr

state_manager, audit_manager = get_managers()

# Header
st.markdown("""
<div class="main-header">
    <h1>🔍 LangGraph Workflow Monitor with Audit Trail</h1>
    <p>Real-time monitoring, control, and audit logging of workflow execution</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Controls & Monitoring")
    
    # Navigation
    page = st.radio(
        "Select View",
        ["Current Execution", "Audit Trail", "Metrics & Analytics", "Agent Performance", "System Health"]
    )
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()
    
    st.divider()
    
    # Auto-refresh toggle
    auto_refresh = st.toggle("Auto-refresh (5s)", value=True)
    if auto_refresh:
        time.sleep(5)
        st.rerun()
    
    st.divider()
    
    # Get statistics from audit system
    st.subheader("📊 Audit Statistics")
    try:
        stats = audit_manager.get_statistics()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Workflows", stats["total_workflows"])
            st.metric("Failed", stats["failed_workflows"])
        with col2:
            st.metric("Completed", stats["completed_workflows"])
            st.metric("Success Rate", f"{stats['success_rate']:.1f}%")
        
        st.metric("Total Audit Entries", stats["total_audit_entries"])
    except Exception as e:
        st.warning(f"Could not load audit stats: {e}")
    
    st.divider()
    
    # Workflow statistics
    st.subheader("📊 Workflow Statistics")
    workflow_stats = state_manager.get_stats()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Runs", workflow_stats["total_executions"])
        st.metric("Errors", workflow_stats["errors"])
    with col2:
        st.metric("Completed", workflow_stats["completed"])
        st.metric("Success Rate", f"{workflow_stats['success_rate']:.1f}%")
    
    st.divider()
    
    # Management buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Current", use_container_width=True, type="secondary"):
            state_manager.clear_current_execution()
            st.success("Current execution cleared!")
            time.sleep(1)
            st.rerun()
    
    with col2:
        if st.button("📤 Export Audit", use_container_width=True, type="secondary"):
            try:
                export_path = "audit_export.json"
                audit_manager.export_data(export_path)
                st.success(f"Exported to {export_path}")
            except Exception as e:
                st.error(f"Export failed: {e}")

# Main content - Page routing
if page == "Current Execution":
    # ========================================================================
    # Current Execution
    # ========================================================================
    
    current_execution = state_manager.get_current_execution()
    
    if current_execution:
        # Execution status header
        status = current_execution.get("status", "idle")
        status_colors = {
            "idle": ("🟡", "status-idle"),
            "running": ("🔵", "status-running"),
            "completed": ("🟢", "status-completed"),
            "error": ("🔴", "status-error")
        }
        icon, css_class = status_colors.get(status, ("⚪", "status-idle"))
        
        st.markdown(f"""
        <div class="status-card {css_class}">
            <h3>{icon} Execution: {current_execution["execution_id"]}</h3>
            <p><strong>Status:</strong> {status.upper()} | <strong>Step:</strong> {current_execution["current_step"]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress
        progress = current_execution["steps_completed"] / current_execution["total_steps"]
        st.progress(progress, text=f"Step {current_execution['steps_completed']}/{current_execution['total_steps']}")
        
        # Main tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 Overview", 
            "📝 Logs", 
            "📊 Details", 
            "📥 Input/Output",
            "🔐 Audit"
        ])
        
        with tab1:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Current Step", current_execution["current_step"])
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                duration = "Calculating..."
                if current_execution.get("end_time"):
                    start = datetime.fromisoformat(current_execution["start_time"])
                    end = datetime.fromisoformat(current_execution["end_time"])
                    duration = f"{(end - start).total_seconds():.1f}s"
                else:
                    start = datetime.fromisoformat(current_execution["start_time"])
                    duration = f"{(datetime.now() - start).total_seconds():.1f}s"
                st.metric("Duration", duration)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Steps Completed", f"{current_execution['steps_completed']}/{current_execution['total_steps']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Workflow visualization
            st.subheader("🔄 Workflow Steps")
            steps = [
                "Fetch User Profile",
                "Validate Profile",
                "Build Prompt",
                "Generate Questions",
                "Parse Response",
                "Format Output"
            ]
            
            cols = st.columns(len(steps))
            for i, (col, step) in enumerate(zip(cols, steps)):
                with col:
                    if i < current_execution["steps_completed"]:
                        st.success(f"✅ {step}", icon="✅")
                    elif i == current_execution["steps_completed"]:
                        st.info(f"⏳ {step}", icon="⏳")
                    else:
                        st.text(f"⚪ {step}")
        
        with tab2:
            st.subheader("📝 Execution Logs")
            
            logs = current_execution.get("logs", [])
            if logs:
                for log in reversed(logs[-50:]):
                    st.markdown(f'<div class="log-entry">{log}</div>', unsafe_allow_html=True)
            else:
                st.info("No logs available yet")
        
        with tab3:
            st.subheader("📊 Execution Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Execution ID:**", current_execution["execution_id"])
                st.write("**Start Time:**", current_execution["start_time"])
                if current_execution.get("end_time"):
                    st.write("**End Time:**", current_execution["end_time"])
            
            with col2:
                st.write("**Status:**", current_execution["status"])
                st.write("**Total Steps:**", current_execution["total_steps"])
                st.write("**Steps Completed:**", current_execution["steps_completed"])
            
            if current_execution.get("error"):
                st.error(f"**Error:** {current_execution['error']}")
        
        with tab4:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📥 User Input")
                st.json(current_execution["user_input"])
            
            with col2:
                st.subheader("📤 Result")
                if current_execution.get("result"):
                    st.json(current_execution["result"])
                else:
                    st.info("Result not available yet")
        
        with tab5:
            st.subheader("🔐 Audit Trail for Execution")
            
            try:
                exec_id = current_execution["execution_id"]
                audit_entries = audit_manager.get_audit_trail(
                    execution_id=exec_id,
                    limit=100
                )
                
                if audit_entries:
                    # Create DataFrame for better display
                    df_data = []
                    for entry in audit_entries:
                        df_data.append({
                            "Timestamp": entry.get("timestamp", ""),
                            "Event Type": entry.get("event_type", ""),
                            "Agent": entry.get("agent_name", "-"),
                            "Action": entry.get("action", "-"),
                            "Status": entry.get("status", ""),
                            "Duration (ms)": entry.get("duration_ms", "-")
                        })
                    
                    df = pd.DataFrame(df_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    st.metric("Total Audit Entries", len(audit_entries))
                else:
                    st.info("No audit entries yet")
            
            except Exception as e:
                st.error(f"Error loading audit trail: {e}")
    
    else:
        st.info("👋 No active workflow execution. Waiting for user input...")
        
        st.subheader("📜 Recent Executions")
        
        history = state_manager.get_execution_history(limit=10)
        if history:
            for exec_data in history:
                status = exec_data.get("status", "unknown")
                icon = {"completed": "🟢", "error": "🔴", "running": "🔵"}.get(status, "⚪")
                
                with st.expander(f"{icon} {exec_data['execution_id']} - {status.upper()}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Start:**", exec_data.get("start_time", "N/A"))
                        st.write("**Steps:**", f"{exec_data.get('steps_completed', 0)}/{exec_data.get('total_steps', 0)}")
                    with col2:
                        if exec_data.get("end_time"):
                            st.write("**End:**", exec_data["end_time"])
                        if exec_data.get("error"):
                            st.error(exec_data["error"])
        else:
            st.write("No execution history available")

elif page == "Audit Trail":
    # ========================================================================
    # Audit Trail
    # ========================================================================
    
    st.subheader("🔐 Audit Trail")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_workflow = st.text_input("Filter by Workflow ID (optional)")
    with col2:
        filter_event = st.selectbox(
            "Event Type",
            ["All", "workflow_start", "workflow_end", "agent_action", "error"]
        )
    with col3:
        limit = st.slider("Limit entries", 10, 500, 100)
    
    try:
        filters = {}
        if filter_workflow:
            filters["workflow_id"] = filter_workflow
        if filter_event != "All":
            filters["event_type"] = filter_event
        
        audit_entries = audit_manager.get_audit_trail(limit=limit, **filters)
        
        if audit_entries:
            # Create DataFrame
            df_data = []
            for entry in audit_entries:
                df_data.append({
                    "Timestamp": entry.get("timestamp", "")[:19],
                    "Event": entry.get("event_type", ""),
                    "Workflow": entry.get("workflow_id", "")[:10] + "...",
                    "Execution": entry.get("execution_id", "")[:10] + "...",
                    "Agent": entry.get("agent_name", "-"),
                    "Action": entry.get("action", "-"),
                    "Status": entry.get("status", ""),
                    "Duration (ms)": entry.get("duration_ms", "-")
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.metric("Audit Entries", len(audit_entries))
        else:
            st.info("No audit entries found")
    
    except Exception as e:
        st.error(f"Error loading audit trail: {e}")

elif page == "Metrics & Analytics":
    # ========================================================================
    # Metrics & Analytics
    # ========================================================================
    
    st.subheader("📊 Metrics & Analytics")
    
    try:
        stats = audit_manager.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Workflows", stats["total_workflows"])
        with col2:
            st.metric("Completed", stats["completed_workflows"])
        with col3:
            st.metric("Failed", stats["failed_workflows"])
        with col4:
            st.metric("Success Rate", f"{stats['success_rate']:.1f}%")
        
        st.divider()
        
        # Workflow duration analysis
        st.subheader("⏱️ Workflow Duration Analysis")
        
        workflows = audit_manager.workflow_db.all()
        
        if workflows:
            durations = [w.get("total_duration_ms", 0) for w in workflows if w.get("total_duration_ms")]
            
            if durations:
                import statistics
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Avg Duration (ms)", f"{statistics.mean(durations):.0f}")
                with col2:
                    st.metric("Max Duration (ms)", f"{max(durations):.0f}")
                with col3:
                    st.metric("Min Duration (ms)", f"{min(durations):.0f}")
                with col4:
                    st.metric("Median Duration (ms)", f"{statistics.median(durations):.0f}")
                
                # Duration chart
                df_durations = pd.DataFrame({
                    "Workflow ID": [w.get("workflow_id", "")[:10] for w in workflows],
                    "Duration (ms)": durations
                })
                
                st.line_chart(df_durations.set_index("Workflow ID"))
        
        st.divider()
        
        # Error analysis
        st.subheader("⚠️ Error Analysis")
        
        errors = audit_manager.get_recent_errors(hours=24, limit=50)
        
        if errors:
            st.metric("Recent Errors (24h)", len(errors))
            
            error_data = []
            for error in errors:
                error_data.append({
                    "Time": error.get("timestamp", "")[:19],
                    "Workflow": error.get("workflow_id", "")[:10],
                    "Error": error.get("error_message", "")[:50]
                })
            
            df_errors = pd.DataFrame(error_data)
            st.dataframe(df_errors, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No errors in last 24 hours!")
    
    except Exception as e:
        st.error(f"Error loading metrics: {e}")

elif page == "Agent Performance":
    # ========================================================================
    # Agent Performance
    # ========================================================================
    
    st.subheader("🤖 Agent Performance Metrics")
    
    try:
        agent_metrics = audit_manager.get_agent_metrics()
        
        if agent_metrics:
            # Create DataFrame
            df_data = []
            for metric in agent_metrics:
                df_data.append({
                    "Agent": metric.get("agent_name", ""),
                    "Total Executions": metric.get("total_executions", 0),
                    "Successful": metric.get("successful_executions", 0),
                    "Failed": metric.get("failed_executions", 0),
                    "Avg Duration (ms)": f"{metric.get('avg_duration_ms', 0):.2f}",
                    "Last Executed": metric.get("last_executed", "")[:19]
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Agent success rates
            st.subheader("Success Rates by Agent")
            
            success_data = []
            for metric in agent_metrics:
                total = metric.get("total_executions", 1)
                successful = metric.get("successful_executions", 0)
                success_rate = (successful / total * 100) if total > 0 else 0
                
                success_data.append({
                    "Agent": metric.get("agent_name", ""),
                    "Success Rate (%)": success_rate
                })
            
            df_success = pd.DataFrame(success_data)
            st.bar_chart(df_success.set_index("Agent"))
        
        else:
            st.info("No agent metrics available yet")
    
    except Exception as e:
        st.error(f"Error loading agent metrics: {e}")

elif page == "System Health":
    # ========================================================================
    # System Health
    # ========================================================================
    
    st.subheader("🏥 System Health")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Database Health")
        try:
            audit_count = len(audit_manager.audit_db.all())
            workflow_count = len(audit_manager.workflow_db.all())
            metric_count = len(audit_manager.metrics_db.all())
            
            st.metric("Audit Entries", audit_count)
            st.metric("Workflows", workflow_count)
            st.metric("Metrics", metric_count)
            
            st.success("✅ Databases OK")
        except Exception as e:
            st.error(f"Database error: {e}")
    
    with col2:
        st.subheader("Recent Activity")
        try:
            stats = audit_manager.get_statistics()
            recent_errors = audit_manager.get_recent_errors(hours=1, limit=10)
            
            st.metric("Workflows Today", stats["total_workflows"])
            st.metric("Errors (1h)", len(recent_errors))
            st.metric("Success Rate", f"{stats['success_rate']:.1f}%")
        except Exception as e:
            st.error(f"Error loading stats: {e}")
    
    with col3:
        st.subheader("Maintenance")
        
        if st.button("🗑️ Clean Old Data (>30 days)"):
            try:
                audit_manager.clear_old_data(days=30)
                st.success("Cleaned old data successfully!")
            except Exception as e:
                st.error(f"Clean failed: {e}")
        
        if st.button("📤 Export All Data"):
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                export_path = f"audit_export_{timestamp}.json"
                audit_manager.export_data(export_path)
                st.success(f"Exported to {export_path}")
            except Exception as e:
                st.error(f"Export failed: {e}")

# Footer
st.divider()
st.caption("LangGraph Workflow Monitor with TinyDB Audit System | Admin Interface")
