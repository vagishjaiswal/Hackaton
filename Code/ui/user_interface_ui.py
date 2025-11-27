"""
End User UI for LangGraph Workflow
Run with: 
    cd Code
    streamlit run ui/user_interface_ui.py --server.port 8502
"""

import streamlit as st
import sys
import time
import asyncio
from pathlib import Path
import json
import os

# Add project root to path - use absolute path to Code directory
# __file__ should be: .../Code/ui/user_interface_ui.py
try:
    code_dir = Path(__file__).parent.parent.resolve()
except:
    # Fallback if __file__ is not available
    code_dir = Path(os.getcwd()).resolve()

if str(code_dir) not in sys.path:
    sys.path.insert(0, str(code_dir))

from workflow_state_manager import WorkflowStateManager, WorkflowStatus
from src.workflow.langgraph_interview_workflow import create_interview_workflow

# Page configuration
st.set_page_config(
    page_title="Interview Question Generator",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #059669 0%, #10b981 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .input-section {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    .result-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #10b981;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .question-card {
        background: #f8fafc;
        padding: 1.25rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border: 1px solid #e2e8f0;
    }
    .question-number {
        display: inline-block;
        background: #10b981;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    .badge-technical { background: #dbeafe; color: #1e40af; }
    .badge-behavioral { background: #fef3c7; color: #92400e; }
    .badge-problem { background: #fce7f3; color: #9f1239; }
    .badge-junior { background: #f3f4f6; color: #1f2937; }
    .badge-mid { background: #fed7aa; color: #9a3412; }
    .badge-senior { background: #ddd6fe; color: #5b21b6; }
</style>
""", unsafe_allow_html=True)

# Initialize state manager
@st.cache_resource
def get_state_manager():
    return WorkflowStateManager()

state_manager = get_state_manager()

# Session state initialization
if 'execution_id' not in st.session_state:
    st.session_state.execution_id = None
if 'workflow_running' not in st.session_state:
    st.session_state.workflow_running = False
if 'result' not in st.session_state:
    st.session_state.result = None

# Header
st.markdown("""
<div class="main-header">
    <h1>💼 AI Interview Question Generator</h1>
    <p>Generate personalized interview questions based on candidate profiles</p>
</div>
""", unsafe_allow_html=True)

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.subheader("📝 Candidate Information")
    
    # Input method
    input_method = st.radio(
        "Select input method:",
        ["User ID", "User Name"],
        horizontal=True
    )
    
    if input_method == "User ID":
        user_id = st.number_input("Enter User ID:", min_value=1, value=1, step=1)
        user_name = None
    else:
        user_name = st.text_input("Enter User Name:")
        user_id = None
    
    # CSV file selection
    # Path should be relative to Code directory (since UI is in Code/ui/)
    data_dir = Path(__file__).parent.parent / "data" / "input"
    csv_files = list(data_dir.glob("*.csv")) if data_dir.exists() else []
    
    if csv_files:
        csv_file_names = [f.name for f in csv_files]
        selected_csv = st.selectbox("Select CSV file:", csv_file_names)
    else:
        st.warning("No CSV files found in data/input/")
        selected_csv = "test-agent.csv"
    
    # Number of questions
    num_questions = st.slider(
        "Number of questions to generate:",
        min_value=1,
        max_value=10,
        value=5
    )
    
    # LLM configuration
    with st.expander("⚙️ Advanced Settings"):
        llm_provider = st.selectbox("LLM Provider:", ["ollama", "openai"])
        llm_model = st.text_input("Model Name:", value="llama3.2" if llm_provider == "ollama" else "gpt-4")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Generate button
    if st.button("🚀 Generate Interview Questions", use_container_width=True, type="primary", disabled=st.session_state.workflow_running):
        if (input_method == "User ID" and user_id) or (input_method == "User Name" and user_name):
            st.session_state.workflow_running = True
            st.session_state.result = None
            
            # Create execution
            user_input = {
                "user_id": user_id,
                "user_name": user_name,
                "csv_file": selected_csv,
                "num_questions": num_questions,
                "llm_provider": llm_provider,
                "llm_model": llm_model
            }
            
            execution_id = state_manager.create_execution(user_input, total_steps=6)
            st.session_state.execution_id = execution_id
            
            with st.spinner("🔄 Generating questions... Please wait"):
                try:
                    # Update status
                    state_manager.update_execution(execution_id, status=WorkflowStatus.RUNNING.value)
                    state_manager.add_log(execution_id, "Workflow started")
                    
                    # Create and run workflow
                    workflow = create_interview_workflow(
                        llm_provider=llm_provider,
                        llm_model=llm_model
                    )
                    
                    initial_state = {
                        "user_id": user_id,
                        "user_name": user_name,
                        "csv_file": selected_csv,
                        "data_dir": "data/input",  # Relative path from Code directory
                        "num_questions": num_questions,
                        "llm_provider": llm_provider,
                        "llm_model": llm_model,
                    }
                    
                    # Execute workflow and track progress
                    state_manager.add_log(execution_id, "Executing workflow...")
                    result = workflow.invoke(initial_state)
                    
                    # Update state based on result
                    if result.get("final_output"):
                        output = result["final_output"]
                        
                        if output.get("status") == "success":
                            state_manager.update_execution(
                                execution_id,
                                status=WorkflowStatus.COMPLETED.value,
                                steps_completed=6,
                                current_step="Completed",
                                result=output
                            )
                            state_manager.add_log(execution_id, "Workflow completed successfully", "SUCCESS")
                            st.session_state.result = output
                        else:
                            error = output.get("error", "Unknown error")
                            state_manager.update_execution(
                                execution_id,
                                status=WorkflowStatus.ERROR.value,
                                error=error
                            )
                            state_manager.add_log(execution_id, f"Error: {error}", "ERROR")
                            st.error(f"❌ Error: {error}")
                    else:
                        state_manager.update_execution(
                            execution_id,
                            status=WorkflowStatus.ERROR.value,
                            error="No output produced"
                        )
                        state_manager.add_log(execution_id, "No output produced", "ERROR")
                        st.error("❌ Workflow failed to produce output")
                    
                except Exception as e:
                    state_manager.update_execution(
                        execution_id,
                        status=WorkflowStatus.ERROR.value,
                        error=str(e)
                    )
                    state_manager.add_log(execution_id, f"Exception: {str(e)}", "ERROR")
                    st.error(f"❌ Error: {str(e)}")
                
                finally:
                    st.session_state.workflow_running = False
                    st.rerun()
        else:
            st.warning("⚠️ Please enter a User ID or User Name")

with col2:
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.subheader("📊 Results")
    
    if st.session_state.workflow_running:
        st.info("🔄 Workflow is running... Check the Admin Monitor UI for real-time progress")
        
        # Show simple progress
        with st.spinner("Processing..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(100):
                time.sleep(0.05)
                progress_bar.progress(i + 1)
                status_text.text(f"Processing: {i + 1}%")
    
    elif st.session_state.result:
        result = st.session_state.result
        
        if result.get("status") == "success":
            # Success message
            st.success("✅ Interview questions generated successfully!")
            
            # Candidate info
            user_profile = result.get("user_profile", {})
            if user_profile:
                st.markdown(f"""
                <div class="result-card">
                    <h4>👤 Candidate Profile</h4>
                    <p><strong>Name:</strong> {user_profile.get('name', 'N/A')}</p>
                    <p><strong>Role:</strong> {user_profile.get('job_role', 'N/A')}</p>
                    <p><strong>Experience:</strong> {user_profile.get('experience_years', 'N/A')} years</p>
                    <p><strong>Skills:</strong> {user_profile.get('skills', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Questions
            questions = result.get("interview_questions", [])
            if questions:
                st.markdown(f"### 💡 {len(questions)} Interview Questions Generated")
                
                for idx, q in enumerate(questions, 1):
                    category = q.get("category", "general")
                    difficulty = q.get("difficulty", "mid")
                    
                    category_class = f"badge-{category[:8]}"  # technical, behavioral, problem
                    difficulty_class = f"badge-{difficulty}"
                    
                    st.markdown(f"""
                    <div class="question-card">
                        <div class="question-number">Question {idx}</div>
                        <h4>{q.get('question', 'No question text')}</h4>
                        <div style="margin-top: 0.75rem;">
                            <span class="badge {category_class}">{category.upper()}</span>
                            <span class="badge {difficulty_class}">{difficulty.upper()}</span>
                        </div>
                        <p style="margin-top: 0.75rem; color: #64748b; font-size: 0.875rem;">
                            <strong>Rationale:</strong> {q.get('rationale', 'N/A')}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Download button
                st.download_button(
                    label="📥 Download Questions (JSON)",
                    data=json.dumps(result, indent=2),
                    file_name=f"interview_questions_{st.session_state.execution_id}.json",
                    mime="application/json",
                    use_container_width=True
                )
        else:
            st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    else:
        st.info("👈 Enter candidate information and click 'Generate Interview Questions' to start")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("💼 Interview Question Generator")
with col2:
    if st.session_state.execution_id:
        st.caption(f"Execution ID: {st.session_state.execution_id}")
with col3:
    st.caption("Powered by LangGraph")
