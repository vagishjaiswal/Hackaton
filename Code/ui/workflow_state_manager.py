"""
Workflow State Manager
Shared state management between Admin and User UIs
"""

import json
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum


class WorkflowStatus(Enum):
    """Workflow execution status"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class WorkflowExecution:
    """Track a workflow execution"""
    execution_id: str
    user_input: Dict[str, Any]
    status: str
    current_step: str
    steps_completed: int
    total_steps: int
    start_time: str
    end_time: Optional[str] = None
    error: Optional[str] = None
    logs: List[str] = None
    result: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.logs is None:
            self.logs = []


class WorkflowStateManager:
    """
    Manages workflow state across multiple UI instances
    Uses file-based persistence for simplicity
    """
    
    def __init__(self, state_dir: str = "workflow_state"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(exist_ok=True)
        
        self.executions_file = self.state_dir / "executions.json"
        self.current_execution_file = self.state_dir / "current_execution.json"
        
        self._lock = threading.Lock()
        self._initialize_state()
    
    def _initialize_state(self):
        """Initialize state files if they don't exist"""
        if not self.executions_file.exists():
            self._write_json(self.executions_file, {"executions": []})
        
        if not self.current_execution_file.exists():
            self._write_json(self.current_execution_file, {})
    
    def _read_json(self, file_path: Path) -> Dict:
        """Read JSON file with error handling"""
        try:
            if not file_path.exists():
                return {}
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return {}
    
    def _write_json(self, file_path: Path, data: Dict):
        """Write JSON file with error handling"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error writing {file_path}: {e}")
    
    def create_execution(self, user_input: Dict[str, Any], total_steps: int = 6) -> str:
        """Create a new workflow execution"""
        with self._lock:
            execution_id = f"exec_{int(time.time() * 1000)}"
            
            execution = WorkflowExecution(
                execution_id=execution_id,
                user_input=user_input,
                status=WorkflowStatus.IDLE.value,
                current_step="Initializing",
                steps_completed=0,
                total_steps=total_steps,
                start_time=datetime.now().isoformat(),
                logs=[]
            )
            
            # Save current execution
            self._write_json(self.current_execution_file, asdict(execution))
            
            # Add to executions history
            data = self._read_json(self.executions_file)
            if "executions" not in data:
                data["executions"] = []
            data["executions"].append(asdict(execution))
            self._write_json(self.executions_file, data)
            
            return execution_id
    
    def get_current_execution(self) -> Optional[Dict[str, Any]]:
        """Get current workflow execution"""
        with self._lock:
            data = self._read_json(self.current_execution_file)
            return data if data else None
    
    def update_execution(
        self,
        execution_id: str,
        status: Optional[str] = None,
        current_step: Optional[str] = None,
        steps_completed: Optional[int] = None,
        error: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None
    ):
        """Update execution state"""
        with self._lock:
            data = self._read_json(self.current_execution_file)
            
            if not data or data.get("execution_id") != execution_id:
                return
            
            if status:
                data["status"] = status
            if current_step:
                data["current_step"] = current_step
            if steps_completed is not None:
                data["steps_completed"] = steps_completed
            if error:
                data["error"] = error
                data["status"] = WorkflowStatus.ERROR.value
            if result:
                data["result"] = result
            
            if status == WorkflowStatus.COMPLETED.value or status == WorkflowStatus.ERROR.value:
                data["end_time"] = datetime.now().isoformat()
            
            self._write_json(self.current_execution_file, data)
            
            # Update in history
            history_data = self._read_json(self.executions_file)
            if "executions" not in history_data:
                history_data["executions"] = []
            for i, exec_data in enumerate(history_data["executions"]):
                if exec_data["execution_id"] == execution_id:
                    history_data["executions"][i] = data
                    break
            self._write_json(self.executions_file, history_data)
    
    def add_log(self, execution_id: str, message: str, level: str = "INFO"):
        """Add log message to execution"""
        with self._lock:
            data = self._read_json(self.current_execution_file)
            
            if not data or data.get("execution_id") != execution_id:
                return
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] [{level}] {message}"
            
            if "logs" not in data:
                data["logs"] = []
            
            data["logs"].append(log_entry)
            
            # Keep only last 100 logs
            if len(data["logs"]) > 100:
                data["logs"] = data["logs"][-100:]
            
            self._write_json(self.current_execution_file, data)
    
    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get execution history"""
        with self._lock:
            data = self._read_json(self.executions_file)
            executions = data.get("executions", [])
            return executions[-limit:][::-1]  # Return most recent first
    
    def clear_current_execution(self):
        """Clear current execution"""
        with self._lock:
            self._write_json(self.current_execution_file, {})
    
    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        with self._lock:
            data = self._read_json(self.executions_file)
            executions = data.get("executions", [])
            
            total = len(executions)
            completed = sum(1 for e in executions if e["status"] == WorkflowStatus.COMPLETED.value)
            errors = sum(1 for e in executions if e["status"] == WorkflowStatus.ERROR.value)
            
            return {
                "total_executions": total,
                "completed": completed,
                "errors": errors,
                "success_rate": (completed / total * 100) if total > 0 else 0
            }
