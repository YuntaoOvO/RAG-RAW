"""
Step 3: Vector Database Module
===============================

This module handles:
1. Creating a vector database from downloaded PDFs
2. Querying the database with generated queries
3. Saving query results to files

Usage:
    # Standalone execution with default constants
    python step3_vectordb.py
    
    # Import and use with custom parameters
    from step3_vectordb import create_db_and_query
    results = create_db_and_query(info=custom_info, queries=custom_queries)
"""

import os
import re
import json
from tqdm import tqdm

from rag_core import load_pdfs_info
from FlagEmbedding import BGEM3FlagModel
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb


# ============================================================================
# Stable Configuration for Testing/Showcase
# ============================================================================

TIMESTAMP = '20250901_002253'
MODEL_PATH = '/home/yuntao/bge-m3'
DOWNLOAD_DIR = './download'
PERSIST_DIRECTORY = './spinodal'
OUTPUT_DIR = './output'

# Paper info for stable testing
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
    """Sanitize filename by removing illegal characters."""
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    if len(filename) > 100:
        filename = filename[:100]
    return filename


def sanitize_metadata(meta):
    """
    Sanitize metadata for ChromaDB compatibility.
    ChromaDB only supports str, int, float, bool types.
    """
    if meta is None or not isinstance(meta, dict):
        return {'doc_id': 'unknown', 'source': 'unknown', 'page': 0}
    
    sanitized = {}
    for key, value in meta.items():
        if value is None:
            sanitized[key] = 'null'
        elif isinstance(value, (str, int, float, bool)):
            sanitized[key] = value
        else:
            sanitized[key] = str(value)
    
    if 'doc_id' not in sanitized:
        sanitized['doc_id'] = 'unknown'
    if 'source' not in sanitized:
        sanitized['source'] = 'unknown'  
    if 'page' not in sanitized:
        sanitized['page'] = 0
        
    return sanitized


def ensure_output_dir(output_dir=OUTPUT_DIR):
    """Ensure output directory exists."""
    os.makedirs(output_dir, exist_ok=True)


def load_queries_from_file(queries_file):
    """Load queries from a JSON file."""
    with open(queries_file, 'r', encoding='utf-8') as f:
        return json.load(f)


# ============================================================================
# Vector Database Creation
# ============================================================================

def create_temp_db(info, dbname=None, persist_directory=PERSIST_DIRECTORY,
                   download_dir=DOWNLOAD_DIR, model_path=MODEL_PATH,
                   chunk_size=1024, chunk_overlap=20, batch_size=4, max_length=1024,
                   timestamp=None):
    """
    Create a temporary vector database from PDFs.
    
    Args:
        info: List of paper info dicts with 'doc_id' keys
        dbname: Database collection name (auto-generated if None)
        persist_directory: Directory to persist the database
        download_dir: Directory containing PDF files
        model_path: Path to the BGE-M3 model
        chunk_size: Text chunk size for splitting
        chunk_overlap: Overlap between chunks
        batch_size: Batch size for embedding
        max_length: Maximum sequence length
        timestamp: Timestamp for naming (uses TIMESTAMP if None)
        
    Returns:
        Collection name
    """
    if timestamp is None:
        timestamp = TIMESTAMP
    
    if dbname is None:
        dbname = f"temp_{timestamp}"
    
    print(f"Creating vector database: {dbname}")
    print(f"Model path: {model_path}")
    print(f"Persist directory: {persist_directory}")
    
    # Load embedding model
    print("\nLoading BGE-M3 model...")
    model = BGEM3FlagModel(model_path, model_kwargs={'device': 'cuda'}, use_fp16=True)
    
    # Create text splitter
    r_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap
    )
    
    # Load PDFs
    print(f"\nLoading PDFs from {download_dir}...")
    doc, failed_files = load_pdfs_info(download_dir, info=info)
    print(f"Loaded {len(doc)} pages, {len(failed_files)} files failed")
    
    if failed_files:
        print(f"Failed files: {failed_files}")
    
    # Create source to doc_id mapping
    source_to_docid = {}
    for item in info:
        arxiv_id = item['doc_id']
        clean_id = sanitize_filename(arxiv_id.split('/')[-1])
        file_path = os.path.join(download_dir, f"{clean_id}.pdf")
        normalized_path = os.path.normpath(file_path)
        source_to_docid[normalized_path] = arxiv_id
    
    # Add doc_id to each page's metadata
    print("\nAdding doc_id to metadata...")
    for idx, page in enumerate(doc):
        if page.metadata is None:
            page.metadata = {}
        
        source_path = page.metadata.get('source', '')
        normalized_source = os.path.normpath(source_path)
        
        matched = False
        if normalized_source in source_to_docid:
            page.metadata['doc_id'] = source_to_docid[normalized_source]
            matched = True
        else:
            for norm_path, doc_id in source_to_docid.items():
                if os.path.basename(normalized_source) == os.path.basename(norm_path):
                    page.metadata['doc_id'] = doc_id
                    matched = True
                    break
        
        if not matched:
            page.metadata['doc_id'] = 'unknown'
    
    # Split documents and prepare metadata
    print("\nSplitting documents...")
    splits = []
    metas = []
    
    for page in tqdm(doc, desc="Splitting"):
        page_splits = r_splitter.split_text(page.page_content)
        splits.extend(page_splits)
        for _ in page_splits:
            clean_meta = sanitize_metadata(page.metadata)
            metas.append(clean_meta)
    
    print(f"Total chunks: {len(splits)}")
    
    # Guard: Check if there's anything to embed
    if len(splits) == 0:
        error_msg = f"No text chunks to embed. All {len(failed_files)} PDF files failed to load from '{download_dir}'. " \
                    f"Failed files: {failed_files[:5]}{'...' if len(failed_files) > 5 else ''}"
        print(f"\n❌ ERROR: {error_msg}")
        raise ValueError(error_msg)
    
    # Create embeddings
    print("\nCreating embeddings...")
    embeddings = model.encode(splits, batch_size=batch_size, max_length=max_length)['dense_vecs']
    print(f"Created {len(embeddings)} embeddings")
    
    # Store in ChromaDB
    print("\nStoring in ChromaDB...")
    client = chromadb.PersistentClient(path=persist_directory)
    collection = client.get_or_create_collection(name=dbname)
    
    collection.add(
        ids=[f"id{j}" for j in range(len(splits))],
        documents=splits,
        metadatas=metas,
        embeddings=embeddings
    )
    
    print(f"\nDatabase '{dbname}' created successfully!")
    print(f"Total documents: {collection.count()}")
    
    return dbname


