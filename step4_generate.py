"""
Step 4: Literature Review Generation Module
=============================================

This module generates and polishes literature reviews using AI:
1. Stage 1: Generate initial draft from results
2. Stage 2: Enhance with logical context
3. Stage 3: Finalize with future work directions

Usage:
    # Standalone execution with default constants
    python step4_generate.py
    
    # Import and use with custom inputs
    from step4_generate import generate_review
    final_review = generate_review(user_input="my topic", results=my_results)
"""

import os
import re
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# ============================================================================
# Stable Configuration for Testing/Showcase
# ============================================================================

TIMESTAMP = '20250901_002253'
OUTPUT_DIR = './output'

USER_INPUT = "the effect of spinodal construction of first order phase transition in the equation of state and the fluid dynamic simulations"


# ============================================================================
# AI Agent Class
# ============================================================================

class Agent:
    """AI Agent for generating literature review using OpenAI-compatible API."""
    
    def __init__(self, system=""):
        self.system = system
        self.client = OpenAI(
            api_key=os.getenv("MIMO_API_KEY"),
            base_url="https://api.xiaomimimo.com/v1"
        )
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": system})
    
    def chat(self, user_input, context="", stream=False):
        """Send a message and get a response."""
        if context:
            full_input = f"{context}\n\n{user_input}"
        else:
            full_input = user_input
        
        self.messages.append({"role": "user", "content": full_input})
        
        response = self.client.chat.completions.create(
            model="mimo-v2-flash",
            messages=self.messages,
            stream=stream
        )
        
        if stream:
            return response
        else:
            assistant_message = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": assistant_message})
            return assistant_message


# ============================================================================
# Utility Functions
# ============================================================================

def clean_generated_text(gen_text):
    """Remove <think> tags and their content from generated text."""
    return re.sub(r'<think>.*?</think>', '', gen_text, flags=re.DOTALL).strip()


def ensure_output_dir(output_dir=OUTPUT_DIR):
    """Ensure output directory exists."""
    os.makedirs(output_dir, exist_ok=True)


def load_results_from_file(file_path):
    """Load query results from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('texts', data)


def save_draft(content, file_path):
    """Save draft content to a file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Saved: {file_path}")


def let_bibtex_in(bibfile_path):
    """Load bibtex content from file."""
    try:
        with open(bibfile_path, 'r', encoding='utf-8') as file:
            bibtex_content = file.read()
        return bibtex_content
    except FileNotFoundError:
        print(f"Warning: BibTeX file not found: {bibfile_path}")
        return ""


# ============================================================================
# Literature Review Generation Functions
# ============================================================================

def literature_review_stage1(topic, results):
    """
    Stage 1: Generate initial draft from research results.
    
    Args:
        topic: Research topic
        results: List of result texts from database query
        
    Returns:
        Initial draft with LaTeX citations
    """
    prompt = r'''You are a distinguished physicist and expert literature review author with exceptional analytical and synthesis capabilities, publishing in Science and Nature.

        Your mission: Compose the initial draft of a comprehensive, publication-quality literature review focusing on research findings and key results IN Latex source code for Science/Nature.

        Input structure:
        1. Results: Key findings from papers with document identifiers (doc_id/arxiv_id)

        Output requirements:

        STRUCTURE:
        - Introduction: Establish the research domain and its significance
        - Research Timeline & Key Findings: Chronological or thematic presentation of major results
        - Logical Connections & Evolution: Initial framework for how ideas connect (will be enhanced later)
        - Future Research Directions: Preliminary outline (will be completed later)

        CITATION FORMAT - CRITICAL:
        - Use LaTeX citation format: \cite{doc_id}
        - Extract doc_id/arxiv_id from the results data (e.g., 0903.4335, 2408.09679, hep-ph/0009171)
        - Format examples: \cite{0903.4335}, \cite{2408.09679}, \cite{hep-ph/0009171}
        - Ensure every factual claim is properly cited with \cite{doc_id}
        - Multiple citations: \cite{paper1,paper2,paper3}
        - This format is compatible with BibTeX files for Science/Nature submissions

        SYNTHESIS REQUIREMENTS:
        - Identify common themes across multiple papers
        - Highlight contradictions or debates in the field
        - Show methodological evolution
        - Present findings chronologically or thematically

        WRITING STYLE:
        - Clear, formal academic English suitable for Science/Nature
        - Coherent narrative flow between paragraphs
        - No bullet points - use continuous prose
        - Professional tone suitable for top-tier publication

        CRITICAL: Use ONLY the provided information. Do not fabricate or infer beyond the given sources.
        '''

    agent = Agent(prompt)
    
    context = f"""Research Topic: {topic}
                    RESULTS:
                    {str(results)}

                    Generate an initial literature review draft with LaTeX citations using \\cite{{doc_id}} format. Extract doc_id values from the results and use them in citations:
                """
                        
    gen_text = agent.chat(topic, context=context, stream=False)
    gen_text = clean_generated_text(gen_text)
    return gen_text


