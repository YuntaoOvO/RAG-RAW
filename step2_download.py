"""
Step 2: PDF Download Module
============================

This module handles downloading PDFs from arXiv based on paper info.
Paper info can come from:
1. Constant INFO list (for stable testing)
2. Parsed from a .bib file

Usage:
    # Standalone execution with default constants
    python step2_download.py
    
    # Import and use with custom info
    from step2_download import download_papers, parse_bib_file
    info = parse_bib_file("topic.bib")
    download_papers(info=info)
"""

import os
import re
import time
import requests


# ============================================================================
# Stable Configuration for Testing/Showcase
# ============================================================================

TIMESTAMP = '20250901_002253'
DOWNLOAD_DIR = './download'

# Paper info list for stable testing
INFO = [
    {'doc_id': '0903.4335'},
    {'doc_id': '2408.09679'},
    {'doc_id': '2409.16525'},
    {'doc_id': '2311.08277'},
    {'doc_id': '2407.16963'},
    {'doc_id': 'hep-ph/0009171v2'},
    {'doc_id': '2409.13961'},
    {'doc_id': '1302.2956'},
    {'doc_id': 'hep-ph/0308271v1'},
    {'doc_id': '1905.12544'},
    {'doc_id': '1007.1448'}
]


# ============================================================================
# Utility Functions
# ============================================================================

def sanitize_filename(filename):
    """
    Sanitize filename by removing illegal characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized safe filename
    """
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    if len(filename) > 100:
        filename = filename[:100]
    return filename


def ensure_download_dir(download_dir=DOWNLOAD_DIR):
    """Ensure download directory exists."""
    os.makedirs(download_dir, exist_ok=True)


# ============================================================================
# BibTeX Parsing Functions
# ============================================================================