# ============================================================================
# Vector Database Querying
# ============================================================================

def query_sentence(questions, collection_name, top_k=50,
                   persist_directory=PERSIST_DIRECTORY,
                   model_path=MODEL_PATH,
                   batch_size=16, max_length=1024,
                   return_metadata=True):
    """
    Query the vector database with questions.
    
    Args:
        questions: Query string or list of query strings
        collection_name: Name of the collection to query
        top_k: Number of results to return per query
        persist_directory: Database directory
        model_path: Path to the BGE-M3 model
        batch_size: Batch size for embedding
        max_length: Maximum sequence length
        return_metadata: Whether to return metadata
        
    Returns:
        Tuple of (texts, metadata) if return_metadata=True, else just texts
    """
    client = chromadb.PersistentClient(path=persist_directory)
    collection = client.get_or_create_collection(name=collection_name)
    
    print(f"Querying collection '{collection_name}' ({collection.count()} documents)")
    
    # Load model
    model = BGEM3FlagModel(model_path, model_kwargs={'device': 'cuda'}, use_fp16=True)
    
    # Parse questions
    if isinstance(questions, str):
        try:
            questions = json.loads(questions)
        except:
            questions = [questions]
    
    print(f"Processing {len(questions)} queries...")
    
    # Create embeddings for queries
    embeddings = model.encode(questions, batch_size=batch_size, max_length=max_length)['dense_vecs']
    
    # Query database
    results = collection.query(query_embeddings=embeddings, n_results=top_k)
    
    # Extract results
    res_txt = []
    res_meta = []
    
    for doc_list, meta_list in zip(results["documents"], results.get("metadatas", [])):
        res_txt.extend(doc_list)
        if return_metadata:
            res_meta.extend(meta_list)
    
    print(f"Retrieved {len(res_txt)} results")
    
    if return_metadata:
        return res_txt, res_meta
    else:
        return res_txt


def query_all(queries_dict, collection_name, top_k=19,
              persist_directory=PERSIST_DIRECTORY,
              model_path=MODEL_PATH):
    """
    Query database with all three query types.
    
    Args:
        queries_dict: Dict with 'results', 'logical', 'future' query lists
        collection_name: Name of the collection
        top_k: Results per query
        persist_directory: Database directory
        model_path: Model path
        
    Returns:
        Dict with 'results', 'logical', 'future' query results
    """
    print("\n[1/3] Querying with results queries...")
    results_txt, results_meta = query_sentence(
        queries_dict['results'],
        collection_name=collection_name,
        persist_directory=persist_directory,
        model_path=model_path,
        top_k=top_k,
        return_metadata=True
    )
    
    print("\n[2/3] Querying with logical queries...")
    logical_txt = query_sentence(
        queries_dict['logical'],
        collection_name=collection_name,
        persist_directory=persist_directory,
        model_path=model_path,
        top_k=top_k,
        return_metadata=False
    )
    
    print("\n[3/3] Querying with future work queries...")
    future_txt = query_sentence(
        queries_dict['future'],
        collection_name=collection_name,
        persist_directory=persist_directory,
        model_path=model_path,
        top_k=top_k,
        return_metadata=False
    )
    
    return {
        'results_txt': results_txt,
        'results_meta': results_meta,
        'logical_txt': logical_txt,
        'future_txt': future_txt
    }


