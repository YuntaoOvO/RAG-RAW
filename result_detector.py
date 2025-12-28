"""
Result Detector Utility
=======================

Utility module for scanning and detecting existing results across
the project directories. Used by Streamlit pages to auto-detect
available files and refresh state.
"""

import os
import json
import glob
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


# Directory paths
BASE_DIR = '/home/yuntao/Mydata'
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
PYTHIA_WORKSPACE = os.path.join(BASE_DIR, 'pythia_workspace')
PYTHIA_SCRIPTS_DIR = os.path.join(PYTHIA_WORKSPACE, 'scripts')
PYTHIA_RESULTS_DIR = os.path.join(PYTHIA_WORKSPACE, 'results')
PYTHIA_EVENTS_DIR = os.path.join(PYTHIA_WORKSPACE, 'events')
BIB_DIR = os.path.join(BASE_DIR, 'bib')


def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get metadata about a file."""
    try:
        stat = os.stat(file_path)
        return {
            'path': file_path,
            'name': os.path.basename(file_path),
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'modified_timestamp': stat.st_mtime,
        }
    except OSError:
        return {
            'path': file_path,
            'name': os.path.basename(file_path),
            'size': 0,
            'modified': None,
            'modified_timestamp': 0,
        }


def scan_directory(directory: str, extensions: List[str] = None) -> List[Dict[str, Any]]:
    """
    Scan a directory for files with given extensions.
    
    Args:
        directory: Path to scan
        extensions: List of extensions to include (e.g., ['.json', '.tex'])
        
    Returns:
        List of file info dicts, sorted by modification time (newest first)
    """
    if not os.path.exists(directory):
        return []
    
    files = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path):
            if extensions is None or any(item.endswith(ext) for ext in extensions):
                files.append(get_file_info(item_path))
    
    # Sort by modification time, newest first
    files.sort(key=lambda x: x['modified_timestamp'], reverse=True)
    return files


def scan_results() -> Dict[str, List[Dict[str, Any]]]:
    """
    Scan all output directories for existing results.
    
    Returns:
        Dict with categorized results:
        - literature_reviews: .tex files in output/
        - simulation_results: .json files in pythia_workspace/results/
        - simulation_scripts: .py files in pythia_workspace/scripts/
        - query_results: query result .json files in output/
        - bib_files: .bib files in bib/
    """
    results = {
        'literature_reviews': [],
        'research_articles': [],
        'simulation_results': [],
        'simulation_scripts': [],
        'query_results': [],
        'bib_files': [],
        'all_tex_files': [],
        'all_json_files': [],
    }
    
    # Literature reviews (.tex in output/)
    tex_files = scan_directory(OUTPUT_DIR, ['.tex'])
    results['literature_reviews'] = [f for f in tex_files if 'review' in f['name'].lower() or 'draft' in f['name'].lower()]
    
    # Research articles (.tex files with 'research_article' in name)
    results['research_articles'] = [f for f in tex_files if 'research_article' in f['name'].lower()]
    
    results['all_tex_files'] = tex_files
    
    # Query results (.json in output/)
    json_output = scan_directory(OUTPUT_DIR, ['.json'])
    results['query_results'] = json_output
    results['all_json_files'] = json_output
    
    # Simulation results (.json in pythia_workspace/results/)
    results['simulation_results'] = scan_directory(PYTHIA_RESULTS_DIR, ['.json', '.png', '.pdf'])
    
    # Also check scripts dir for misplaced results
    scripts_json = scan_directory(PYTHIA_SCRIPTS_DIR, ['.json'])
    if scripts_json:
        results['simulation_results'].extend(scripts_json)
    
    # Simulation scripts (.py in pythia_workspace/scripts/)
    results['simulation_scripts'] = scan_directory(PYTHIA_SCRIPTS_DIR, ['.py'])
    
    # BibTeX files
    results['bib_files'] = scan_directory(BIB_DIR, ['.bib'])
    
    return results


def get_latest_results() -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Get the most recent file from each category.
    
    Returns:
        Dict with latest file from each category (or None if none exist)
    """
    all_results = scan_results()
    
    return {
        'latest_review': all_results['literature_reviews'][0] if all_results['literature_reviews'] else None,
        'latest_simulation': all_results['simulation_results'][0] if all_results['simulation_results'] else None,
        'latest_script': all_results['simulation_scripts'][0] if all_results['simulation_scripts'] else None,
        'latest_query': all_results['query_results'][0] if all_results['query_results'] else None,
    }


def load_json_result(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Load and parse a JSON result file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Parsed JSON data or None if failed
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, IOError):
        return None


def load_tex_content(file_path: str) -> Optional[str]:
    """
    Load content of a .tex file.
    
    Args:
        file_path: Path to .tex file
        
    Returns:
        File content or None if failed
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except (FileNotFoundError, IOError):
        return None


def get_results_summary() -> Dict[str, Any]:
    """
    Get a summary of all available results for display.
    
    Returns:
        Summary dict with counts and status
    """
    results = scan_results()
    latest = get_latest_results()
    
    return {
        'counts': {
            'literature_reviews': len(results['literature_reviews']),
            'simulation_results': len(results['simulation_results']),
            'simulation_scripts': len(results['simulation_scripts']),
            'query_results': len(results['query_results']),
        },
        'latest': latest,
        'has_reviews': len(results['literature_reviews']) > 0,
        'has_simulations': len(results['simulation_results']) > 0,
        'has_scripts': len(results['simulation_scripts']) > 0,
        'ready_for_article': len(results['literature_reviews']) > 0 and len(results['simulation_results']) > 0,
    }


def find_literature_review(timestamp: str = None) -> Optional[str]:
    """
    Find a literature review file, optionally by timestamp.
    
    Args:
        timestamp: Optional timestamp to match (e.g., '20250901_002253')
        
    Returns:
        Path to the review file or None
    """
    results = scan_results()
    reviews = results['literature_reviews']
    
    if not reviews:
        return None
    
    if timestamp:
        for review in reviews:
            if timestamp in review['name']:
                return review['path']
    
    # Return the latest
    return reviews[0]['path'] if reviews else None


def ensure_directories():
    """Ensure all required directories exist."""
    dirs = [
        OUTPUT_DIR,
        PYTHIA_WORKSPACE,
        PYTHIA_SCRIPTS_DIR,
        PYTHIA_RESULTS_DIR,
        PYTHIA_EVENTS_DIR,
        BIB_DIR,
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)


# For quick testing
if __name__ == '__main__':
    print("Scanning results...")
    summary = get_results_summary()
    print(f"\nResults Summary:")
    print(f"  Literature Reviews: {summary['counts']['literature_reviews']}")
    print(f"  Simulation Results: {summary['counts']['simulation_results']}")
    print(f"  Simulation Scripts: {summary['counts']['simulation_scripts']}")
    print(f"  Query Results: {summary['counts']['query_results']}")
    print(f"\nReady for article generation: {summary['ready_for_article']}")
    
    if summary['latest']['latest_review']:
        print(f"\nLatest Review: {summary['latest']['latest_review']['name']}")
    if summary['latest']['latest_simulation']:
        print(f"Latest Simulation: {summary['latest']['latest_simulation']['name']}")

