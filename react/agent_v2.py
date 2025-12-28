"""
ReAct Agent v2
==============

Refactored ReAct agent inspired by DeepResearch architecture.
Uses XML-based tool call format for cleaner parsing.

Features:
- <tool_call> and <tool_response> XML format
- <think> for reasoning, <answer> for final response
- Token counting and context management
- Better error handling with retries
- Structured result output
"""

import os
import re
import json
import time
from typing import Dict, Any, List, Optional, Iterator
from datetime import datetime

from openai import OpenAI
from dotenv import load_dotenv

from .config import (
    BASE_DIR,
    OUTPUT_DIR,
    MAX_ITERATIONS,
    VERBOSE,
    API_KEY_ENV,
    API_BASE_URL,
    MODEL_NAME,
    ensure_directories,
    get_timestamp
)

from .tools.file_reader import FileReaderTool
from .tools.file_writer import FileWriterTool
from .tools.code_executor import CodeExecutorTool
from .tools.pythia_tool import PythiaTool
from .tools.analyzer import AnalyzerTool

load_dotenv()

# XML Tags
TOOL_CALL_START = '<tool_call>'
TOOL_CALL_END = '</tool_call>'
TOOL_RESPONSE_START = '<tool_response>'
TOOL_RESPONSE_END = '</tool_response>'
THINK_START = '<think>'
THINK_END = '</think>'
ANSWER_START = '<answer>'
ANSWER_END = '</answer>'
CODE_START = '<code>'
CODE_END = '</code>'


def today_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")