# ============================================================================
# Main Functions
# ============================================================================

def save_query_results(query_results, output_dir=OUTPUT_DIR, timestamp=None):
    """Save query results to JSON files."""
    if timestamp is None:
        timestamp = TIMESTAMP
    
    ensure_output_dir(output_dir)
    
    # Save results
    results_file = os.path.join(output_dir, f"results_txt_{timestamp}.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'texts': query_results['results_txt'],
            'metadata': query_results['results_meta']
        }, f, indent=2, ensure_ascii=False)
    print(f"Saved: {results_file}")
    
    # Save logical
    logical_file = os.path.join(output_dir, f"logical_txt_{timestamp}.json")
    with open(logical_file, 'w', encoding='utf-8') as f:
        json.dump({'texts': query_results['logical_txt']}, f, indent=2, ensure_ascii=False)
    print(f"Saved: {logical_file}")
    
    # Save future
    future_file = os.path.join(output_dir, f"future_txt_{timestamp}.json")
    with open(future_file, 'w', encoding='utf-8') as f:
        json.dump({'texts': query_results['future_txt']}, f, indent=2, ensure_ascii=False)
    print(f"Saved: {future_file}")
    
    return {
        'results_file': results_file,
        'logical_file': logical_file,
        'future_file': future_file
    }


def create_db_and_query(info=None, queries=None, queries_file=None,
                        timestamp=None, model_path=MODEL_PATH,
                        download_dir=DOWNLOAD_DIR,
                        persist_directory=PERSIST_DIRECTORY,
                        output_dir=OUTPUT_DIR,
                        skip_db_creation=False,
                        top_k=19):
    """
    Main function to create database and query it.
    
    Args:
        info: Paper info list (uses INFO constant if None)
        queries: Query dict (loads from file if None)
        queries_file: Path to queries JSON file
        timestamp: Timestamp for naming
        model_path: Path to BGE-M3 model
        download_dir: PDF directory
        persist_directory: Database directory
        output_dir: Output directory
        skip_db_creation: If True, skip DB creation and use existing
        top_k: Results per query
        
    Returns:
        Dict with query results and file paths
    """
    if timestamp is None:
        timestamp = TIMESTAMP
    
    if info is None:
        info = INFO
    
    collection_name = f"temp_{timestamp}"
    
    # Create database if needed
    if not skip_db_creation:
        print("\n" + "=" * 50)
        print("Creating Vector Database")
        print("=" * 50)
        create_temp_db(
            info=info,
            dbname=collection_name,
            persist_directory=persist_directory,
            download_dir=download_dir,
            model_path=model_path,
            timestamp=timestamp
        )
    else:
        print(f"Skipping DB creation, using existing: {collection_name}")
    
    # Load queries
    if queries is None:
        if queries_file is None:
            queries_file = os.path.join(output_dir, f"queries_{timestamp}.json")
        
        if os.path.exists(queries_file):
            print(f"\nLoading queries from: {queries_file}")
            queries = load_queries_from_file(queries_file)
        else:
            # Use constant queries
            print("\nUsing constant queries (no queries file found)")
            from step1_query_gen import get_const_queries
            queries = get_const_queries()
    
    # Query database
    print("\n" + "=" * 50)
    print("Querying Vector Database")
    print("=" * 50)
    query_results = query_all(
        queries,
        collection_name=collection_name,
        persist_directory=persist_directory,
        model_path=model_path,
        top_k=top_k
    )
    
    # Save results
    print("\n" + "=" * 50)
    print("Saving Query Results")
    print("=" * 50)
    file_paths = save_query_results(query_results, output_dir=output_dir, timestamp=timestamp)
    
    return {
        'query_results': query_results,
        'file_paths': file_paths,
        'collection_name': collection_name
    }


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Step 3: Vector Database Creation and Querying")
    print("=" * 70)
    
    # Create database and query
    # Set skip_db_creation=True if database already exists
    result = create_db_and_query(
        info=INFO,
        skip_db_creation=False,  # Set to True to skip DB creation
        top_k=19
    )
    
    print("\n" + "=" * 70)
    print("Step 3 Complete!")
    print("=" * 70)
    print(f"\nCollection: {result['collection_name']}")
    print(f"\nOutput files:")
    for name, path in result['file_paths'].items():
        print(f"  {name}: {path}")
    print(f"\nResults summary:")
    print(f"  Results texts: {len(result['query_results']['results_txt'])}")
    print(f"  Logical texts: {len(result['query_results']['logical_txt'])}")
    print(f"  Future texts: {len(result['query_results']['future_txt'])}")