def literature_review_stage2(topic, stage1_draft, logical_context):
    """
    Stage 2: Enhance draft with logical connections and intellectual evolution.
    
    Args:
        topic: Research topic
        stage1_draft: Initial draft from stage 1
        logical_context: Logical connection texts from database query
        
    Returns:
        Enhanced draft with logical context
    """
    prompt = r'''You are a distinguished physicist refining a literature review for Science/Nature publication by incorporating logical connections and intellectual evolution IN Latex source code for Science/Nature.

        Your mission: Enhance the existing literature review draft by enriching it with theoretical foundations, logical progressions, and intellectual lineage.

        Input structure:
        1. Initial Draft: A complete literature review draft with LaTeX citations already in place
        2. Logical Context: Information about theoretical connections, research evolution, and intellectual debates

        Output requirements:

        ENHANCEMENT FOCUS:
        - Significantly enhance the "Logical Connections & Evolution" section
        - Improve narrative flow and theoretical foundations throughout
        - Show how ideas built upon each other, evolved, or contradicted previous work
        - Add intellectual debates and methodological progressions
        - Weave logical context naturally into existing narrative

        CITATION PRESERVATION:
        - Maintain ALL existing LaTeX citations from the initial draft
        - Preserve the \cite{doc_id} format throughout
        - Do NOT remove or modify existing citations
        - Logical context may not have citations - that's expected

        SYNTHESIS REQUIREMENTS:
        - Identify theoretical lineage and conceptual development
        - Highlight methodological evolution
        - Show consensus building or persistent debates
        - Connect research efforts across time and approaches

        WRITING STYLE:
        - Maintain Science/Nature publication standards
        - Preserve clear, formal academic English
        - Enhance coherent narrative flow between paragraphs
        - Keep continuous prose without bullet points
        - Professional tone suitable for top-tier publication

        CRITICAL: Build upon the existing draft. Do not remove content. Add logical depth and theoretical context.
        '''

    agent = Agent(prompt)
    
    context = f"""Research Topic: {topic}
                    INITIAL DRAFT:
                    {stage1_draft}

                    LOGICAL CONTEXT TO INCORPORATE:
                    {str(logical_context)}

                    Refine the draft by enriching logical connections, theoretical evolution, and intellectual lineage while preserving all existing citations:"""
                        
    gen_text = agent.chat(topic, context=context, stream=False)
    gen_text = clean_generated_text(gen_text)
    return gen_text


