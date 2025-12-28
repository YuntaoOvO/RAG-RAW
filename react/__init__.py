"""
ReAct Framework for Particle Physics Research
==============================================

A Reason-Act framework that enables AI to:
1. Read literature reviews and extract future work items
2. Learn Pythia8 Python API for particle physics simulations
3. Generate and execute Python code for physics simulations
4. Analyze results and write research articles

Main Components:
- agent: Main ReAct agent with reasoning loop
- tools: Tool implementations (file_reader, file_writer, code_executor, etc.)
- prompts: System prompts for different tasks
- config: Configuration constants
"""

from .agent import ReactAgent
from .config import *

__version__ = "1.0.0"
__all__ = ['ReactAgent']

