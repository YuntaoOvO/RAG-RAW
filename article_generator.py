"""
Article Generator
=================

Generate research articles from literature review and simulation results.
"""

import os
import re
import time
import json
from datetime import datetime
from rag_core import Agent
from react.prompts.writer import WRITER_PROMPT, ARTICLE_TEMPLATE

OUTPUT_DIR = '/home/yuntao/Mydata/output'


def get_timestamp() -> str:
    """Generate timestamp for file naming."""
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def save_article(article_text: str, title: str = "Research Article", 
                 output_dir: str = OUTPUT_DIR, timestamp: str = None) -> str:
    """
    Save article to file.
    
    Args:
        article_text: Article content in LaTeX format
        title: Article title
        output_dir: Output directory
        timestamp: Optional timestamp (auto-generated if None)
        
    Returns:
        Path to saved file
    """
    if timestamp is None:
        timestamp = get_timestamp()
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Sanitize title for filename
    safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')[:50]
    filename = f"research_article_{safe_title}_{timestamp}.tex"
    filepath = os.path.join(output_dir, filename)
    
    # Save file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(article_text)
    
    return filepath


def save_article_chinese(article_text: str, title: str = "Research Article",
                         output_dir: str = OUTPUT_DIR, timestamp: str = None) -> str:
    """
    Save Chinese article to file.
    
    Args:
        article_text: Chinese article content in LaTeX format
        title: Article title
        output_dir: Output directory
        timestamp: Optional timestamp (should match English version)
        
    Returns:
        Path to saved file
    """
    if timestamp is None:
        timestamp = get_timestamp()
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Sanitize title for filename
    safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')[:50]
    filename = f"research_article_zh_{safe_title}_{timestamp}.tex"
    filepath = os.path.join(output_dir, filename)
    
    # Save file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(article_text)
    
    return filepath


