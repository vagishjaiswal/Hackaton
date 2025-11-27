# Workflow Integration Guide

This guide explains how to integrate the dual UI system with your existing LangGraph workflow to add real-time monitoring and progress tracking.

## Overview

The integration adds monitoring hooks to your workflow so the Admin UI can display real-time progress. The End User UI handles input/output, while the Admin UI shows what's happening inside the workflow.

## Integration Steps

### Step 1: Enhanced Workflow with Progress Tracking

Modify your workflow nodes to report progress to the state manager. Here's how to update your `langgraph_interview_workflow.py`:

```python
# At the top of your workflow file
from pathlib import Path
import sys

# Import state manager
ui_path = Path(__file__).parent.parent.parent / "ui"
sys.path.insert(0, str(ui_path))
from workflow_state_manager import WorkflowStateManager

# Initialize state manager (use as global or pass through state)
state_manager = WorkflowStateManager()


def fetch_user_profile(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node 1: Fetch user profile from CSV"""
    execution_id = state.get("execution_id")
    
    # Log start
    if execution_id:
        state_manager.add_log(execution_id, "Fetching user profile...")
        state_manager.update_execution(
            execution_id,
            status="running",
            current_step="Fetch User Profile",
            steps_completed=0
        )
    
    logger.info("Step 1: Fetching user profile...")
    
    try:
        # Your existing logic here...
        user_id = state.get("user_id")
        # ... fetch user ...
        
        # Log success
        if execution_id:
            state_manager.add_log(
                execution_id,
                f"✓ Found user: {user_profile.get('name', 'Unknown')}",
                "SUCCESS"
            )
            state_manager.update_execution(
                execution_id,
                steps_completed=1
            )
        
        return {
            **state,
            "user_profile": user_profile,
            # ... rest of your return ...
        }
    
    except Exception as e:
        # Log error
        if execution_id:
            state_manager.add_log(
                execution_id,
                f"Error fetching user: {str(e)}",
                "ERROR"
            )
        
        logger.error(f"Error fetching user profile: {e}")
        return {**state, "status": "error", "error": str(e)}
```

### Step 2: Add Progress Tracking to All Nodes

Apply the same pattern to all your workflow nodes:

```python
def validate_user_profile(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node 2: Validate user profile"""
    execution_id = state.get("execution_id")
    
    if execution_id:
        state_manager.add_log(execution_id, "Validating user profile...")
        state_manager.update_execution(
            execution_id,
            current_step="Validate Profile",
            steps_completed=1
        )
    
    # ... your validation logic ...
    
    if execution_id:
        state_manager.add_log(execution_id, "✓ Profile validated", "SUCCESS")
        state_manager.update_execution(execution_id, steps_completed=2)
    
    return updated_state


def build_prompt(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node 3: Build prompt"""
    execution_id = state.get("execution_id")
    
    if execution_id:
        state_manager.add_log(execution_id, "Building question generation prompt...")
        state_manager.update_execution(
            execution_id,
            current_step="Build Prompt",
            steps_completed=2
        )
    
    # ... your prompt building logic ...
    
    if execution_id:
        state_manager.add_log(execution_id, f"✓ Prompt built ({len(prompt)} chars)", "SUCCESS")
        state_manager.update_execution(execution_id, steps_completed=3)
    
    return updated_state


def generate_questions(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node 4: Generate questions"""
    execution_id = state.get("execution_id")
    
    if execution_id:
        state_manager.add_log(execution_id, "Calling LLM to generate questions...")
        state_manager.update_execution(
            execution_id,
            current_step="Generate Questions",
            steps_completed=3
        )
    
    # ... your LLM call ...
    
    if execution_id:
        state_manager.add_log(execution_id, "✓ LLM response received", "SUCCESS")
        state_manager.update_execution(execution_id, steps_completed=4)
    
    return updated_state


def parse_response(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node 5: Parse response"""
    execution_id = state.get("execution_id")
    
    if execution_id:
        state_manager.add_log(execution_id, "Parsing LLM response...")
        state_manager.update_execution(
            execution_id,
            current_step="Parse Response",
            steps_completed=4
        )
    
    # ... your parsing logic ...
    
    if execution_id:
        state_manager.add_log(
            execution_id,
            f"✓ Parsed {len(questions)} questions",
            "SUCCESS"
        )
        state_manager.update_execution(execution_id, steps_completed=5)
    
    return updated_state


def format_output(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node 6: Format output"""
    execution_id = state.get("execution_id")
    
    if execution_id:
        state_manager.add_log(execution_id, "Formatting final output...")
        state_manager.update_execution(
            execution_id,
            current_step="Format Output",
            steps_completed=5
        )
    
    # ... your formatting logic ...
    
    if execution_id:
        if error:
            state_manager.add_log(execution_id, f"Workflow failed: {error}", "ERROR")
        else:
            state_manager.add_log(execution_id, "✓ Workflow completed successfully!", "SUCCESS")
        
        state_manager.update_execution(
            execution_id,
            steps_completed=6,
            current_step="Completed"
        )
    
    return updated_state
```