def literature_review_stage3(topic, stage2_draft, future_work_raw, bibfile_path=None, timestamp=None):
    """
    Stage 3: Finalize with future research directions.
    
    Args:
        topic: Research topic
        stage2_draft: Enhanced draft from stage 2
        future_work_raw: Future work texts from database query
        bibfile_path: Path to bibtex file (optional)
        timestamp: Timestamp for default bibtex path
        
    Returns:
        Final polished literature review
    """
    # Load bibtex content if available
    if bibfile_path is None and timestamp is not None:
        bibfile_path = f"bib/topic_{timestamp}.bib"
    
    bibtext = ""
    if bibfile_path:
        bibtext = let_bibtex_in(bibfile_path)
    
    prompt = r'''You are a distinguished physicist finalizing a literature review for Science/Nature publication by synthesizing future research directions IN Latex source code for Science/Nature.

        Your mission: Complete the literature review by consolidating future research directions and ensuring publication readiness.
        For the future work section, you should list the potential future research directions and the corresponding citations. Then get them ranked by the possibility of being realized using AI tools of yourself. 
        Select the top 2 or 3 directions to write a brief research plan for each of them.

        Input structure:
        1. Refined Draft: A literature review with comprehensive findings and logical connections already in place
        2. Future Work Directions: Raw aggregated future research suggestions from multiple papers

        Output requirements:

        COMPLETION FOCUS:
        - Significantly enhance and complete the "Future Research Directions" section
        - Consolidate overlapping suggestions into coherent themes
        - Remove redundant or already-addressed future directions
        - Identify genuine research gaps and open problems
        - Prioritize future directions by importance and feasibility

        CITATION PRESERVATION:
        - Maintain ALL existing LaTeX citations throughout the document
        - Preserve the \cite{doc_id} format, only with the bibtex citation format because we have bibtex file will be provided later
        - Do NOT remove or modify any existing content or citations

        SYNTHESIS REQUIREMENTS:
        - Group related future directions into thematic categories
        - Remove redundancy while preserving unique insights
        - Ensure future directions are not already addressed in the findings
        - Present a clear research agenda moving forward
        - Balance ambition with feasibility

        FINAL POLISH:
        - Ensure overall coherence across all sections
        - Verify smooth transitions between sections
        - Check that introduction and conclusion align
        - Confirm Science/Nature publication standards throughout
        - Ensure continuous prose without bullet points

        WRITING STYLE:
        - Clear, formal academic English suitable for Science/Nature
        - Coherent narrative flow between all sections
        - Professional tone throughout
        - Publication-ready quality
        - Output LaTeX source code , and citation format: \cite{doc_id}
        - ADD URLs FOR EVERY Reference: to the bibtex file, use \usepackage{hyperref} and then use \href{url_of_arxiv}{arxiv_id} to link the arxiv_id to the url_of_arxiv
        CRITICAL: This is the final version. Ensure completeness, coherence, and publication readiness.
        '''

    agent = Agent(prompt)
    
    context = f"""Research Topic: {topic}
                    REFINED DRAFT:
                    {stage2_draft}

                    FUTURE WORK DIRECTIONS TO SYNTHESIZE:
                    {str(future_work_raw)}

                    BIBTEX FILE:
                    {bibtext}
                    Finalize the review by synthesizing future research directions and ensuring publication quality:
                    """
                        
    gen_text = agent.chat(topic, context=context, stream=False)
    gen_text = clean_generated_text(gen_text)
    return gen_text


def translate_to_chinese(text):
    """
    Translate the final review to Chinese using LaTeX ctexart format.
    
    Args:
        text: English LaTeX content to translate
        
    Returns:
        Chinese translated LaTeX content
    """
    prompt = r"You are a Chinese academic translator using latex output format(remember to use \documentclass{ctexart} ). Translate the following academic paper to Chinese (only main text, not the codes) and keep the citation format."
    
    agent = Agent(prompt)
    context = f"translate the following text to Chinese: {text}"
    gen_text = agent.chat(text, context=context, stream=False)
    gen_text = clean_generated_text(gen_text)
    return gen_text


# ============================================================================
# Main Functions
# ============================================================================