def clean_generated_text(text: str) -> str:
    """Clean generated text by removing markdown code blocks."""
    # Remove markdown code blocks
    text = re.sub(r'```latex\s*\n?', '', text)
    text = re.sub(r'```\s*\n?', '', text)
    text = re.sub(r'```tex\s*\n?', '', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


def generate_article(literature_file: str, simulation_result_file: str, 
                     title: str = "Research Article", sections: list = None):
    """
    Generate a research article from literature review and simulation results.
    
    Args:
        literature_file: Path to literature review .tex file
        simulation_result_file: Path to simulation results .json file
        title: Article title
        sections: List of sections to include
        
    Returns:
        Generated article in LaTeX format
    """
    if sections is None:
        sections = ["Abstract", "Introduction", "Methodology", "Results", "Conclusion"]
    
    # Read literature review
    log_file = '/home/yuntao/Mydata/.cursor/debug.log'
    # #region agent log
    try:
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"F","location":"article_generator.py:114","message":"Starting generate_article","data":{"literature_file":literature_file,"simulation_file":simulation_result_file,"title":title},"timestamp":int(time.time()*1000)}) + '\n')
    except: pass
    # #endregion
    
    try:
        with open(literature_file, 'r', encoding='utf-8') as f:
            literature_content = f.read()
        # #region agent log
        try:
            with open(log_file, 'a', encoding='utf-8') as log:
                log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"F","location":"article_generator.py:120","message":"Literature file read","data":{"length":len(literature_content)},"timestamp":int(time.time()*1000)}) + '\n')
        except: pass
        # #endregion
    except Exception as e:
        # #region agent log
        try:
            with open(log_file, 'a', encoding='utf-8') as log:
                log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"F","location":"article_generator.py:123","message":"Error reading literature","data":{"error":str(e)},"timestamp":int(time.time()*1000)}) + '\n')
        except: pass
        # #endregion
        raise Exception(f"Error reading literature file: {e}")
    
    # Read simulation results
    # #region agent log
    try:
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"article_generator.py:122","message":"Reading simulation file","data":{"file":simulation_result_file,"exists":os.path.exists(simulation_result_file)},"timestamp":int(time.time()*1000)}) + '\n')
    except: pass
    # #endregion
    
    try:
        # #region agent log
        try:
            with open(log_file, 'a', encoding='utf-8') as log:
                file_size = os.path.getsize(simulation_result_file) if os.path.exists(simulation_result_file) else 0
                log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"article_generator.py:125","message":"Before JSON load","data":{"file_size":file_size},"timestamp":int(time.time()*1000)}) + '\n')
        except: pass
        # #endregion
        
        with open(simulation_result_file, 'r', encoding='utf-8') as f:
            file_content = f.read()
            
        # #region agent log
        try:
            with open(log_file, 'a', encoding='utf-8') as log:
                log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"article_generator.py:130","message":"File content read","data":{"content_length":len(file_content),"first_100_chars":file_content[:100],"last_100_chars":file_content[-100:]},"timestamp":int(time.time()*1000)}) + '\n')
        except: pass
        # #endregion
        
        # Try to parse JSON, with fallback for incomplete files
        try:
            simulation_data = json.loads(file_content)
        except json.JSONDecodeError as json_err:
            # #region agent log
            try:
                with open(log_file, 'a', encoding='utf-8') as log:
                    log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C1","location":"article_generator.py:150","message":"JSON parse failed, attempting repair","data":{"error":str(json_err),"error_pos":getattr(json_err, 'pos', None)},"timestamp":int(time.time()*1000)}) + '\n')
            except: pass
            # #endregion
            
            # Try to repair incomplete JSON by closing open structures
            repaired_content = file_content.rstrip()
            
            # Remove trailing incomplete key-value pairs (ending with ": " or ":")
            # Match patterns like: ,\n      "key":  or \n      "key":
            repaired_content = re.sub(r',?\s*\n\s*"[^"]*":\s*$', '', repaired_content)
            repaired_content = re.sub(r',\s*"[^"]*":\s*$', '', repaired_content)
            
            # #region agent log
            try:
                with open(log_file, 'a', encoding='utf-8') as log:
                    log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C2a","location":"article_generator.py:185","message":"After removing incomplete key","data":{"repaired_end":repaired_content[-100:]},"timestamp":int(time.time()*1000)}) + '\n')
            except: pass
            # #endregion
            
            # Remove trailing comma before closing
            repaired_content = re.sub(r',\s*$', '', repaired_content.rstrip())
            
            # Close open objects/arrays
            open_braces = repaired_content.count('{') - repaired_content.count('}')
            open_brackets = repaired_content.count('[') - repaired_content.count(']')
            repaired_content += '\n' + '}' * open_braces + ']' * open_brackets
            
            # #region agent log
            try:
                with open(log_file, 'a', encoding='utf-8') as log:
                    log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C2","location":"article_generator.py:160","message":"Attempting repaired JSON","data":{"original_len":len(file_content),"repaired_len":len(repaired_content),"open_braces":open_braces,"open_brackets":open_brackets},"timestamp":int(time.time()*1000)}) + '\n')
            except: pass
            # #endregion
            
            try:
                simulation_data = json.loads(repaired_content)
                # #region agent log
                try:
                    with open(log_file, 'a', encoding='utf-8') as log:
                        log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C3","location":"article_generator.py:212","message":"Repaired JSON parsed successfully","data":{"keys":list(simulation_data.keys()) if isinstance(simulation_data, dict) else "not_dict"},"timestamp":int(time.time()*1000)}) + '\n')
                except: pass
                # #endregion
            except json.JSONDecodeError as repair_err:
                # #region agent log
                try:
                    with open(log_file, 'a', encoding='utf-8') as log:
                        log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C4","location":"article_generator.py:220","message":"Repair failed","data":{"error":str(repair_err),"repaired_end":repaired_content[-150:]},"timestamp":int(time.time()*1000)}) + '\n')
                except: pass
                # #endregion
                # If repair failed, try to use partial data by loading what we can
                # Use a more lenient approach: try to extract valid JSON from the beginning
                try:
                    # Find the last complete object by counting braces backwards
                    brace_count = 0
                    last_valid_pos = len(repaired_content)
                    for i in range(len(repaired_content) - 1, -1, -1):
                        if repaired_content[i] == '}':
                            brace_count += 1
                        elif repaired_content[i] == '{':
                            brace_count -= 1
                            if brace_count == 0:
                                last_valid_pos = i + 1
                                break
                    
                    partial_json = repaired_content[:last_valid_pos] + '}'
                    simulation_data = json.loads(partial_json)
                    # #region agent log
                    try:
                        with open(log_file, 'a', encoding='utf-8') as log:
                            log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C5","location":"article_generator.py:235","message":"Partial JSON extracted","data":{"keys":list(simulation_data.keys()) if isinstance(simulation_data, dict) else "not_dict"},"timestamp":int(time.time()*1000)}) + '\n')
                    except: pass
                    # #endregion
                except:
                    raise json_err  # Re-raise original error if all repair attempts fail
        
        # #region agent log
        try:
            with open(log_file, 'a', encoding='utf-8') as log:
                log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"article_generator.py:175","message":"JSON parsed successfully","data":{"keys":list(simulation_data.keys()) if isinstance(simulation_data, dict) else "not_dict"},"timestamp":int(time.time()*1000)}) + '\n')
        except: pass
        # #endregion
        
    except json.JSONDecodeError as e:
        # #region agent log
        try:
            with open(log_file, 'a', encoding='utf-8') as log:
                log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"article_generator.py:140","message":"JSON decode error","data":{"error":str(e),"error_line":getattr(e, 'lineno', None),"error_col":getattr(e, 'colno', None),"error_pos":getattr(e, 'pos', None)},"timestamp":int(time.time()*1000)}) + '\n')
        except: pass
        # #endregion
        raise Exception(f"Invalid JSON format in simulation results file: {e}")
    except Exception as e:
        # #region agent log
        try:
            with open(log_file, 'a', encoding='utf-8') as log:
                log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"E","location":"article_generator.py:145","message":"General error reading file","data":{"error":str(e),"error_type":type(e).__name__},"timestamp":int(time.time()*1000)}) + '\n')
        except: pass
        # #endregion
        raise Exception(f"Error reading simulation results: {e}")
    
    # Extract generated figures if available
    generated_figures = simulation_data.get('generated_figures', [])
    
    # Validate which figures actually exist
    valid_figures = []
    for fig in generated_figures:
        fig_path = fig.get('path', '')
        if os.path.exists(fig_path):
            valid_figures.append(fig)
    
    # Build figures section for prompt
    if valid_figures:
        figures_info = f'''
# AVAILABLE FIGURES (use ONLY these)
The following figures have been generated and are available for inclusion:

{json.dumps(valid_figures, indent=2)}

IMPORTANT for figures:
- ONLY use \\includegraphics for figures listed above
- Use the exact absolute path from the "path" field
- Each figure should have a proper caption using the "caption" or "description" field
- Use \\label{{fig:descriptive_name}} for referencing
- Reference figures in text with \\ref{{fig:name}}

Example:
\\begin{{figure}}[h!]
\\centering
\\includegraphics[width=0.8\\textwidth]{{/home/yuntao/Mydata/pythia_workspace/figures/xxx}}
\\caption{{Transverse momentum spectrum from simulation}}
\\label{{fig:pt_spectrum}}
\\end{{figure}}
'''
    else:
        figures_info = '''
# NO FIGURES AVAILABLE
No pre-generated figures are available. 
CRITICAL: Do NOT use \\includegraphics or placeholder images.
Instead, present data using:
- LaTeX tables (\\begin{table}...\\end{table})
- Inline equations
- Text descriptions of numerical results
'''
    
    # Build prompt
    prompt = WRITER_PROMPT + f'''

Your task: Generate a complete research article in LaTeX format.

Article Title: {title}

Required Sections: {', '.join(sections)}

Literature Review Content:
{literature_content[:5000]}

Simulation Results:
{json.dumps(simulation_data, indent=2, ensure_ascii=False)[:3000]}
{figures_info}

Generate a complete LaTeX article with:
1. Proper document structure with \\documentclass{{article}}
2. All required sections with meaningful content
3. Integration of literature review findings
4. Presentation of simulation results with proper formatting
5. Comprehensive analysis of the simulation results(including figures and tables with conclusions and discussions and future work directions)
6. Proper citations using \\cite{{}} format with urls in each reference

Output ONLY the LaTeX source code, no markdown formatting, no explanations.
'''
    
    agent = Agent(prompt)
    
    context = f"""Generate a research article titled "{title}" combining:
- Literature review findings from: {literature_file}
- Simulation results from: {simulation_result_file}
- Figures and tables from: {simulation_result_file}
Include sections: {', '.join(sections)}
"""
    
    gen_text = agent.chat("Generate the article", context=context, stream=False)
    gen_text = clean_generated_text(gen_text)
    
    # Ensure proper LaTeX document structure
    if not gen_text.startswith(r'\documentclass'):
        # Wrap in document structure if needed
        gen_text = ARTICLE_TEMPLATE.replace('TITLE_PLACEHOLDER', title).replace('ABSTRACT_PLACEHOLDER', '') + '\n\n' + gen_text
    
    # Safeguard: Validate and fix figure references
    gen_text = validate_and_fix_figures(gen_text, valid_figures)
    
    return gen_text