### Step 3: Create Monitored Workflow Wrapper

Create a wrapper function that initializes execution tracking:

```python
def run_monitored_workflow(
    user_id: Optional[int] = None,
    user_name: Optional[str] = None,
    csv_file: str = "test-agent.csv",
    data_dir: str = "../../data/input",
    num_questions: int = 5,
    llm_provider: str = "ollama",
    llm_model: str = "llama3.2",
    execution_id: Optional[str] = None
):
    """
    Run workflow with monitoring
    
    This wrapper adds execution tracking for the dual UI system.
    """
    
    # Create workflow
    workflow = create_interview_workflow(llm_provider, llm_model)
    
    # Prepare initial state with execution_id
    initial_state = {
        "execution_id": execution_id,  # Pass through for tracking
        "user_id": user_id,
        "user_name": user_name,
        "csv_file": csv_file,
        "data_dir": data_dir,
        "num_questions": num_questions,
        "llm_provider": llm_provider,
        "llm_model": llm_model,
    }
    
    try:
        # Execute workflow
        result = workflow.invoke(initial_state)
        return result
    
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        if execution_id:
            state_manager.add_log(execution_id, f"Fatal error: {str(e)}", "ERROR")
            state_manager.update_execution(
                execution_id,
                status="error",
                error=str(e)
            )
        raise
```

### Step 4: Update User UI to Pass Execution ID

The user UI already passes the execution_id, but ensure your workflow receives it:

```python
# In user_interface_ui.py (already done)
initial_state = {
    "execution_id": execution_id,  # This is crucial!
    "user_id": user_id,
    # ... other params ...
}

result = workflow.invoke(initial_state)
```

## Alternative: Non-Intrusive Integration

If you don't want to modify your workflow code, create a monitoring wrapper:

```python
# monitor_wrapper.py
from functools import wraps
from workflow_state_manager import WorkflowStateManager

state_manager = WorkflowStateManager()

def monitor_node(step_name: str, step_number: int):
    """Decorator to add monitoring to workflow nodes"""
    def decorator(func):
        @wraps(func)
        def wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
            execution_id = state.get("execution_id")
            
            # Log start
            if execution_id:
                state_manager.add_log(execution_id, f"Starting: {step_name}")
                state_manager.update_execution(
                    execution_id,
                    current_step=step_name,
                    steps_completed=step_number - 1
                )
            
            try:
                # Execute original function
                result = func(state)
                
                # Log success
                if execution_id:
                    state_manager.add_log(
                        execution_id,
                        f"✓ Completed: {step_name}",
                        "SUCCESS"
                    )
                    state_manager.update_execution(
                        execution_id,
                        steps_completed=step_number
                    )
                
                return result
            
            except Exception as e:
                # Log error
                if execution_id:
                    state_manager.add_log(
                        execution_id,
                        f"Error in {step_name}: {str(e)}",
                        "ERROR"
                    )
                raise
        
        return wrapper
    return decorator


# Usage: Decorate your existing functions
@monitor_node("Fetch User Profile", 1)
def fetch_user_profile(state: Dict[str, Any]) -> Dict[str, Any]:
    # Your existing code unchanged
    pass

@monitor_node("Validate Profile", 2)
def validate_user_profile(state: Dict[str, Any]) -> Dict[str, Any]:
    # Your existing code unchanged
    pass

# ... and so on for all nodes
```