class ReactAgentV2:
    """
    ReAct Agent v2 - Cleaner architecture with XML-based tool calls.
    """
    
    def __init__(self, 
                 verbose: bool = VERBOSE,
                 max_iterations: int = MAX_ITERATIONS,
                 temperature: float = 0.7,
                 max_retries: int = 3):
        """
        Initialize the ReAct agent.
        """
        self.verbose = verbose
        self.max_iterations = max_iterations
        self.temperature = temperature
        self.max_retries = max_retries
        
        # Initialize API client
        self.client = OpenAI(
            api_key=os.getenv(API_KEY_ENV),
            base_url=API_BASE_URL,
            timeout=120.0
        )
        
        # Initialize tools
        self.tools = self._init_tools()
        
        # System prompt
        self.system_prompt = self._build_system_prompt()
        
        # Conversation state
        self.messages: List[Dict[str, str]] = []
        self.current_round = 0
        
        ensure_directories()
    
    def _init_tools(self) -> Dict[str, Dict[str, Any]]:
        """Initialize all available tools."""
        tools = {}
        
        # File operations
        file_reader = FileReaderTool()
        tools['read_file'] = {
            'fn': file_reader.run,
            'desc': 'Read file contents',
            'params': {'file_path': 'Path to file'}
        }
        tools['list_files'] = {
            'fn': file_reader.list_files,
            'desc': 'List files in directory',
            'params': {'directory': 'Path', 'extension': 'Filter (optional)'}
        }
        
        file_writer = FileWriterTool()
        tools['write_file'] = {
            'fn': file_writer.run,
            'desc': 'Write content to file',
            'params': {'file_path': 'Path', 'content': 'Content'}
        }
        tools['write_python'] = {
            'fn': file_writer.write_python_script,
            'desc': 'Write Python script',
            'params': {'script_name': 'Name', 'code': 'Python code'}
        }
        
        # Code execution
        executor = CodeExecutorTool()
        tools['run_code'] = {
            'fn': executor.run,
            'desc': 'Execute Python code',
            'params': {'code': 'Python code', 'script_name': 'Optional name'}
        }
        tools['run_script'] = {
            'fn': executor.run_script,
            'desc': 'Execute existing script',
            'params': {'script_path': 'Path to script'}
        }
        
        # Pythia8 simulation
        pythia = PythiaTool()
        tools['pythia_generate'] = {
            'fn': pythia.run,
            'desc': 'Generate Pythia8 simulation script',
            'params': {'action': 'basic|histogram|analysis', 'process_type': 'qcd|minbias', 'energy': 'GeV', 'nevents': 'Count'}
        }
        tools['pythia_api'] = {
            'fn': pythia.get_pythia_api_docs,
            'desc': 'Get Pythia8 API documentation',
            'params': {}
        }
        
        # Analysis
        analyzer = AnalyzerTool()
        tools['extract_future_work'] = {
            'fn': lambda **kw: analyzer.run('extract_future_work', **kw),
            'desc': 'Extract future work items from LaTeX',
            'params': {'tex_file': 'Path to .tex file'}
        }
        tools['parse_results'] = {
            'fn': lambda **kw: analyzer.run('parse_simulation_results', **kw),
            'desc': 'Parse simulation results',
            'params': {'results_file': 'Path to results'}
        }
        tools['summarize_review'] = {
            'fn': lambda **kw: analyzer.run('summarize_literature', **kw),
            'desc': 'Summarize literature review',
            'params': {'tex_file': 'Path to .tex file'}
        }
        
        return tools
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt with tool descriptions."""
        tools_xml = self._build_tools_xml()
        
        return f'''You are a research assistant specialized in particle physics simulation using Pythia8mc.
Your task is to conduct automated research: read literature, run simulations, and produce analysis results.

Current date: {today_date()}

# ⚠️ CRITICAL PATH RULES (READ CAREFULLY)

**Absolute paths - ALWAYS use these exact paths:**
- Base directory: `/home/yuntao/Mydata/`
- Scripts: `/home/yuntao/Mydata/pythia_workspace/scripts/`
- Results: `/home/yuntao/Mydata/pythia_workspace/results/`
- Events: `/home/yuntao/Mydata/pythia_workspace/events/`
- Figures: `/home/yuntao/Mydata/pythia_workspace/figures/`
- Literature: `/home/yuntao/Mydata/output/`

**NEVER do this (common error):**
❌ `./pythia_workspace/scripts/./pythia_workspace/scripts/file.py`
❌ `pythia_workspace/scripts/file.py` (missing base path)

**ALWAYS do this:**
✅ `/home/yuntao/Mydata/pythia_workspace/scripts/file.py`

**In Python scripts, construct paths safely:**
```python
import os
BASE_DIR = "/home/yuntao/Mydata/pythia_workspace"
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
FIGURES_DIR = os.path.join(BASE_DIR, "figures")
# Always verify before operations
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)
```

# 📊 FIGURE GENERATION (IMPORTANT)

When your analysis produces numerical results that benefit from visualization:
1. Use matplotlib.pyplot to create publication-quality figures
2. Save figures as PDF for vector quality
3. Record ALL generated figure paths in the analysis JSON under "generated_figures" key



**CRITICAL:** Include figure paths in your analysis JSON:
```json
{{
  "generated_figures": [
    {{
      "path": "/home/yuntao/Mydata/pythia_workspace/figures/xxx",
      "description": "Description of the figure",
      "caption": "Caption of the figure"
    }}
  ]
}}
```

# Tools
{tools_xml}

# Response Format

**For tool calls:**
<think>
Brief reasoning about what to do next...
</think>
<tool_call>
{{"name": "tool_name", "arguments": {{"param": "value"}}}}
</tool_call>

**For Python code:**
<think>
What this code will do...
</think>
<tool_call>
{{"name": "run_code", "arguments": {{}}}}
<code>
import os
# Your Python code - use absolute paths!
print("Results...")
</code>
</tool_call>

# 🎯 TERMINATION CRITERIA

Your task is COMPLETE when you have:
1. ✅ Generated a simulation script saved to `/home/yuntao/Mydata/pythia_workspace/scripts/`
2. ✅ Executed the script successfully
3. ✅ Generated visualization figures saved to `/home/yuntao/Mydata/pythia_workspace/figures/` (if applicable)
4. ✅ Saved analysis results JSON to `/home/yuntao/Mydata/pythia_workspace/results/analysis_*.json`
   - Include "generated_figures" array with paths and captions for all figures

**STOP IMMEDIATELY after saving analysis results. Provide <answer>:**
<think>
Task complete. Script at [path], results at [path], figures at [paths], key findings: [summary]
</think>
<answer>
{{
  "status": "completed",
  "script_path": "/home/yuntao/Mydata/pythia_workspace/scripts/xxx.py",
  "results_path": "/home/yuntao/Mydata/pythia_workspace/results/analysis_xxx.json",
  "figures": ["/home/yuntao/Mydata/pythia_workspace/figures/figure1.pdf"],
  "summary": "Brief description of what was analyzed",
  "key_findings": ["finding1", "finding2"]
}}
</answer>

# Rules

1. Use <think></think> for ALL reasoning (keep it brief)
2. Use <tool_call></tool_call> with valid JSON
3. Wait for <tool_response> before next action
4. Write CLEAN files (no markdown, no "raw" markers)
5. ALWAYS use absolute paths starting with /home/yuntao/Mydata/
6. Before running a script, verify the path is correct
7. After saving analysis results, STOP and provide <answer>
'''
    
    def _build_tools_xml(self) -> str:
        """Build XML description of available tools."""
        lines = ['<tools>']
        for name, info in self.tools.items():
            params_str = ', '.join([f'"{k}": "{v}"' for k, v in info['params'].items()])
            lines.append(f'{{"name": "{name}", "description": "{info["desc"]}", "parameters": {{{params_str}}}}}')
        lines.append('</tools>')
        return '\n'.join(lines)
    
    def reset(self):
        """Reset conversation state."""
        self.messages = [{"role": "system", "content": self.system_prompt}]
        self.current_round = 0
    
    def _log(self, msg: str):
        if self.verbose:
            print(msg)
    
    def _call_llm(self, messages: List[Dict], use_thinking: bool = True) -> str:
        """
        Call the LLM with retry logic and thinking mode support.
        
        Args:
            messages: List of message dicts
            use_thinking: Whether to enable thinking mode (reasoning_content)
        """
        for attempt in range(self.max_retries):
            try:
                # Build request parameters
                request_params = {
                    "model": MODEL_NAME,
                    "messages": messages,
                    "temperature": self.temperature,
                    "max_tokens": 4096,
                    "stop": [TOOL_RESPONSE_START]
                }
                
                # Add thinking parameter if supported (for models that support reasoning)
                # Note: This is API-specific and may not be supported by all providers
                if use_thinking:
                    try:
                        # Try to add thinking parameter (format depends on API)
                        request_params["thinking"] = {
                            "type": "enabled"
                        }
                    except:
                        # If thinking parameter is not supported, continue without it
                        pass
                
                response = self.client.chat.completions.create(**request_params)
                
                # Extract content - handle thinking mode response
                message = response.choices[0].message
                content = message.content
                
                # If thinking mode is enabled, check for reasoning_content
                if use_thinking and hasattr(message, 'reasoning_content') and message.reasoning_content:
                    # Store reasoning for context (can be used in next messages)
                    if not hasattr(self, 'reasoning_history'):
                        self.reasoning_history = []
                    self.reasoning_history.append(message.reasoning_content)
                
                if content and content.strip():
                    return content.strip()
                    
            except Exception as e:
                self._log(f"LLM call attempt {attempt + 1} failed: {e}")
                # If thinking mode fails, retry without it
                if use_thinking and attempt == 0:
                    self._log("Retrying without thinking mode...")
                    return self._call_llm(messages, use_thinking=False)
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
        
        return "Error: Failed to get response from LLM"
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        """Parse agent response to extract think, tool_call, or answer."""
        result = {
            'think': None,
            'tool_call': None,
            'tool_name': None,
            'tool_args': None,
            'code': None,
            'answer': None
        }
        
        # Extract thinking
        think_match = re.search(rf'{THINK_START}(.*?){THINK_END}', content, re.DOTALL)
        if think_match:
            result['think'] = think_match.group(1).strip()
        
        # Check for final answer
        answer_match = re.search(rf'{ANSWER_START}(.*?){ANSWER_END}', content, re.DOTALL)
        if answer_match:
            result['answer'] = answer_match.group(1).strip()
            return result
        
        # Extract tool call
        tool_match = re.search(rf'{TOOL_CALL_START}(.*?){TOOL_CALL_END}', content, re.DOTALL)
        if tool_match:
            tool_content = tool_match.group(1).strip()
            result['tool_call'] = tool_content
            
            # Check for embedded code
            code_match = re.search(rf'{CODE_START}(.*?){CODE_END}', tool_content, re.DOTALL)
            if code_match:
                result['code'] = code_match.group(1).strip()
                # Remove code block from JSON parsing
                json_part = re.sub(rf'{CODE_START}.*?{CODE_END}', '', tool_content, flags=re.DOTALL).strip()
            else:
                json_part = tool_content
            
            # Parse JSON
            try:
                # Find JSON object
                json_match = re.search(r'\{.*\}', json_part, re.DOTALL)
                if json_match:
                    tool_json = json.loads(json_match.group())
                    result['tool_name'] = tool_json.get('name')
                    result['tool_args'] = tool_json.get('arguments', {})
            except json.JSONDecodeError:
                self._log(f"Failed to parse tool JSON: {json_part[:100]}")
        
        # Fallback: Try old format (Thought/Action/Action Input)
        if not result['tool_name']:
            action_match = re.search(r'Action:\s*(\w+)', content)
            if action_match:
                result['tool_name'] = action_match.group(1).strip()
                # Find Action Input
                input_match = re.search(r'Action Input:\s*(\{.*?\})', content, re.DOTALL)
                if input_match:
                    try:
                        result['tool_args'] = json.loads(input_match.group(1))
                    except:
                        result['tool_args'] = {}
        
        return result
    
    def _execute_tool(self, name: str, args: Dict, code: str = None) -> str:
        """Execute a tool and return the result."""
        if name not in self.tools:
            return f"Error: Unknown tool '{name}'. Available: {list(self.tools.keys())}"
        
        tool = self.tools[name]
        
        try:
            # Special handling for code execution
            if name == 'run_code' and code:
                args['code'] = code
            
            # Execute
            result = tool['fn'](**args) if args else tool['fn']()
            
            # Format result
            if isinstance(result, dict):
                return json.dumps(result, indent=2, ensure_ascii=False, default=str)
            return str(result)
            
        except Exception as e:
            return f"Error executing {name}: {str(e)}"
    
    def run(self, task: str, context: str = None) -> Dict[str, Any]:
        """Run the ReAct loop."""
        self.reset()
        
        # Build user message
        user_msg = task
        if context:
            user_msg = f"Context:\n{context}\n\nTask:\n{task}"
        
        self.messages.append({"role": "user", "content": user_msg})
        
        trace = []
        
        while self.current_round < self.max_iterations:
            self.current_round += 1
            self._log(f"\n{'─'*40}\nRound {self.current_round}\n{'─'*40}")
            
            # Get LLM response
            content = self._call_llm(self.messages)
            self.messages.append({"role": "assistant", "content": content})
            
            # Parse response
            parsed = self._parse_response(content)
            
            if parsed['think']:
                self._log(f"💭 Think: {parsed['think'][:200]}...")
            
            # Record trace
            trace.append({
                'round': self.current_round,
                'think': parsed['think'],
                'tool_name': parsed['tool_name'],
                'tool_args': parsed['tool_args']
            })
            
            # Check for final answer
            if parsed['answer']:
                self._log(f"✅ Answer: {parsed['answer'][:300]}...")
                return {
                    'success': True,
                    'answer': parsed['answer'],
                    'rounds': self.current_round,
                    'trace': trace,
                    'messages': self.messages
                }
            
            # Execute tool
            if parsed['tool_name']:
                self._log(f"⚡ Tool: {parsed['tool_name']}")
                self._log(f"   Args: {str(parsed['tool_args'])[:150]}...")
                
                observation = self._execute_tool(
                    parsed['tool_name'],
                    parsed['tool_args'] or {},
                    parsed.get('code')
                )
                
                self._log(f"👁 Observation: {observation[:200]}...")
                
                trace[-1]['observation'] = observation
                
                # Add observation
                self.messages.append({
                    "role": "user",
                    "content": f"{TOOL_RESPONSE_START}\n{observation}\n{TOOL_RESPONSE_END}"
                })
            else:
                self._log("⚠ No tool call or answer found")
                self.messages.append({
                    "role": "user",
                    "content": "Please use the correct format: <think>...</think> followed by <tool_call>...</tool_call> or <answer>...</answer>"
                })
        
        # Max iterations reached
        return {
            'success': False,
            'answer': None,
            'rounds': self.current_round,
            'trace': trace,
            'messages': self.messages,
            'error': 'Max iterations reached'
        }
    
    def run_streaming(self, task: str, context: str = None) -> Iterator[Dict[str, Any]]:
        """Run the ReAct loop with streaming output."""
        self.reset()
        
        user_msg = task
        if context:
            user_msg = f"Context:\n{context}\n\nTask:\n{task}"
        
        self.messages.append({"role": "user", "content": user_msg})
        
        yield {'type': 'start', 'content': 'Starting agent...', 'iteration': 0}
        
        while self.current_round < self.max_iterations:
            self.current_round += 1
            
            yield {'type': 'iteration', 'content': str(self.current_round), 'iteration': self.current_round}
            
            # Get LLM response
            content = self._call_llm(self.messages)
            self.messages.append({"role": "assistant", "content": content})
            
            # Parse response
            parsed = self._parse_response(content)
            
            if parsed['think']:
                yield {
                    'type': 'thought',
                    'content': parsed['think'],
                    'iteration': self.current_round
                }
            
            # Check for final answer
            if parsed['answer']:
                yield {
                    'type': 'final_answer',
                    'content': parsed['answer'],
                    'iteration': self.current_round
                }
                return
            
            # Execute tool
            if parsed['tool_name']:
                yield {
                    'type': 'action',
                    'content': parsed['tool_name'],
                    'action_input': parsed['tool_args'] or {},
                    'iteration': self.current_round
                }
                
                observation = self._execute_tool(
                    parsed['tool_name'],
                    parsed['tool_args'] or {},
                    parsed.get('code')
                )
                
                yield {
                    'type': 'observation',
                    'content': observation,
                    'iteration': self.current_round
                }
                
                self.messages.append({
                    "role": "user",
                    "content": f"{TOOL_RESPONSE_START}\n{observation}\n{TOOL_RESPONSE_END}"
                })
            else:
                yield {
                    'type': 'info',
                    'content': 'Waiting for proper response format...',
                    'iteration': self.current_round
                }
                self.messages.append({
                    "role": "user",
                    "content": "Please respond with <think>...</think> and then <tool_call>...</tool_call> or <answer>...</answer>"
                })
        
        yield {
            'type': 'info',
            'content': f'Reached max iterations ({self.max_iterations}). Session can be continued.',
            'iteration': self.current_round
        }
    
    def get_context_for_continuation(self) -> List[Dict[str, str]]:
        """Get conversation context for session continuation."""
        return self.messages.copy()
    
    def load_context(self, messages: List[Dict[str, str]]):
        """Load conversation context from a previous session."""
        self.messages = messages
        self.current_round = sum(1 for m in messages if m['role'] == 'assistant')

