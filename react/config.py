"""
ReAct Framework Configuration
==============================

Central configuration file for all ReAct components.
"""

import os

# ============================================================================
# Directory Paths
# ============================================================================

# Base directory
BASE_DIR = '/home/yuntao/Mydata'

# Output directories
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
PYTHIA_WORKSPACE = os.path.join(BASE_DIR, 'pythia_workspace')
PYTHIA_SCRIPTS_DIR = os.path.join(PYTHIA_WORKSPACE, 'scripts')
PYTHIA_EVENTS_DIR = os.path.join(PYTHIA_WORKSPACE, 'events')
PYTHIA_RESULTS_DIR = os.path.join(PYTHIA_WORKSPACE, 'results')
PYTHIA_FIGURES_DIR = os.path.join(PYTHIA_WORKSPACE, 'figures')

# React directory
REACT_DIR = os.path.join(BASE_DIR, 'react')

# ============================================================================
# Timestamp (stable for testing)
# ============================================================================

TIMESTAMP = '20250901_002253'

# ============================================================================
# Model Configuration
# ============================================================================

# Embedding model path
BGE_MODEL_PATH = '/home/yuntao/bge-m3'

# API Configuration (uses environment variables)
API_KEY_ENV = 'MIMO_API_KEY'
API_BASE_URL = 'https://api.xiaomimimo.com/v1'
MODEL_NAME = 'mimo-v2-flash'

# ============================================================================
# Code Execution Configuration
# ============================================================================

# Maximum execution time for Python scripts (seconds)
CODE_EXECUTION_TIMEOUT = 300

# Maximum output size (characters)
MAX_OUTPUT_SIZE = 50000

# Allowed import modules for generated code
ALLOWED_IMPORTS = [
    'pythia8',
    'numpy',
    'matplotlib',
    'scipy',
    'pandas',
    'json',
    'os',
    'sys',
    'math',
    'random',
    'datetime',
    'collections',
    'itertools',
    'functools',
]

# ============================================================================
# ReAct Agent Configuration
# ============================================================================

# Maximum iterations before stopping
MAX_ITERATIONS = 20

# Maximum retries for tool execution
MAX_TOOL_RETRIES = 3

# Verbose output
VERBOSE = True

# ============================================================================
# File Operation Configuration
# ============================================================================

# Allowed file extensions for reading
READABLE_EXTENSIONS = ['.tex', '.py', '.txt', '.json', '.md', '.csv', '.dat']

# Allowed file extensions for writing
WRITABLE_EXTENSIONS = ['.tex', '.py', '.txt', '.json', '.md']

# Maximum file size for reading (bytes)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# ============================================================================
# Pythia8 Configuration
# ============================================================================

# Default beam settings
PYTHIA_DEFAULT_BEAM = 'p p'
PYTHIA_DEFAULT_ENERGY = 13000  # GeV (LHC energy)

# Default number of events
PYTHIA_DEFAULT_NEVENTS = 10000

# Common process types
PYTHIA_PROCESSES = {
    'qcd': 'HardQCD:all = on',
    'minbias': 'SoftQCD:all = on',
    'higgs': 'HiggsSM:gg2H = on',
    'top': 'Top:gg2ttbar = on',
    'w': 'WeakSingleBoson:ffbar2W = on',
    'z': 'WeakSingleBoson:ffbar2gmZ = on',
    'dijet': 'HardQCD:gg2gg = on\nHardQCD:gg2qqbar = on',
}

# ============================================================================
# Helper Functions
# ============================================================================

def ensure_directories():
    """Create all necessary directories."""
    dirs = [
        OUTPUT_DIR,
        PYTHIA_WORKSPACE,
        PYTHIA_SCRIPTS_DIR,
        PYTHIA_EVENTS_DIR,
        PYTHIA_RESULTS_DIR,
        PYTHIA_FIGURES_DIR,
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def get_timestamp():
    """Get current timestamp or use stable timestamp."""
    return TIMESTAMP


def get_output_path(filename, subdir=None):
    """Get full path for an output file."""
    if subdir:
        base = os.path.join(OUTPUT_DIR, subdir)
        os.makedirs(base, exist_ok=True)
        return os.path.join(base, filename)
    return os.path.join(OUTPUT_DIR, filename)


def get_pythia_script_path(script_name):
    """Get full path for a Pythia script."""
    if not script_name.endswith('.py'):
        script_name += '.py'
    return os.path.join(PYTHIA_SCRIPTS_DIR, script_name)


def get_pythia_result_path(result_name):
    """Get full path for a Pythia result file."""
    return os.path.join(PYTHIA_RESULTS_DIR, result_name)



