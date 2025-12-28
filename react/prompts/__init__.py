"""
ReAct Prompts Module
====================

System prompts for different agent roles:
- researcher: Research planning and analysis prompts
- coder: Code generation prompts for Pythia8
- writer: Article writing prompts in LaTeX format
"""

from .researcher import RESEARCHER_PROMPT, FUTURE_WORK_ANALYZER_PROMPT
from .coder import CODER_PROMPT, PYTHIA_EXPERT_PROMPT
from .writer import WRITER_PROMPT, ARTICLE_TEMPLATE

__all__ = [
    'RESEARCHER_PROMPT',
    'FUTURE_WORK_ANALYZER_PROMPT',
    'CODER_PROMPT',
    'PYTHIA_EXPERT_PROMPT',
    'WRITER_PROMPT',
    'ARTICLE_TEMPLATE'
]