## Testing the Integration

### 1. Test Basic Connectivity

```python
# test_integration.py
from workflow_state_manager import WorkflowStateManager

# Initialize
sm = WorkflowStateManager()

# Create test execution
exec_id = sm.create_execution(
    user_input={"test": "data"},
    total_steps=6
)

print(f"Created execution: {exec_id}")

# Simulate progress
import time
for i in range(6):
    sm.update_execution(
        exec_id,
        current_step=f"Step {i+1}",
        steps_completed=i
    )
    sm.add_log(exec_id, f"Completed step {i+1}")
    time.sleep(1)

# Complete
sm.update_execution(
    exec_id,
    status="completed",
    steps_completed=6,
    result={"test": "result"}
)

print("Test completed!")
```

### 2. Run Full Integration Test

```bash
# Terminal 1: Start Admin UI
cd ui
streamlit run admin_monitor_ui.py --server.port 8501

# Terminal 2: Start User UI  
cd ui
streamlit run user_interface_ui.py --server.port 8502

# Terminal 3: Run test
python test_integration.py
```

Watch the Admin UI - you should see:
- Execution appear
- Progress bar move
- Logs appear in real-time
- Status update to "completed"

## Customization Options

### Add Custom Metrics

```python
# In your workflow nodes
if execution_id:
    state_manager.add_log(
        execution_id,
        f"LLM tokens used: {token_count}",
        "INFO"
    )
```

### Add Conditional Logging

```python
# Only log important events
if execution_id and user_profile:
    state_manager.add_log(
        execution_id,
        f"Processing user: {user_profile['name']} "
        f"({user_profile['experience_years']} years exp)",
        "INFO"
    )
```

### Add Error Context

```python
except Exception as e:
    if execution_id:
        state_manager.add_log(
            execution_id,
            f"Error in {node_name}: {str(e)}\n"
            f"Context: {json.dumps(error_context, indent=2)}",
            "ERROR"
        )
```

## Performance Considerations

1. **File I/O**: State manager uses file-based storage. For high-frequency workflows, consider:
   - Batching updates
   - Using in-memory cache
   - Switching to database backend

2. **Logging**: Don't log in tight loops:
   ```python
   # Bad - logs 1000 times
   for item in items:
       if execution_id:
           state_manager.add_log(execution_id, f"Processing {item}")
   
   # Good - logs once
   if execution_id:
       state_manager.add_log(
           execution_id,
           f"Processing {len(items)} items"
       )
   ```

3. **State Updates**: Minimize update frequency:
   ```python
   # Only update on significant progress
   if i % 10 == 0 and execution_id:
       state_manager.update_execution(...)
   ```

## Troubleshooting

### Logs Not Appearing in Admin UI

**Check:**
1. execution_id is being passed correctly
2. State manager is using same state directory
3. File permissions are correct
4. Auto-refresh is enabled in Admin UI

### Progress Not Updating

**Check:**
1. `steps_completed` is incrementing
2. `update_execution()` is being called
3. No exceptions in workflow
4. Check Admin UI logs tab

### Multiple Executions Interfering

**Solution:** Each execution has unique ID, but only one "current" execution is shown. Clear old executions:
```python
state_manager.clear_current_execution()
```

## Next Steps

1. ✅ Add monitoring to your workflow nodes
2. ✅ Test with a simple execution
3. ✅ Verify logs appear in Admin UI
4. ✅ Test error handling
5. ✅ Customize logging as needed
6. ✅ Deploy both UIs

---

Your workflow is now fully integrated with the dual UI system! 🎉
