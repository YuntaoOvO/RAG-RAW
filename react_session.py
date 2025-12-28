"""
ReAct Session Manager
======================

Manages session logging, saving, and resuming for the ReAct agent.
Each session is saved as a JSON file for review and continuation.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


# Session directory
SESSIONS_DIR = '/home/yuntao/Mydata/output/react_sessions'


def ensure_sessions_dir():
    """Ensure the sessions directory exists."""
    os.makedirs(SESSIONS_DIR, exist_ok=True)


def generate_session_id() -> str:
    """Generate a unique session ID based on timestamp."""
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def get_session_path(session_id: str) -> str:
    """Get the file path for a session."""
    return os.path.join(SESSIONS_DIR, f'session_{session_id}.json')


class ReactSession:
    """
    Manages a ReAct agent session with step-by-step logging.
    
    Attributes:
        session_id: Unique identifier for the session
        task: The original task description
        steps: List of all steps taken
        status: Current status (in_progress, paused, completed)
        context: Conversation context for resumption
    """
    
    def __init__(self, session_id: str = None, task: str = None):
        self.session_id = session_id or generate_session_id()
        self.task = task or ""
        self.steps: List[Dict[str, Any]] = []
        self.status = "in_progress"
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.final_result: Optional[Dict[str, Any]] = None
        self.context: List[Dict[str, str]] = []  # Conversation history for resumption
        self.current_iteration = 0
        self.max_iterations = 15
        self.literature_file: Optional[str] = None
        self.total_runtime_seconds = 0  # Total runtime tracking
        self.last_run_start: Optional[str] = None  # For timing
        
        ensure_sessions_dir()
    
    def add_step(self, step_type: str, content: str, iteration: int = None, 
                 action_name: str = None, action_input: Dict = None):
        """
        Add a step to the session log.
        
        Args:
            step_type: Type of step (thought, action, observation, final_answer, error)
            content: The content of the step
            iteration: Current iteration number
            action_name: Name of the action (for action steps)
            action_input: Input parameters (for action steps)
        """
        step = {
            "iteration": iteration or self.current_iteration,
            "type": step_type,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        if action_name:
            step["action_name"] = action_name
        if action_input:
            step["action_input"] = action_input
        
        self.steps.append(step)
        self.updated_at = datetime.now().isoformat()
        self.current_iteration = iteration or self.current_iteration
        
        # Auto-save after each step
        self.save()
    
    def update_context(self, messages: List[Dict[str, str]]):
        """Update the conversation context for resumption."""
        self.context = messages
        self.save()
    
    def set_status(self, status: str):
        """Set the session status."""
        self.status = status
        self.updated_at = datetime.now().isoformat()
        self.save()
    
    def set_final_result(self, result: Dict[str, Any]):
        """Set the final result and mark as completed."""
        self.final_result = result
        self.status = "completed"
        self.updated_at = datetime.now().isoformat()
        self.save()
    
    def pause(self):
        """Pause the session for later resumption."""
        self.status = "paused"
        self.updated_at = datetime.now().isoformat()
        # Update runtime
        if self.last_run_start:
            start_time = datetime.fromisoformat(self.last_run_start)
            elapsed = (datetime.now() - start_time).total_seconds()
            self.total_runtime_seconds += int(elapsed)
            self.last_run_start = None
        self.save()
    
    def resume(self):
        """Resume a paused session."""
        self.status = "in_progress"
        self.last_run_start = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.save()
    
    def start_timer(self):
        """Start the run timer."""
        self.last_run_start = datetime.now().isoformat()
        self.save()
    
    def stop_timer(self):
        """Stop the timer and accumulate runtime."""
        if self.last_run_start:
            start_time = datetime.fromisoformat(self.last_run_start)
            elapsed = (datetime.now() - start_time).total_seconds()
            self.total_runtime_seconds += int(elapsed)
            self.last_run_start = None
        self.save()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "session_id": self.session_id,
            "task": self.task,
            "steps": self.steps,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "final_result": self.final_result,
            "context": self.context,
            "current_iteration": self.current_iteration,
            "max_iterations": self.max_iterations,
            "literature_file": self.literature_file,
            "step_count": len(self.steps),
            "total_runtime_seconds": self.total_runtime_seconds,
            "last_run_start": self.last_run_start
        }
    
    def save(self):
        """Save session to JSON file."""
        path = get_session_path(self.session_id)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, session_id: str) -> 'ReactSession':
        """Load a session from JSON file."""
        path = get_session_path(session_id)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Session not found: {session_id}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        session = cls(session_id=data['session_id'], task=data.get('task', ''))
        session.steps = data.get('steps', [])
        session.status = data.get('status', 'in_progress')
        session.created_at = data.get('created_at', datetime.now().isoformat())
        session.updated_at = data.get('updated_at', datetime.now().isoformat())
        session.final_result = data.get('final_result')
        session.context = data.get('context', [])
        session.current_iteration = data.get('current_iteration', 0)
        session.max_iterations = data.get('max_iterations', 15)
        session.literature_file = data.get('literature_file')
        session.total_runtime_seconds = data.get('total_runtime_seconds', 0)
        session.last_run_start = data.get('last_run_start')
        
        return session
    
    def get_steps_by_iteration(self) -> Dict[int, List[Dict[str, Any]]]:
        """Group steps by iteration number."""
        grouped = {}
        for step in self.steps:
            iteration = step.get('iteration', 0)
            if iteration not in grouped:
                grouped[iteration] = []
            grouped[iteration].append(step)
        return grouped
    
    def get_summary(self) -> str:
        """Get a brief summary of the session."""
        thought_count = len([s for s in self.steps if s['type'] == 'thought'])
        action_count = len([s for s in self.steps if s['type'] == 'action'])
        
        return f"Session {self.session_id}: {thought_count} thoughts, {action_count} actions, status={self.status}"


def list_sessions() -> List[Dict[str, Any]]:
    """List all available sessions."""
    ensure_sessions_dir()
    sessions = []
    
    for filename in os.listdir(SESSIONS_DIR):
        if filename.startswith('session_') and filename.endswith('.json'):
            try:
                path = os.path.join(SESSIONS_DIR, filename)
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                sessions.append({
                    'session_id': data.get('session_id'),
                    'status': data.get('status'),
                    'created_at': data.get('created_at'),
                    'step_count': data.get('step_count', len(data.get('steps', []))),
                    'task': data.get('task', '')[:100] + '...' if len(data.get('task', '')) > 100 else data.get('task', '')
                })
            except (json.JSONDecodeError, KeyError):
                continue
    
    # Sort by created_at, newest first
    sessions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return sessions


def get_latest_session() -> Optional[ReactSession]:
    """Get the most recent session."""
    sessions = list_sessions()
    if sessions:
        return ReactSession.load(sessions[0]['session_id'])
    return None


def get_pausable_sessions() -> List[Dict[str, Any]]:
    """Get sessions that can be resumed (paused or in_progress)."""
    sessions = list_sessions()
    return [s for s in sessions if s['status'] in ('paused', 'in_progress')]


# For testing
if __name__ == '__main__':
    # Create a test session
    session = ReactSession(task="Test task for particle physics research")
    session.add_step("thought", "I need to read the literature review", iteration=1)
    session.add_step("action", "read_file", iteration=1, 
                     action_name="read_file", 
                     action_input={"file_path": "./output/review.tex"})
    session.add_step("observation", "File content here...", iteration=1)
    
    print(f"Created session: {session.session_id}")
    print(f"Saved to: {get_session_path(session.session_id)}")
    print(f"Summary: {session.get_summary()}")
    
    # List sessions
    print("\nAll sessions:")
    for s in list_sessions():
        print(f"  - {s['session_id']}: {s['status']}, {s['step_count']} steps")

