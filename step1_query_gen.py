"""
Step 1: Query Generation Module
================================

This module generates search queries using 3 AI-based functions:
1. ai_paper_results_query - generates result-focused queries
2. ai_logical_chain_query - generates logical connection queries  
3. ai_future_work_query - generates future work queries

The queries are saved to a JSON file for use by subsequent steps.

Usage:
    # Standalone execution with default constants
    python step1_query_gen.py
    
    # Import and use with custom input
    from step1_query_gen import generate_queries
    queries = generate_queries(user_input="my custom topic", n=10)
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

# Pre-generated queries for stable testing (fallback)
CONST_RESULT_QUERIES = [
    "spinodal construction first order phase transition equation of state fluid dynamic simulation results",
    "spinodal decomposition phase transition fluid dynamics numerical simulation findings",
    "first order phase transition spinodal region equation of state fluid flow results",
    "spinodal construction thermodynamic equation of state fluid dynamic simulation conclusions",
    "phase transition spinodal instability fluid dynamics simulation experimental outcomes",
    "spinodal construction first order transition EOS fluid dynamic modeling discoveries",
    "spinodal region phase transition equation of state fluid simulation results discussion",
    "first order phase transition spinodal construction fluid dynamics theoretical conclusions",
    "spinodal construction phase transition equation of state fluid dynamic simulation abstract",
    "spinodal construction first order phase transition fluid dynamics simulation summary findings"
]

CONST_LOGICAL_QUERIES = [
    "theoretical foundations of spinodal construction in first order phase transitions and equation of state evolution",
    "methodological evolution of spinodal construction from thermodynamic theory to fluid dynamic simulations",
    "intellectual lineage connecting spinodal decomposition theory to hydrodynamic modeling approaches",
    "research progression from classical nucleation theory to spinodal construction in phase transition literature",
    "theoretical connections between equation of state modifications and spinodal region construction methods",
    "evolution of computational fluid dynamics approaches for simulating spinodal decomposition in phase transitions",
    "intellectual debates on metastability and spinodal construction in first order phase transition modeling",
    "methodological connections between thermodynamic instability criteria and fluid dynamic simulation techniques",
    "research lineage tracing from van der Waals theory to modern spinodal construction in EOS development",
    "theoretical and computational evolution of spinodal construction methods in multiphase flow simulations"
]

CONST_FUTURE_QUERIES = [
    "future work spinodal construction first order phase transition equation of state fluid dynamic simulations",
    "limitations spinodal construction first order phase transition equation of state fluid dynamic simulations",
    "open problems spinodal construction first order phase transition equation of state fluid dynamic simulations",
    "future directions spinodal construction first order phase transition equation of state fluid dynamic simulations",
    "unexplored areas spinodal construction first order phase transition equation of state fluid dynamic simulations",
    "research gaps spinodal construction first order phase transition equation of state fluid dynamic simulations",
    "future outlook spinodal construction first order phase transition equation of state fluid dynamic simulations",
    "suggested improvements spinodal construction first order phase transition equation of state fluid dynamic simulations",
    "remaining challenges spinodal construction first order phase transition equation of state fluid dynamic simulations",
    "future research spinodal construction first order phase transition equation of state fluid dynamic simulations"
]


# ============================================================================
# AI Agent Class
# ============================================================================

class Agent:
    """AI Agent for generating queries using OpenAI-compatible API."""
    
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


# ============================================================================
# AI Query Generation Functions
# ============================================================================

def ai_paper_results_query(topic, n=10):
    """Generate result-focused search queries for academic papers."""
    prompt = f'''You are an expert academic search specialist focused on extracting research findings and conclusions.

Your task: Generate {n} precise search queries to retrieve key research results, conclusions, and discoveries from academic papers.

Target sections: Results, Conclusions, Discussion, Abstract, Summary
Focus: Research findings, experimental outcomes, theoretical conclusions, discovery timelines, and publication metadata

Requirements:
- Each query must target content that contains identifiable results or conclusions
- Queries should capture both specific findings and their temporal context
- Prioritize queries that will return content WITH metadata (doc_id, source, publication info)
- Format queries to maximize retrieval of citable, result-oriented content

Output format:
["query 1 targeting specific results and conclusions",
 "query 2 focusing on experimental findings",
 "query 3 about theoretical outcomes",
 ...
 "query {n} capturing key discoveries"]
'''

    agent = Agent(prompt)
    context = f"Research topic: {topic}\n\nGenerate {n} result-focused search queries:"
    gen_text = agent.chat(topic, context=context, stream=False)
    gen_text = clean_generated_text(gen_text)
    return gen_text


def ai_logical_chain_query(topic, n=10):
    """Generate queries for logical connections and intellectual lineage."""
    prompt = f'''You are an expert in tracing the evolution of scientific ideas and logical connections between research efforts.

Your task: Generate {n} precise search queries to identify the logical progression, theoretical connections, and intellectual lineage within academic literature.

Target sections: Introduction, Literature Review, Background, Related Work
Focus: Prior work citations, theoretical foundations, research evolution, methodological connections, intellectual debates

Requirements:
- Each query must target content discussing relationships between different research efforts
- Queries should capture how ideas evolved, built upon each other, or contradicted previous work
- Focus on finding narrative connections rather than isolated results
- Format queries to retrieve context-rich literature review content

Output format:
["query 1 about theoretical foundations and origins",
 "query 2 exploring methodological evolution",
 "query 3 on intellectual connections between studies",
 ...
 "query {n} tracing research lineage"]'''

    agent = Agent(prompt)
    context = f"Research topic: {topic}\n\nGenerate {n} queries for logical connections:"
    gen_text = agent.chat(topic, context=context, stream=False)
    gen_text = clean_generated_text(gen_text)
    return gen_text


def ai_future_work_query(topic, n=10):
    """Generate queries for future work and research gaps."""
    prompt = f'''You are an expert at identifying research gaps, open problems, and future research directions in academic literature.

Your task: Generate {n} precise search queries to extract future work suggestions, limitations, and unexplored research directions from academic papers.

Target sections: Future Work, Future Directions, Limitations, Outlook, Discussion (future-oriented parts), Conclusion (forward-looking statements)
Focus: Proposed future research, acknowledged limitations, open questions, suggested improvements, unexplored areas

Requirements:
- Each query must target forward-looking content about potential future research
- Queries should capture both explicit "future work" sections and implicit research gaps
- Focus on identifying what remains to be done rather than what was accomplished
- Format queries to aggregate future directions across multiple papers

Output format:
["query 1 about explicitly stated future research directions",
 "query 2 focusing on acknowledged limitations",
 "query 3 on open problems and challenges",
 ...
 "query {n} capturing unexplored research areas"]'''

    agent = Agent(prompt)
    context = f"Research topic: {topic}\n\nGenerate {n} future work queries:"
    gen_text = agent.chat(topic, context=context, stream=False)
    gen_text = clean_generated_text(gen_text)
    return gen_text


def parse_query_response(response_text):
    """Parse AI-generated query response into a list."""
    try:
        # Try to parse as JSON
        queries = json.loads(response_text)
        if isinstance(queries, list):
            return queries
    except json.JSONDecodeError:
        pass
    
    # Fallback: extract strings from the response
    import ast
    try:
        queries = ast.literal_eval(response_text)
        if isinstance(queries, list):
            return queries
    except:
        pass
    
    # Last resort: split by newlines and clean
    lines = response_text.strip().split('\n')
    queries = []
    for line in lines:
        line = line.strip().strip(',').strip('"').strip("'").strip('[').strip(']')
        if line and not line.startswith('#'):
            queries.append(line)
    
    return queries if queries else [response_text]


# ============================================================================
# Main Functions
# ============================================================================

def generate_queries(user_input=None, n=10, output_file=None, use_const=False, timestamp=None):
    """
    Generate all query types and save to file.
    
    Args:
        user_input: Research topic (uses USER_INPUT constant if None)
        n: Number of queries to generate for each type
        output_file: Output file path (auto-generated if None)
        use_const: If True, use pre-generated constant queries instead of AI
        timestamp: Timestamp for file naming (uses TIMESTAMP constant if None)
    
    Returns:
        dict with 'results', 'logical', 'future' query lists
    """
    if user_input is None:
        user_input = USER_INPUT
    
    if timestamp is None:
        timestamp = TIMESTAMP
    
    ensure_output_dir()
    
    if output_file is None:
        output_file = os.path.join(OUTPUT_DIR, f"queries_{timestamp}.json")
    
    if use_const:
        print("Using pre-generated constant queries...")
        queries = {
            'user_input': user_input,
            'timestamp': timestamp,
            'results': CONST_RESULT_QUERIES,
            'logical': CONST_LOGICAL_QUERIES,
            'future': CONST_FUTURE_QUERIES
        }
    else:
        print(f"Generating queries for topic: {user_input[:80]}...")
        
        print("\n[1/3] Generating result-focused queries...")
        results_raw = ai_paper_results_query(user_input, n=n)
        results_queries = parse_query_response(results_raw)
        print(f"  Generated {len(results_queries)} queries")
        
        print("\n[2/3] Generating logical chain queries...")
        logical_raw = ai_logical_chain_query(user_input, n=n)
        logical_queries = parse_query_response(logical_raw)
        print(f"  Generated {len(logical_queries)} queries")
        
        print("\n[3/3] Generating future work queries...")
        future_raw = ai_future_work_query(user_input, n=n)
        future_queries = parse_query_response(future_raw)
        print(f"  Generated {len(future_queries)} queries")
        
        queries = {
            'user_input': user_input,
            'timestamp': timestamp,
            'results': results_queries,
            'logical': logical_queries,
            'future': future_queries
        }
    
    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(queries, f, indent=2, ensure_ascii=False)
    
    print(f"\nQueries saved to: {output_file}")
    
    return queries


def get_const_queries():
    """Return constant queries for stable testing."""
    return {
        'user_input': USER_INPUT,
        'timestamp': TIMESTAMP,
        'results': CONST_RESULT_QUERIES,
        'logical': CONST_LOGICAL_QUERIES,
        'future': CONST_FUTURE_QUERIES
    }


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Step 1: Query Generation")
    print("=" * 70)
    
    # Use constant queries for stable testing
    # Set use_const=False to generate new queries via AI
    queries = generate_queries(use_const=True)
    
    print("\n" + "=" * 70)
    print("Query Generation Complete!")
    print("=" * 70)
    print(f"\nResults queries: {len(queries['results'])}")
    print(f"Logical queries: {len(queries['logical'])}")
    print(f"Future queries: {len(queries['future'])}")