def generate_review(user_input=None, results=None, logical=None, future=None,
                    results_file=None, logical_file=None, future_file=None,
                    output_dir=OUTPUT_DIR, timestamp=None,
                    save_intermediate=True, bibfile_path=None,
                    generate_chinese=True):
    """
    Generate a complete literature review through 3 stages.
    
    Args:
        user_input: Research topic (uses USER_INPUT constant if None)
        results: Results texts (loads from file if None)
        logical: Logical texts (loads from file if None)
        future: Future texts (loads from file if None)
        results_file: Path to results JSON file
        logical_file: Path to logical JSON file
        future_file: Path to future JSON file
        output_dir: Output directory for drafts
        timestamp: Timestamp for file naming
        save_intermediate: Whether to save intermediate drafts
        bibfile_path: Path to bibtex file for Stage 3
        generate_chinese: Whether to generate Chinese translation
        
    Returns:
        Dict with all drafts, final review, and Chinese translation
    """
    if timestamp is None:
        timestamp = TIMESTAMP
    
    if user_input is None:
        user_input = USER_INPUT
    
    ensure_output_dir(output_dir)
    
    # Load inputs from files if not provided directly
    if results is None:
        if results_file is None:
            results_file = os.path.join(output_dir, f"results_txt_{timestamp}.json")
        print(f"Loading results from: {results_file}")
        results = load_results_from_file(results_file)
    
    if logical is None:
        if logical_file is None:
            logical_file = os.path.join(output_dir, f"logical_txt_{timestamp}.json")
        print(f"Loading logical from: {logical_file}")
        logical = load_results_from_file(logical_file)
    
    if future is None:
        if future_file is None:
            future_file = os.path.join(output_dir, f"future_txt_{timestamp}.json")
        print(f"Loading future from: {future_file}")
        future = load_results_from_file(future_file)
    
    print(f"\nTopic: {user_input[:80]}...")
    print(f"Results: {len(results)} texts")
    print(f"Logical: {len(logical)} texts")
    print(f"Future: {len(future)} texts")
    
    # Stage 1: Generate initial draft
    print("\n" + "=" * 50)
    print("Stage 1: Generating initial draft from results...")
    print("=" * 50)
    draft1 = literature_review_stage1(user_input, results)
    print("Stage 1 completed.")
    
    if save_intermediate:
        draft1_file = os.path.join(output_dir, f"draft1_{timestamp}.tex")
        save_draft(draft1, draft1_file)
    
    # Stage 2: Enhance with logical context
    print("\n" + "=" * 50)
    print("Stage 2: Enhancing with logical context...")
    print("=" * 50)
    draft2 = literature_review_stage2(user_input, draft1, logical)
    print("Stage 2 completed.")
    
    if save_intermediate:
        draft2_file = os.path.join(output_dir, f"draft2_{timestamp}.tex")
        save_draft(draft2, draft2_file)
    
    # Stage 3: Finalize with future work (with bibtex support)
    print("\n" + "=" * 50)
    print("Stage 3: Finalizing with future work directions...")
    print("=" * 50)
    final_review = literature_review_stage3(
        user_input, draft2, future, 
        bibfile_path=bibfile_path, 
        timestamp=timestamp
    )
    print("Stage 3 completed.")
    
    # Save final review (English)
    final_file = os.path.join(output_dir, f"final_review_{timestamp}.tex")
    save_draft(final_review, final_file)
    
    # Generate Chinese translation if requested
    final_review_zh = None
    final_file_zh = None
    if generate_chinese:
        print("\n" + "=" * 50)
        print("Generating Chinese translation...")
        print("=" * 50)
        final_review_zh = translate_to_chinese(final_review)
        print("Chinese translation completed.")
        
        final_file_zh = os.path.join(output_dir, f"final_review_zh_{timestamp}.tex")
        save_draft(final_review_zh, final_file_zh)
    
    return {
        'draft1': draft1,
        'draft2': draft2,
        'final_review': final_review,
        'final_review_zh': final_review_zh,
        'files': {
            'draft1': os.path.join(output_dir, f"draft1_{timestamp}.tex") if save_intermediate else None,
            'draft2': os.path.join(output_dir, f"draft2_{timestamp}.tex") if save_intermediate else None,
            'final': final_file,
            'final_zh': final_file_zh
        }
    }


def generate_review_from_files(timestamp=None, output_dir=OUTPUT_DIR, user_input=None,
                                bibfile_path=None, generate_chinese=True):
    """
    Convenience function to generate review from existing result files.
    
    Args:
        timestamp: Timestamp to identify files
        output_dir: Directory containing input files
        user_input: Research topic
        bibfile_path: Path to bibtex file
        generate_chinese: Whether to generate Chinese translation
        
    Returns:
        Dict with all drafts, final review, and Chinese translation
    """
    if timestamp is None:
        timestamp = TIMESTAMP
    
    return generate_review(
        user_input=user_input,
        timestamp=timestamp,
        output_dir=output_dir,
        bibfile_path=bibfile_path,
        generate_chinese=generate_chinese
    )


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Step 4: Literature Review Generation")
    print("=" * 70)
    
    # Generate review from existing result files
    result = generate_review_from_files(
        timestamp=TIMESTAMP,
        output_dir=OUTPUT_DIR,
        user_input=USER_INPUT
    )
    
    print("\n" + "=" * 70)
    print("Literature Review Generation Complete!")
    print("=" * 70)
    
    print("\nOutput files:")
    for name, path in result['files'].items():
        if path:
            print(f"  {name}: {path}")
    
    print("\n" + "=" * 70)
    print("FINAL LITERATURE REVIEW PREVIEW (English)")
    print("=" * 70)
    # Show first 2000 characters of final review
    preview = result['final_review'][:2000]
    if len(result['final_review']) > 2000:
        preview += "\n\n... [truncated for preview] ..."
    print(preview)
    
    if result.get('final_review_zh'):
        print("\n" + "=" * 70)
        print("中文翻译预览 (Chinese Translation Preview)")
        print("=" * 70)
        preview_zh = result['final_review_zh'][:2000]
        if len(result['final_review_zh']) > 2000:
            preview_zh += "\n\n... [已截断] ..."
        print(preview_zh)

