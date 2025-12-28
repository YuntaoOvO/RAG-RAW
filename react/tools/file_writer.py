"""
File Writer Tool
================

Tool for writing/creating files (tex, py, txt, json, etc.)
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

from ..config import (
    BASE_DIR,
    WRITABLE_EXTENSIONS,
    OUTPUT_DIR,
    PYTHIA_SCRIPTS_DIR,
    PYTHIA_RESULTS_DIR,
    get_timestamp
)


class FileWriterTool:
    """
    Tool for writing files of various types.
    
    Supported formats: .tex, .py, .txt, .json, .md
    """
    
    name = "file_writer"
    description = """Write content to a file. 
    Supported formats: tex, py, txt, json, md.
    Creates parent directories if they don't exist.
    Input: file_path (str), content (str)
    Returns success status and file info."""
    
    def __init__(self, base_dir: str = BASE_DIR, allowed_dirs: list = None):
        self.base_dir = base_dir
        # Restrict writing to specific directories for safety
        self.allowed_dirs = allowed_dirs or [
            OUTPUT_DIR,
            PYTHIA_SCRIPTS_DIR,
            PYTHIA_RESULTS_DIR,
            os.path.join(BASE_DIR, 'pythia_workspace'),
        ]
    
    def _resolve_path(self, file_path: str) -> str:
        """Resolve relative paths to absolute paths."""
        if os.path.isabs(file_path):
            return file_path
        return os.path.join(self.base_dir, file_path)
    
    def _validate_path(self, file_path: str) -> tuple[bool, str]:
        """Validate file path for security."""
        abs_path = self._resolve_path(file_path)
        
        # Check file extension
        ext = os.path.splitext(abs_path)[1].lower()
        if ext not in WRITABLE_EXTENSIONS:
            return False, f"Unsupported file type: {ext}. Allowed: {WRITABLE_EXTENSIONS}"
        
        # Check if path is within allowed directories
        abs_path_normalized = os.path.normpath(abs_path)
        is_allowed = False
        for allowed_dir in self.allowed_dirs:
            allowed_normalized = os.path.normpath(allowed_dir)
            if abs_path_normalized.startswith(allowed_normalized):
                is_allowed = True
                break
        
        if not is_allowed:
            return False, f"Write not allowed in this directory. Allowed: {self.allowed_dirs}"
        
        return True, abs_path
    
    def run(self, file_path: str, content: str, overwrite: bool = True) -> Dict[str, Any]:
        """
        Write content to a file.
        
        Args:
            file_path: Path to the file (relative or absolute)
            content: Content to write
            overwrite: Whether to overwrite existing file
            
        Returns:
            Dict with 'success', 'file_path' or 'error' keys
        """
        valid, result = self._validate_path(file_path)
        
        if not valid:
            return {
                'success': False,
                'error': result
            }
        
        abs_path = result
        
        # Check if file exists and overwrite is False
        if os.path.exists(abs_path) and not overwrite:
            return {
                'success': False,
                'error': f"File exists and overwrite=False: {file_path}"
            }
        
        try:
            # Create parent directories if needed
            parent_dir = os.path.dirname(abs_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            
            # Write file
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                'success': True,
                'file_path': abs_path,
                'size': len(content),
                'lines': content.count('\n') + 1
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to write file: {str(e)}"
            }
    
    def append(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Append content to a file.
        
        Args:
            file_path: Path to the file
            content: Content to append
            
        Returns:
            Dict with 'success' or 'error'
        """
        valid, result = self._validate_path(file_path)
        
        if not valid:
            return {
                'success': False,
                'error': result
            }
        
        abs_path = result
        
        try:
            with open(abs_path, 'a', encoding='utf-8') as f:
                f.write(content)
            
            return {
                'success': True,
                'file_path': abs_path,
                'appended_size': len(content)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to append to file: {str(e)}"
            }
    
    def write_python_script(self, script_name: str, code: str, 
                           add_header: bool = True) -> Dict[str, Any]:
        """
        Write a Python script to the Pythia scripts directory.
        
        Args:
            script_name: Name of the script (without path)
            code: Python code to write
            add_header: Whether to add a timestamp header
            
        Returns:
            Dict with 'success' and 'file_path' or 'error'
        """
        if not script_name.endswith('.py'):
            script_name += '.py'
        
        file_path = os.path.join(PYTHIA_SCRIPTS_DIR, script_name)
        
        if add_header:
            header = f'''"""
Auto-generated Pythia8 script
Generated: {datetime.now().isoformat()}
Timestamp: {get_timestamp()}
"""

'''
            code = header + code
        
        return self.run(file_path, code)
    
    def write_tex_article(self, article_name: str, content: str) -> Dict[str, Any]:
        """
        Write a LaTeX article to the output directory.
        
        Args:
            article_name: Name of the article file
            content: LaTeX content
            
        Returns:
            Dict with 'success' and 'file_path' or 'error'
        """
        if not article_name.endswith('.tex'):
            article_name += '.tex'
        
        file_path = os.path.join(OUTPUT_DIR, article_name)
        
        return self.run(file_path, content)
    
    def write_json(self, file_path: str, data: Any, indent: int = 2) -> Dict[str, Any]:
        """
        Write JSON data to a file.
        
        Args:
            file_path: Path to the file
            data: Data to serialize as JSON
            indent: JSON indentation level
            
        Returns:
            Dict with 'success' and 'file_path' or 'error'
        """
        try:
            content = json.dumps(data, indent=indent, ensure_ascii=False)
            return self.run(file_path, content)
        except (TypeError, ValueError) as e:
            return {
                'success': False,
                'error': f"Failed to serialize JSON: {str(e)}"
            }
    
    def write_results(self, result_name: str, data: Any) -> Dict[str, Any]:
        """
        Write analysis results to the results directory.
        
        Args:
            result_name: Name of the result file
            data: Data to write (dict or string)
            
        Returns:
            Dict with 'success' and 'file_path' or 'error'
        """
        if not result_name.endswith(('.json', '.txt')):
            result_name += '.json'
        
        file_path = os.path.join(PYTHIA_RESULTS_DIR, result_name)
        
        if isinstance(data, dict):
            return self.write_json(file_path, data)
        else:
            return self.run(file_path, str(data))


# Tool function for agent registration
def create_file_writer_tool(base_dir: str = BASE_DIR) -> Dict[str, Any]:
    """Create a file writer tool instance for agent registration."""
    tool = FileWriterTool(base_dir)
    return {
        'name': tool.name,
        'description': tool.description,
        'function': tool.run,
        'instance': tool
    }