def validate_and_fix_figures(tex_content: str, valid_figures: list) -> str:
    """
    Validate figure references in LaTeX content and remove invalid ones.
    
    Args:
        tex_content: LaTeX content to validate
        valid_figures: List of valid figure dictionaries with 'path' key
        
    Returns:
        Fixed LaTeX content with invalid figures removed or replaced
    """
    # Get set of valid figure paths
    valid_paths = set()
    for fig in valid_figures:
        fig_path = fig.get('path', '')
        valid_paths.add(fig_path)
        # Also add the filename without path for relative references
        valid_paths.add(os.path.basename(fig_path))
        # Add without extension
        base_name = os.path.splitext(os.path.basename(fig_path))[0]
        valid_paths.add(base_name)
    
    # Find all \includegraphics references
    pattern = r'\\begin\{figure\}.*?\\end\{figure\}'
    
    def check_figure_block(match):
        block = match.group(0)
        # Extract the path from \includegraphics
        img_pattern = r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}'
        img_match = re.search(img_pattern, block)
        
        if img_match:
            img_path = img_match.group(1)
            # Check if this path is valid
            is_valid = (
                img_path in valid_paths or
                os.path.exists(img_path) or
                any(img_path.endswith(vp) or vp.endswith(img_path) for vp in valid_paths if vp)
            )
            
            if not is_valid:
                # Replace the figure block with a comment
                caption_match = re.search(r'\\caption\{([^}]+)\}', block)
                caption = caption_match.group(1) if caption_match else 'Figure not available'
                
                return f'''% Figure removed: {img_path} (file not found)
% Original caption: {caption}
% Note: Generate this figure using the simulation data'''
        
        return block
    
    # Apply the fix to all figure blocks
    fixed_content = re.sub(pattern, check_figure_block, tex_content, flags=re.DOTALL)
    
    # Also check for standalone \includegraphics without figure environment
    standalone_pattern = r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}'
    
    def check_standalone(match):
        img_path = match.group(1)
        is_valid = (
            img_path in valid_paths or
            os.path.exists(img_path) or
            any(img_path.endswith(vp) or vp.endswith(img_path) for vp in valid_paths if vp)
        )
        if not is_valid:
            return f'% Image removed: {img_path} (file not found)'
        return match.group(0)
    
    fixed_content = re.sub(standalone_pattern, check_standalone, fixed_content)
    
    return fixed_content


def translate_article_to_chinese(article_text: str):
    """
    Translate article to Chinese LaTeX format.
    
    Args:
        article_text: English LaTeX article
        
    Returns:
        Chinese LaTeX article, with complete urls in each reference
    """
    prompt = '''You are a scientific translator. Translate the following LaTeX article to Chinese.

IMPORTANT:
- Keep all LaTeX commands unchanged (\\section{}, \\cite{}, etc.)
- Keep all mathematical equations unchanged
- Translate only the text content
- Use \\documentclass{ctexart} instead of \\documentclass{article}
- Preserve all formatting and structure, including figures and tables
- Keep all urls in each reference
'''
    
    agent = Agent(prompt)
    
    context = f"""Translate this LaTeX article to Chinese:

{article_text}
"""
    
    gen_text = agent.chat("Translate to Chinese", context=context, stream=False)
    gen_text = clean_generated_text(gen_text)
    
    # Ensure ctexart document class
    # Use simple string replace instead of regex to avoid escape sequence issues
    gen_text = gen_text.replace('\\documentclass{article}', '\\documentclass{ctexart}')
    
    return gen_text