def parse_bib_file(bib_file_path):
    """
    Parse a .bib file and extract arXiv doc_ids.
    
    Args:
        bib_file_path: Path to the .bib file
        
    Returns:
        List of dicts with 'doc_id' keys, e.g., [{'doc_id': '0903.4335'}, ...]
    """
    info = []
    
    if not os.path.exists(bib_file_path):
        print(f"Warning: BibTeX file not found: {bib_file_path}")
        return info
    
    with open(bib_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match arXiv IDs in various formats
    # Matches: eprint = {2408.09679}, arxiv = {hep-ph/0009171}, etc.
    eprint_pattern = r'eprint\s*=\s*[{"]([^}"]+)[}"]'
    arxiv_pattern = r'arxiv\s*=\s*[{"]([^}"]+)[}"]'
    
    # Also match from URLs like https://arxiv.org/abs/2408.09679
    url_pattern = r'arxiv\.org/(?:abs|pdf)/([^\s},]+)'
    
    # Find all matches
    eprints = re.findall(eprint_pattern, content, re.IGNORECASE)
    arxivs = re.findall(arxiv_pattern, content, re.IGNORECASE)
    urls = re.findall(url_pattern, content, re.IGNORECASE)
    
    # Combine all found IDs
    all_ids = set()
    for id_list in [eprints, arxivs, urls]:
        for doc_id in id_list:
            # Clean up the ID
            doc_id = doc_id.strip().rstrip('.pdf')
            if doc_id:
                all_ids.add(doc_id)
    
    # Convert to info format
    for doc_id in all_ids:
        info.append({'doc_id': doc_id})
    
    print(f"Parsed {len(info)} arXiv IDs from {bib_file_path}")
    
    return info


def extract_arxiv_id_from_bibtex_entry(entry_text):
    """
    Extract arXiv ID from a single BibTeX entry.
    
    Args:
        entry_text: Text of a single BibTeX entry
        
    Returns:
        arXiv ID string or None
    """
    # Try eprint field first
    match = re.search(r'eprint\s*=\s*[{"]([^}"]+)[}"]', entry_text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # Try arxiv field
    match = re.search(r'arxiv\s*=\s*[{"]([^}"]+)[}"]', entry_text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # Try URL field
    match = re.search(r'arxiv\.org/(?:abs|pdf)/([^\s},]+)', entry_text, re.IGNORECASE)
    if match:
        return match.group(1).strip().rstrip('.pdf')
    
    return None


# ============================================================================
# PDF Download Functions
# ============================================================================

def download_pdf(info, download_dir=DOWNLOAD_DIR, delay=6, timeout=30):
    """
    Download PDFs from arXiv based on paper info list.
    
    Args:
        info: List of dicts with 'doc_id' keys
        download_dir: Directory to save PDFs
        delay: Delay between downloads in seconds (to respect arXiv rate limits)
        timeout: Request timeout in seconds
        
    Returns:
        download_dir if any downloads successful, None otherwise
    """
    if not info:
        raise ValueError("Paper info list is empty")

    ensure_download_dir(download_dir)
    
    success_count = 0
    for paper in info:
        print(f"Processing paper: {paper}")
        try:
            arxiv_id = paper.get('doc_id')
            if not arxiv_id:
                print(f"  No doc_id found in paper info: {paper}")
                continue

            clean_id = sanitize_filename(arxiv_id.split('/')[-1])
            file_path = os.path.join(download_dir, f"{clean_id}.pdf")

            if os.path.exists(file_path):
                success_count += 1
                print(f"  Already exists: {file_path}")
                continue            

            print(f"  Downloading from arXiv...")
            response = requests.get(
                f"https://arxiv.org/pdf/{arxiv_id}.pdf", 
                timeout=timeout,
                headers={'Connection': 'close'}
            )
            response.raise_for_status()

            with open(file_path, "wb") as f:
                f.write(response.content)

            success_count += 1
            print(f"  Downloaded: {file_path}")
            
            # Respect arXiv rate limits
            if delay > 0:
                time.sleep(delay)
                
        except requests.exceptions.RequestException as e:
            print(f"  Download failed: {e}")
            continue
        except Exception as e:
            print(f"  Error: {e}")
            continue
    
    print(f"\nTotal downloaded/available: {success_count}/{len(info)}")
    return download_dir if success_count > 0 else None


def download_papers(info=None, bib_file=None, download_dir=DOWNLOAD_DIR, delay=6):
    """
    Main download function with flexible input options.
    
    Args:
        info: List of paper info dicts (optional)
        bib_file: Path to .bib file to parse (optional)
        download_dir: Directory to save PDFs
        delay: Delay between downloads
        
    Returns:
        Tuple of (download_dir, info_list) if successful
    """
    # Determine paper info source
    if info is None and bib_file is not None:
        info = parse_bib_file(bib_file)
    elif info is None:
        info = INFO  # Use constant
    
    if not info:
        print("Error: No paper info available")
        return None, []
    
    print(f"\nPreparing to download {len(info)} papers...")
    print(f"Download directory: {download_dir}")
    
    result_dir = download_pdf(info, download_dir=download_dir, delay=delay)
    
    return result_dir, info


def get_info_from_bib_or_const(bib_file=None):
    """
    Get paper info from bib file or return constants.
    
    Args:
        bib_file: Optional path to .bib file
        
    Returns:
        List of paper info dicts
    """
    if bib_file and os.path.exists(bib_file):
        return parse_bib_file(bib_file)
    return INFO


def get_const_info():
    """Return constant info for stable testing."""
    return INFO.copy()


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Step 2: PDF Download")
    print("=" * 70)
    
    # Use constant info for stable testing
    # You can also pass bib_file="topic.bib" to parse from bib file
    result_dir, info = download_papers(info=INFO)
    
    print("\n" + "=" * 70)
    print("PDF Download Complete!")
    print("=" * 70)
    
    if result_dir:
        print(f"\nPDFs available in: {result_dir}")
        print(f"Total papers: {len(info)}")
        
        # List downloaded files
        pdf_files = [f for f in os.listdir(result_dir) if f.endswith('.pdf')]
        print(f"PDF files: {len(pdf_files)}")
        for pdf in sorted(pdf_files):
            print(f"  - {pdf}")
    else:
        print("\nNo papers were downloaded successfully.")

