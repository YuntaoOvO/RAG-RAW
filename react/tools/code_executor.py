"""
Code Executor Tool
==================

Tool for safely executing Python code in a subprocess.
"""

import os
import sys
import subprocess
import tempfile
import json
from typing import Dict, Any, Optional
from datetime import datetime

from ..config import (
    BASE_DIR,
    CODE_EXECUTION_TIMEOUT,
    MAX_OUTPUT_SIZE,
    PYTHIA_SCRIPTS_DIR,
    PYTHIA_RESULTS_DIR,
    ALLOWED_IMPORTS,
    get_timestamp
)


class CodeExecutorTool:
    """
    Tool for executing Python code safely in a subprocess.
    
    Features:
    - Subprocess isolation
    - Timeout protection
    - Output capture
    - Error handling
    """
    
    name = "code_executor"
    description = """Execute Python code in a safe subprocess.
    Input: Python code as a string.
    The code runs with a timeout and output is captured.
    Returns stdout, stderr, and exit code."""
    
    def __init__(self, 
                 timeout: int = CODE_EXECUTION_TIMEOUT,
                 working_dir: str = PYTHIA_SCRIPTS_DIR,
                 python_path: str = None):
        self.timeout = timeout
        self.working_dir = working_dir
        self.python_path = python_path or sys.executable
        
        # Ensure working directory exists
        os.makedirs(self.working_dir, exist_ok=True)
    
    def run(self, code: str, save_script: bool = True, 
            script_name: str = None) -> Dict[str, Any]:
        """
        Execute Python code in a subprocess.
        
        Args:
            code: Python code to execute
            save_script: Whether to save the script to disk
            script_name: Name for the saved script
            
        Returns:
            Dict with 'success', 'stdout', 'stderr', 'exit_code'
        """
        # Generate script name if not provided
        if script_name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            script_name = f"script_{timestamp}.py"
        
        if not script_name.endswith('.py'):
            script_name += '.py'
        
        script_path = os.path.join(self.working_dir, script_name)
        
        try:
            # Write script to file
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Execute in subprocess
            result = subprocess.run(
                [self.python_path, script_path],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=self.working_dir,
                env=self._get_env()
            )
            
            stdout = result.stdout
            stderr = result.stderr
            
            # Truncate if too long
            if len(stdout) > MAX_OUTPUT_SIZE:
                stdout = stdout[:MAX_OUTPUT_SIZE] + "\n... [output truncated]"
            if len(stderr) > MAX_OUTPUT_SIZE:
                stderr = stderr[:MAX_OUTPUT_SIZE] + "\n... [error truncated]"
            
            return {
                'success': result.returncode == 0,
                'stdout': stdout,
                'stderr': stderr,
                'exit_code': result.returncode,
                'script_path': script_path if save_script else None
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f"Execution timed out after {self.timeout} seconds",
                'stdout': '',
                'stderr': '',
                'exit_code': -1,
                'script_path': script_path if save_script else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Execution failed: {str(e)}",
                'stdout': '',
                'stderr': str(e),
                'exit_code': -1
            }
        finally:
            # Clean up if not saving
            if not save_script and os.path.exists(script_path):
                try:
                    os.remove(script_path)
                except:
                    pass
    
    def _get_env(self) -> Dict[str, str]:
        """Get environment variables for subprocess."""
        env = os.environ.copy()
        # Add any necessary paths
        pythonpath = env.get('PYTHONPATH', '')
        if self.working_dir not in pythonpath:
            env['PYTHONPATH'] = f"{self.working_dir}:{pythonpath}"
        return env
    
    def run_script(self, script_path: str) -> Dict[str, Any]:
        """
        Execute an existing Python script.
        
        Args:
            script_path: Path to the script
            
        Returns:
            Dict with execution results
        """
        if not os.path.isabs(script_path):
            script_path = os.path.join(self.working_dir, script_path)
        
        if not os.path.exists(script_path):
            return {
                'success': False,
                'error': f"Script not found: {script_path}"
            }
        
        try:
            result = subprocess.run(
                [self.python_path, script_path],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=os.path.dirname(script_path),
                env=self._get_env()
            )
            
            stdout = result.stdout
            stderr = result.stderr
            
            if len(stdout) > MAX_OUTPUT_SIZE:
                stdout = stdout[:MAX_OUTPUT_SIZE] + "\n... [output truncated]"
            if len(stderr) > MAX_OUTPUT_SIZE:
                stderr = stderr[:MAX_OUTPUT_SIZE] + "\n... [error truncated]"
            
            return {
                'success': result.returncode == 0,
                'stdout': stdout,
                'stderr': stderr,
                'exit_code': result.returncode,
                'script_path': script_path
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f"Execution timed out after {self.timeout} seconds",
                'script_path': script_path
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Execution failed: {str(e)}"
            }
    
    def run_with_args(self, script_path: str, args: list) -> Dict[str, Any]:
        """
        Execute a script with command line arguments.
        
        Args:
            script_path: Path to the script
            args: List of command line arguments
            
        Returns:
            Dict with execution results
        """
        if not os.path.isabs(script_path):
            script_path = os.path.join(self.working_dir, script_path)
        
        if not os.path.exists(script_path):
            return {
                'success': False,
                'error': f"Script not found: {script_path}"
            }
        
        try:
            cmd = [self.python_path, script_path] + [str(a) for a in args]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=os.path.dirname(script_path),
                env=self._get_env()
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout[:MAX_OUTPUT_SIZE],
                'stderr': result.stderr[:MAX_OUTPUT_SIZE],
                'exit_code': result.returncode,
                'command': ' '.join(cmd)
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f"Execution timed out after {self.timeout} seconds"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Execution failed: {str(e)}"
            }
    
    def check_syntax(self, code: str) -> Dict[str, Any]:
        """
        Check Python code syntax without executing.
        
        Args:
            code: Python code to check
            
        Returns:
            Dict with 'valid' and 'error' if any
        """
        try:
            compile(code, '<string>', 'exec')
            return {
                'valid': True,
                'success': True
            }
        except SyntaxError as e:
            return {
                'valid': False,
                'success': False,
                'error': f"Syntax error at line {e.lineno}: {e.msg}",
                'line': e.lineno,
                'offset': e.offset
            }
    
    def list_scripts(self) -> Dict[str, Any]:
        """
        List all scripts in the working directory.
        
        Returns:
            Dict with list of scripts
        """
        try:
            scripts = []
            for f in os.listdir(self.working_dir):
                if f.endswith('.py'):
                    path = os.path.join(self.working_dir, f)
                    scripts.append({
                        'name': f,
                        'path': path,
                        'size': os.path.getsize(path),
                        'modified': datetime.fromtimestamp(
                            os.path.getmtime(path)
                        ).isoformat()
                    })
            
            return {
                'success': True,
                'scripts': scripts,
                'count': len(scripts)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to list scripts: {str(e)}"
            }


# Tool function for agent registration
def create_code_executor_tool(working_dir: str = PYTHIA_SCRIPTS_DIR) -> Dict[str, Any]:
    """Create a code executor tool instance for agent registration."""
    tool = CodeExecutorTool(working_dir=working_dir)
    return {
        'name': tool.name,
        'description': tool.description,
        'function': tool.run,
        'instance': tool
    }

