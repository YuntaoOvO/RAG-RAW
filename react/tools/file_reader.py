"""
File Reader Tool
================

Tool for reading various file types (tex, py, txt, json, etc.)
"""

import os
import json
from typing import Dict, Any, Optional, List

from ..config import (
    BASE_DIR, 
    READABLE_EXTENSIONS, 
    MAX_FILE_SIZE,
    OUTPUT_DIR
)


class FileReaderTool:
    """
    Tool for reading files of various types.
    
    Supported formats: .tex, .py, .txt, .json, .md, .csv, .dat
    """
    
    name = "file_reader"
    description = """Read the contents of a file. 
    Supported formats: tex, py, txt, json, md, csv, dat.
    Input should be the file path (relative to workspace or absolute).
    Returns the file contents as a string."""
    
    def __init__(self, base_dir: str = BASE_DIR):
        self.base_dir = base_dir
    
    def _resolve_path(self, file_path: str) -> str:
        """Resolve relative paths to absolute paths."""
        if os.path.isabs(file_path):
            return file_path
        return os.path.join(self.base_dir, file_path)
    
    def _validate_path(self, file_path: str) -> tuple[bool, str]:
        """Validate file path for security and existence."""
        abs_path = self._resolve_path(file_path)
        
        # Check if file exists
        if not os.path.exists(abs_path):
            return False, f"File not found: {file_path}"
        
        # Check if it's a file
        if not os.path.isfile(abs_path):
            return False, f"Not a file: {file_path}"
        
        # Check file extension
        ext = os.path.splitext(abs_path)[1].lower()
        if ext not in READABLE_EXTENSIONS:
            return False, f"Unsupported file type: {ext}. Allowed: {READABLE_EXTENSIONS}"
        
        # Check file size
        size = os.path.getsize(abs_path)
        if size > MAX_FILE_SIZE:
            return False, f"File too large: {size} bytes (max: {MAX_FILE_SIZE})"
        
        return True, abs_path
    
    def run(self, file_path: str) -> Dict[str, Any]:
        """
        Read a file and return its contents.
        
        Args:
            file_path: Path to the file (relative or absolute)
            
        Returns:
            Dict with 'success', 'content' or 'error' keys
        """
        valid, result = self._validate_path(file_path)
        
        if not valid:
            return {
                'success': False,
                'error': result
            }
        
        abs_path = result
        
        try:
            # Determine encoding
            ext = os.path.splitext(abs_path)[1].lower()
            
            # Read file
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse JSON if applicable
            if ext == '.json':
                try:
                    parsed = json.loads(content)
                    return {
                        'success': True,
                        'content': content,
                        'parsed': parsed,
                        'file_path': abs_path,
                        'file_type': 'json'
                    }
                except json.JSONDecodeError:
                    pass
            
            return {
                'success': True,
                'content': content,
                'file_path': abs_path,
                'file_type': ext[1:],  # Remove dot
                'size': len(content)
            }
            
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(abs_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                return {
                    'success': True,
                    'content': content,
                    'file_path': abs_path,
                    'encoding': 'latin-1'
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Failed to read file with encoding: {str(e)}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to read file: {str(e)}"
            }
    
    def read_section(self, file_path: str, start_marker: str, end_marker: str) -> Dict[str, Any]:
        """
        Read a specific section of a file between markers.
        
        Args:
            file_path: Path to the file
            start_marker: String marking the start of the section
            end_marker: String marking the end of the section
            
        Returns:
            Dict with 'success' and 'content' or 'error'
        """
        result = self.run(file_path)
        
        if not result['success']:
            return result
        
        content = result['content']
        
        # Find section
        start_idx = content.find(start_marker)
        if start_idx == -1:
            return {
                'success': False,
                'error': f"Start marker not found: {start_marker}"
            }
        
        end_idx = content.find(end_marker, start_idx + len(start_marker))
        if end_idx == -1:
            return {
                'success': False,
                'error': f"End marker not found: {end_marker}"
            }
        
        section = content[start_idx + len(start_marker):end_idx]
        
        return {
            'success': True,
            'content': section.strip(),
            'start_pos': start_idx,
            'end_pos': end_idx
        }
    
    def read_lines(self, file_path: str, start_line: int = 1, end_line: int = None) -> Dict[str, Any]:
        """
        Read specific lines from a file.
        
        Args:
            file_path: Path to the file
            start_line: Starting line number (1-indexed)
            end_line: Ending line number (inclusive, None for end of file)
            
        Returns:
            Dict with 'success' and 'lines' or 'error'
        """
        result = self.run(file_path)
        
        if not result['success']:
            return result
        
        lines = result['content'].split('\n')
        total_lines = len(lines)
        
        # Adjust indices
        start_idx = max(0, start_line - 1)
        end_idx = total_lines if end_line is None else min(end_line, total_lines)
        
        selected_lines = lines[start_idx:end_idx]
        
        return {
            'success': True,
            'lines': selected_lines,
            'content': '\n'.join(selected_lines),
            'start_line': start_line,
            'end_line': end_idx,
            'total_lines': total_lines
        }
    
    def list_files(self, directory: str, extension: str = None) -> Dict[str, Any]:
        """
        List files in a directory.
        
        Args:
            directory: Directory path
            extension: Optional file extension filter
            
        Returns:
            Dict with 'success' and 'files' or 'error'
        """
        abs_dir = self._resolve_path(directory)
        
        if not os.path.exists(abs_dir):
            return {
                'success': False,
                'error': f"Directory not found: {directory}"
            }
        
        if not os.path.isdir(abs_dir):
            return {
                'success': False,
                'error': f"Not a directory: {directory}"
            }
        
        try:
            files = []
            for f in os.listdir(abs_dir):
                file_path = os.path.join(abs_dir, f)
                if os.path.isfile(file_path):
                    if extension is None or f.endswith(extension):
                        files.append({
                            'name': f,
                            'path': file_path,
                            'size': os.path.getsize(file_path)
                        })
            
            return {
                'success': True,
                'files': files,
                'count': len(files),
                'directory': abs_dir
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to list directory: {str(e)}"
            }


# Tool function for agent registration
def create_file_reader_tool(base_dir: str = BASE_DIR) -> Dict[str, Any]:
    """Create a file reader tool instance for agent registration."""
    tool = FileReaderTool(base_dir)
    return {
        'name': tool.name,
        'description': tool.description,
        'function': tool.run,
        'instance': tool
    }

