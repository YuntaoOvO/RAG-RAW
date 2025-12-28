"""
ReAct Particle Physics Research System - Streamlit Application
===============================================================

A comprehensive Streamlit app with 4 pages:
1. Literature Review Pipeline - Run the 4-step pipeline
2. ReAct Agent Interface - Interactive AI agent
3. Article Generation - Generate research articles
4. Workflow Visualization - Visual workflow diagram
"""

import streamlit as st
import os
import sys
import json
import time
import re
import html
from datetime import datetime

# Add project root to path
sys.path.insert(0, '/home/yuntao/Mydata')

# Page configuration
st.set_page_config(
    page_title="ReAct Physics Research",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Apple Design System
st.markdown("""
<style>
    /* Apple SF Pro fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=SF+Mono:wght@400;500&display=swap');
    
    /* CSS Variables - Light Theme (Default) */
    :root {
        --nav-height: 52px;
        --primary-color: #0071e3;
        --primary-hover: #0077ed;
        --text-primary: #1d1d1f;
        --text-secondary: rgba(0, 0, 0, 0.56);
        --text-muted: rgba(0, 0, 0, 0.36);
        --bg-primary: #fafafa;
        --bg-secondary: #ffffff;
        --bg-tertiary: #f5f5f7;
        --glass-bg: rgba(255, 255, 255, 0.72);
        --glass-border: rgba(0, 0, 0, 0.08);
        --border-color: rgba(0, 0, 0, 0.1);
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.04);
        --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.08);
        --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.12);
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --transition: cubic-bezier(0.4, 0, 0.2, 1);
        --code-bg: #f5f5f7;
        --thought-bg: rgba(33, 150, 243, 0.08);
        --thought-border: #2196f3;
        --action-bg: rgba(0, 150, 136, 0.08);
        --action-border: #009688;
        --observation-bg: rgba(158, 158, 158, 0.08);
        --observation-border: #9e9e9e;
        --success-bg: rgba(52, 199, 89, 0.08);
        --success-border: #34c759;
        --error-bg: rgba(255, 59, 48, 0.08);
        --error-border: #ff3b30;
    }
    
    /* Dark Theme (Auto-switch based on system preference) */
    @media (prefers-color-scheme: dark) {
        :root {
            --primary-color: #0a84ff;
            --primary-hover: #409cff;
            --text-primary: #f5f5f7;
            --text-secondary: rgba(255, 255, 255, 0.6);
            --text-muted: rgba(255, 255, 255, 0.36);
            --bg-primary: #1c1c1e;
            --bg-secondary: #2c2c2e;
            --bg-tertiary: #3a3a3c;
            --glass-bg: rgba(44, 44, 46, 0.72);
            --glass-border: rgba(255, 255, 255, 0.08);
            --border-color: rgba(255, 255, 255, 0.1);
            --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.2);
            --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.3);
            --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.4);
            --code-bg: #2c2c2e;
            --thought-bg: rgba(33, 150, 243, 0.15);
            --action-bg: rgba(0, 150, 136, 0.15);
            --observation-bg: rgba(158, 158, 158, 0.1);
            --success-bg: rgba(52, 199, 89, 0.15);
            --error-bg: rgba(255, 59, 48, 0.15);
        }
        
        .stApp {
            background: linear-gradient(180deg, #1c1c1e 0%, #000000 100%) !important;
        }
        
        .stCodeBlock {
            background: var(--code-bg) !important;
            border-color: var(--border-color) !important;
        }
    }
    
    /* Base theme */
    .stApp {
        background: linear-gradient(180deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Inter', 'Helvetica Neue', sans-serif;
        -webkit-font-smoothing: antialiased;
        color: var(--text-primary);
    }
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
    
    /* Glass card effect */
    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: saturate(180%) blur(20px);
        -webkit-backdrop-filter: saturate(180%) blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow-md);
        transition: all 0.4s var(--transition);
    }
    
    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
        border-color: rgba(0, 113, 227, 0.2);
    }
    
    /* Gradient text - Apple style */
    .gradient-title {
        background: linear-gradient(135deg, #1d1d1f 0%, #86868b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.015em;
        margin-bottom: 0.5rem;
    }
    
    /* Step cards */
    .step-card {
        background: var(--glass-bg);
        backdrop-filter: saturate(180%) blur(20px);
        -webkit-backdrop-filter: saturate(180%) blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-md);
        padding: 1.25rem;
        text-align: center;
        transition: all 0.3s var(--transition);
        box-shadow: var(--shadow-sm);
    }
    
    .step-card h4 {
        color: var(--text-primary);
        font-weight: 600;
        letter-spacing: -0.01em;
    }
    
    .step-card p {
        color: var(--text-secondary) !important;
    }
    
    .step-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-md);
        border-color: rgba(0, 113, 227, 0.3);
    }
    
    .step-card.completed {
        border-color: #34c759;
        background: rgba(52, 199, 89, 0.08);
    }
    
    .step-card.active {
        border-color: var(--primary-color);
        background: rgba(0, 113, 227, 0.08);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(0, 113, 227, 0.3); }
        50% { box-shadow: 0 0 20px 5px rgba(0, 113, 227, 0.15); }
    }
    
    /* Code blocks */
    .stCodeBlock {
        background: #f5f5f7 !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
        border-radius: var(--radius-sm) !important;
    }
    
    /* Buttons - Apple pill style */
    .stButton > button {
        background: var(--primary-color);
        color: white;
        border: none;
        border-radius: 980px;
        padding: 0.6rem 1.5rem;
        font-weight: 500;
        font-size: 17px;
        transition: all 0.3s var(--transition);
    }
    
    .stButton > button:hover {
        background: #0077ed;
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(0, 113, 227, 0.3);
    }
    
    /* Secondary buttons */
    .stButton > button[kind="secondary"] {
        background: transparent;
        color: var(--primary-color);
        border: 1px solid var(--primary-color);
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: var(--primary-color);
        color: white;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(251, 251, 253, 0.95);
        backdrop-filter: saturate(180%) blur(20px);
        border-right: 1px solid rgba(0, 0, 0, 0.1);
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: var(--text-primary);
    }
    
    /* Text colors */
    .stMarkdown {
        color: var(--text-primary);
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
        letter-spacing: -0.01em;
    }
    
    p, span, div {
        color: var(--text-primary);
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: var(--glass-bg);
        border-radius: var(--radius-sm);
        color: var(--text-primary);
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--primary-color), #00a8ff);
        border-radius: 100px;
    }
    
    /* Metric cards */
    .metric-card {
        background: var(--glass-bg);
        backdrop-filter: saturate(180%) blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-md);
        padding: 1.25rem;
        text-align: center;
        box-shadow: var(--shadow-sm);
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--primary-color);
    }
    
    .metric-label {
        color: var(--text-secondary);
        font-size: 0.9rem;
    }
    
    /* LaTeX preview - full scrollable view */
    .latex-preview {
        background: #ffffff;
        border: 1px solid rgba(0, 0, 0, 0.1);
        border-radius: var(--radius-sm);
        padding: 1.25rem;
        max-height: 600px;
        overflow-y: auto;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 13px;
        line-height: 1.5;
        white-space: pre-wrap;
        word-wrap: break-word;
        font-family: 'SF Mono', 'Menlo', 'Consolas', monospace;
        font-size: 0.85rem;
        color: var(--text-primary);
        max-height: 500px;
        overflow-y: auto;
        line-height: 1.6;
        white-space: pre-wrap;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.04);
    }
    
    /* Chat messages */
    .chat-message {
        padding: 1rem 1.25rem;
        border-radius: var(--radius-md);
        margin-bottom: 0.75rem;
    }
    
    .chat-user {
        background: var(--primary-color);
        color: white;
        margin-left: 20%;
    }
    
    .chat-agent {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        margin-right: 20%;
        color: var(--text-primary);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: var(--glass-bg);
        border-radius: 980px;
        padding: 0.5rem 1.25rem;
        color: var(--text-primary);
        border: 1px solid var(--glass-border);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--primary-color) !important;
        color: white !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #ffffff;
        border: 1px solid rgba(0, 0, 0, 0.1);
        border-radius: var(--radius-sm);
        color: var(--text-primary);
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.15);
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        background: #ffffff;
        border: 1px solid rgba(0, 0, 0, 0.1);
        border-radius: var(--radius-sm);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: var(--primary-color);
        font-weight: 600;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary);
    }
    
    /* Download buttons */
    .stDownloadButton > button {
        background: transparent;
        color: var(--primary-color);
        border: 1px solid var(--primary-color);
        border-radius: 980px;
    }
    
    .stDownloadButton > button:hover {
        background: var(--primary-color);
        color: white;
    }
    
    /* Checkbox */
    .stCheckbox {
        color: var(--text-primary);
    }
    
    /* Success/Warning/Error messages */
    .stSuccess {
        background: rgba(52, 199, 89, 0.1);
        border: 1px solid rgba(52, 199, 89, 0.3);
        color: #1d7d3c;
    }
    
    .stWarning {
        background: rgba(255, 149, 0, 0.1);
        border: 1px solid rgba(255, 149, 0, 0.3);
        color: #996300;
    }
    
    .stError {
        background: rgba(255, 59, 48, 0.1);
        border: 1px solid rgba(255, 59, 48, 0.3);
        color: #c41e11;
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Smooth animations */
    * {
        transition: background-color 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }
</style>
""", unsafe_allow_html=True)

# Constants
TIMESTAMP = '20250901_002253'
OUTPUT_DIR = './output'
PYTHIA_WORKSPACE = './pythia_workspace'


# ============================================================================
# Helper Functions
# ============================================================================

def count_text_length(text: str, is_chinese: bool = False) -> int:
    """
    Count text length appropriately for different languages.
    
    Args:
        text: The text to count
        is_chinese: If True, count Chinese characters; otherwise count words
        
    Returns:
        Character count for Chinese, word count for English
    """
    if is_chinese:
        # Count Chinese characters (CJK Unified Ideographs range)
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        return len(chinese_chars)
    else:
        # Count English words
        return len(text.split())


# Session state initialization
if 'pipeline_status' not in st.session_state:
    st.session_state.pipeline_status = {
        'step1': 'pending',
        'step2': 'pending', 
        'step3': 'pending',
        'step4': 'pending'
    }
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'generated_review' not in st.session_state:
    st.session_state.generated_review = None
if 'generated_review_zh' not in st.session_state:
    st.session_state.generated_review_zh = None
if 'future_work_items' not in st.session_state:
    st.session_state.future_work_items = []
# ReAct Agent workflow state
if 'react_running' not in st.session_state:
    st.session_state.react_running = False
if 'react_trace' not in st.session_state:
    st.session_state.react_trace = []
if 'react_final_answer' not in st.session_state:
    st.session_state.react_final_answer = None
if 'react_workflow_step' not in st.session_state:
    st.session_state.react_workflow_step = 0
if 'react_stop_requested' not in st.session_state:
    st.session_state.react_stop_requested = False


# ============================================================================
# Sidebar Navigation - Apple Style
# ============================================================================
with st.sidebar:
    st.markdown("""
    <div style="padding: 0.5rem 0;">
        <h1 style="font-size: 21px; font-weight: 600; color: #1d1d1f; letter-spacing: -0.02em; margin: 0;">
            ⚛️ RAG System
        </h1>
        <p style="font-size: 12px; color: rgba(0,0,0,0.56); margin: 4px 0 0 0;">
            三阶段文献综述 · ReAct研究系统
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["📚 Literature Review", "🤖 ReAct Agent", "📝 Article Generation", "🔄 Workflow"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("##### 📊 Pipeline Status")
    
    # Status indicators with Apple colors
    status_icons = {'pending': '○', 'running': '◐', 'completed': '●', 'error': '✕'}
    status_colors = {'pending': '#86868b', 'running': '#0071e3', 'completed': '#34c759', 'error': '#ff3b30'}
    
    for step, status in st.session_state.pipeline_status.items():
        icon = status_icons.get(status, '○')
        color = status_colors.get(status, '#86868b')
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 8px; margin: 4px 0; font-size: 12px;">
            <span style="color: {color}; font-size: 10px;">{icon}</span>
            <span style="color: #1d1d1f;">{step.replace('step', 'Step ')}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("##### ⚙️ Configuration")
    st.text_input("Timestamp", value=TIMESTAMP, disabled=True)
    st.text_input("Output Dir", value=OUTPUT_DIR, disabled=True)


# ============================================================================
# Page 1: Literature Review Pipeline
# ============================================================================
if page == "📚 Literature Review":
    st.markdown('<h1 class="gradient-title">Literature Review Pipeline</h1>', unsafe_allow_html=True)
    st.markdown("Generate comprehensive literature reviews using the 4-step pipeline.")
    
    # Research topic input
    st.markdown("### 🎯 Research Topic")
    default_topic = "the effect of spinodal construction of first order phase transition in the equation of state and the fluid dynamic simulations"
    research_topic = st.text_area("Enter your research topic:", value=default_topic, height=100)
    
    # Pipeline steps visualization
    st.markdown("### 📋 Pipeline Steps")
    
    cols = st.columns(4)
    step_info = [
        ("1️⃣ Query Gen", "Generate AI search queries", "step1"),
        ("2️⃣ PDF Download", "Fetch papers from arXiv", "step2"),
        ("3️⃣ Vector DB", "Create searchable index", "step3"),
        ("4️⃣ Review Gen", "Generate literature review", "step4")
    ]
    
    for col, (title, desc, key) in zip(cols, step_info):
        status = st.session_state.pipeline_status[key]
        status_class = 'completed' if status == 'completed' else ('active' if status == 'running' else '')
        with col:
            st.markdown(f"""
            <div class="step-card {status_class}">
                <h4>{title}</h4>
                <p style="color: #9ca3af; font-size: 0.85rem;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Control buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        run_pipeline = st.button("▶️ Run Full Pipeline", use_container_width=True)
    with col2:
        use_cached = st.button("📂 Use Cached Results", use_container_width=True)
    with col3:
        skip_db = st.checkbox("Skip DB creation (use existing)", value=True)
    
    # Run pipeline
    if run_pipeline:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Query Generation
            status_text.markdown("**Step 1/4:** Generating search queries...")
            st.session_state.pipeline_status['step1'] = 'running'
            progress_bar.progress(5)
            
            from step1_query_gen import generate_queries
            queries = generate_queries(user_input=research_topic, use_const=True)
            
            st.session_state.pipeline_status['step1'] = 'completed'
            progress_bar.progress(25)
            
            # Step 2: PDF Download
            status_text.markdown("**Step 2/4:** Downloading papers...")
            st.session_state.pipeline_status['step2'] = 'running'
            
            from step2_download import download_papers, INFO
            download_papers(info=INFO)
            
            st.session_state.pipeline_status['step2'] = 'completed'
            progress_bar.progress(50)
            
            # Step 3: Vector Database
            status_text.markdown("**Step 3/4:** Building vector database...")
            st.session_state.pipeline_status['step3'] = 'running'
            
            from step3_vectordb import create_db_and_query
            result = create_db_and_query(
                info=INFO,
                queries=queries,
                skip_db_creation=skip_db,
                top_k=19
            )
            
            st.session_state.pipeline_status['step3'] = 'completed'
            progress_bar.progress(75)
            
            # Step 4: Review Generation (English + Chinese)
            status_text.markdown("**Step 4/4:** Generating literature review (English + Chinese)...")
            st.session_state.pipeline_status['step4'] = 'running'
            
            from step4_generate import generate_review
            review_result = generate_review(
                user_input=research_topic,
                results=result['query_results']['results_txt'],
                logical=result['query_results']['logical_txt'],
                future=result['query_results']['future_txt'],
                save_intermediate=True,
                generate_chinese=True
            )
            
            st.session_state.pipeline_status['step4'] = 'completed'
            st.session_state.generated_review = review_result['final_review']
            st.session_state.generated_review_zh = review_result.get('final_review_zh')
            progress_bar.progress(100)
            
            status_text.markdown("✅ **Pipeline completed successfully!**")
            st.success("Literature review generated in both English and Chinese! Check the output below.")
            
        except Exception as e:
            st.error(f"Pipeline error: {str(e)}")
            status_text.markdown(f"❌ **Error:** {str(e)}")
    
    # Use cached results
    if use_cached:
        review_file = f"{OUTPUT_DIR}/final_review_{TIMESTAMP}.tex"
        review_file_zh = f"{OUTPUT_DIR}/final_review_zh_{TIMESTAMP}.tex"
        
        if os.path.exists(review_file):
            with open(review_file, 'r', encoding='utf-8') as f:
                st.session_state.generated_review = f.read()
            
            # Also try to load Chinese version
            if os.path.exists(review_file_zh):
                with open(review_file_zh, 'r', encoding='utf-8') as f:
                    st.session_state.generated_review_zh = f.read()
            
            for key in st.session_state.pipeline_status:
                st.session_state.pipeline_status[key] = 'completed'
            st.success("Loaded cached review!")
        else:
            st.warning("No cached review found. Run the pipeline first.")
    
    # Display results
    if st.session_state.generated_review:
        st.markdown("### 📄 Generated Literature Review")
        
        # Language tabs
        tab_en, tab_zh = st.tabs(["🇬🇧 English", "🇨🇳 中文"])
        
        with tab_en:
            col1, col2 = st.columns([3, 1])
            with col1:
                # Full LaTeX preview with scrollable container
                import html
                escaped_content = html.escape(st.session_state.generated_review)
                st.markdown(f"""
                <div class="latex-preview">
{escaped_content}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("**Actions**")
                st.download_button(
                    "📥 Download English .tex",
                    st.session_state.generated_review,
                    file_name=f"literature_review_{TIMESTAMP}.tex",
                    mime="text/plain",
                    key="download_en"
                )
                
                # Stats
                st.markdown("**Statistics**")
                words = count_text_length(st.session_state.generated_review, is_chinese=False)
                lines = st.session_state.generated_review.count('\n')
                cites = st.session_state.generated_review.count('\\cite')
                
                st.metric("Words", f"{words:,}")
                st.metric("Lines", f"{lines:,}")
                st.metric("Citations", cites)
        
        with tab_zh:
            if st.session_state.generated_review_zh:
                col1, col2 = st.columns([3, 1])
                with col1:
                    # Full Chinese LaTeX preview with scrollable container
                    escaped_content_zh = html.escape(st.session_state.generated_review_zh)
                    st.markdown(f"""
                    <div class="latex-preview">
{escaped_content_zh}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("**操作**")
                    st.download_button(
                        "📥 下载中文 .tex",
                        st.session_state.generated_review_zh,
                        file_name=f"literature_review_zh_{TIMESTAMP}.tex",
                        mime="text/plain",
                        key="download_zh"
                    )
                    
                    # Stats
                    st.markdown("**统计**")
                    # Use Chinese character count for accurate CJK text measurement
                    chars_zh = count_text_length(st.session_state.generated_review_zh, is_chinese=True)
                    lines_zh = st.session_state.generated_review_zh.count('\n')
                    cites_zh = st.session_state.generated_review_zh.count('\\cite')
                    
                    st.metric("中文字符", f"{chars_zh:,}")
                    st.metric("行数", f"{lines_zh:,}")
                    st.metric("引用", cites_zh)
            else:
                st.info("中文版本正在生成中，或尚未生成。请重新运行流水线以生成中文翻译。")


# ============================================================================
# Page 2: ReAct Agent Interface - Complete Redesign
# ============================================================================
elif page == "🤖 ReAct Agent":
    # Imports
    from result_detector import scan_results, find_literature_review
    from react_session import ReactSession, list_sessions
    
    # Initialize session state
    if 'current_session' not in st.session_state:
        st.session_state.current_session = None
    if 'react_start_time' not in st.session_state:
        st.session_state.react_start_time = None
    if 'react_status_text' not in st.session_state:
        st.session_state.react_status_text = "Ready"
    if 'react_conversation' not in st.session_state:
        st.session_state.react_conversation = []
    if 'react_final_result' not in st.session_state:
        st.session_state.react_final_result = None
    
    # Modern Chat Interface CSS
    st.markdown("""
    <style>
        .react-chat-container {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            height: 65vh;
            min-height: 500px;
            overflow-y: auto;
            padding: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .react-message {
            margin: 1rem 0;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            animation: slideIn 0.3s ease;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .react-message.think {
            background: #f0f9ff;
            border-left: 3px solid #3b82f6;
        }
        .react-message.action {
            background: #f0fdf4;
            border-left: 3px solid #22c55e;
        }
        .react-message.result {
            background: #fafafa;
            border-left: 3px solid #94a3b8;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }
        .react-message.answer {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            margin-left: auto;
            max-width: 80%;
        }
        .react-message.error {
            background: #fef2f2;
            border-left: 3px solid #ef4444;
            color: #dc2626;
        }
        .react-label {
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            opacity: 0.8;
            margin-bottom: 0.5rem;
        }
        .react-status {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
        }
        .react-status.running {
            background: #dbeafe;
            color: #1e40af;
        }
        .react-status.complete {
            background: #d1fae5;
            color: #065f46;
        }
        .react-status.ready {
            background: #f3f4f6;
            color: #6b7280;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Calculate elapsed time
    elapsed_time = 0
    if st.session_state.react_start_time and st.session_state.react_running:
        elapsed_time = int(time.time() - st.session_state.react_start_time)
    
    is_running = st.session_state.react_running
    is_complete = st.session_state.react_final_result is not None
    
    # Header
    col_header1, col_header2 = st.columns([3, 1])
    with col_header1:
        st.markdown('<h2 style="margin:0; font-size:1.5rem; font-weight:600;">🤖 ReAct Research Agent</h2>', unsafe_allow_html=True)
    with col_header2:
        if is_running:
            st.markdown(f'<div class="react-status running">● {st.session_state.react_status_text} ({elapsed_time}s)</div>', unsafe_allow_html=True)
        elif is_complete:
            st.markdown('<div class="react-status complete">✓ Complete</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="react-status ready">○ Ready</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Controls
    results = scan_results()
    review_options = {r['name']: r['path'] for r in results['literature_reviews']} if results['literature_reviews'] else {}
    
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([3, 1, 1])
    with col_ctrl1:
        if review_options:
            selected_review = st.selectbox("📄 Literature Review:", list(review_options.keys()), disabled=is_running)
            literature_file = review_options[selected_review]
        else:
            literature_file = st.text_input("📄 Literature File:", value=f"{OUTPUT_DIR}/final_review_{TIMESTAMP}.tex", disabled=is_running)
    
    with col_ctrl2:
        start_btn = st.button("▶️ Start", type="primary", use_container_width=True, disabled=is_running)
    
    with col_ctrl3:
        stop_btn = st.button("⏹️ Stop", use_container_width=True, disabled=not is_running)
    
    # Handle stop button - terminate and save
    if stop_btn:
        if st.session_state.current_session:
            try:
                session = ReactSession.load(st.session_state.current_session)
                session.stop_timer()
                session.set_status("stopped")
                session.save()
                st.success(f"✅ Session saved: {session.session_id}")
            except:
                pass
        st.session_state.react_running = False
        st.session_state.react_start_time = None
        st.session_state.react_status_text = "Stopped"
        st.rerun()
    
    # Conversation display
    st.markdown("#### 💬 Agent Conversation")
    chat_container = st.container()
    
    def run_agent_workflow(task: str, session: ReactSession):
        """Run agent workflow with NO iteration limits - runs until completion or stop."""
        try:
            from react.agent_v2 import ReactAgentV2
            # NO LIMIT - set to very large number
            agent = ReactAgentV2(verbose=False, max_iterations=99999)
        except ImportError:
            from react.agent import ReactAgent
            agent = ReactAgent(verbose=False, max_iterations=99999)
        
        def update_status(text):
            st.session_state.react_status_text = text
        
        def add_message(msg_type, content, iteration=0):
            """Add message to conversation."""
            msg = {
                'type': msg_type,
                'content': content,
                'iteration': iteration,
                'timestamp': time.time()
            }
            st.session_state.react_conversation.append(msg)
            session.add_step(msg_type, content, iteration)
        
        # Start timer
        session.start_timer()
        
        with chat_container:
            for step in agent.run_streaming(task):
                # Check stop request
                if not st.session_state.react_running:
                    session.stop_timer()
                    session.set_status("stopped")
                    session.save()
                    add_message("info", "Workflow stopped by user")
                    st.warning("⏹️ Workflow stopped. Session saved.")
                    break
                
                step_type = step.get('type', '')
                content = step.get('content', '')
                iteration = step.get('iteration', 0)
                action_input = step.get('action_input', {})
                
                session.current_iteration = iteration
                
                # Update status
                if step_type == 'thought':
                    update_status("Thinking...")
                elif step_type == 'action':
                    update_status(f"🔧 {content}")
                elif step_type == 'observation':
                    update_status("Processing result...")
                
                # Display messages
                if step_type == 'start':
                    st.markdown('<div class="react-message action"><div class="react-label">🚀 Starting</div>Initializing research agent...</div>', unsafe_allow_html=True)
                    add_message("info", "Agent started")
                
                elif step_type == 'iteration':
                    st.markdown(f'<div style="padding:0.5rem; font-size:12px; color:#6b7280; border-bottom:1px solid #e5e7eb;">Step {iteration}</div>', unsafe_allow_html=True)
                
                elif step_type == 'thought':
                    import html as html_module
                    escaped = html_module.escape(content[:500])
                    st.markdown(f'<div class="react-message think"><div class="react-label">💭 Thinking</div>{escaped}{"..." if len(content) > 500 else ""}</div>', unsafe_allow_html=True)
                    add_message("thought", content, iteration)
                
                elif step_type == 'action':
                    import html as html_module
                    escaped_content = html_module.escape(content)
                    input_preview = str(action_input)[:150] if action_input else ""
                    st.markdown(f'<div class="react-message action"><div class="react-label">⚡ {escaped_content}</div><code style="font-size:11px;">{html_module.escape(input_preview)}</code></div>', unsafe_allow_html=True)
                    add_message("action", content, iteration)
                
                elif step_type == 'observation':
                    with st.expander(f"📄 Result ({len(content)} chars)", expanded=False):
                        st.code(content[:1500] + ("..." if len(content) > 1500 else ""), language='text')
                    add_message("observation", content[:500], iteration)
                
                elif step_type == 'final_answer':
                    update_status("Complete")
                    try:
                        import json
                        result_data = json.loads(content) if content.strip().startswith('{') else {"summary": content}
                    except:
                        result_data = {"summary": content}
                    
                    session.set_final_result(result_data)
                    session.stop_timer()
                    session.set_status("completed")
                    session.save()
                    
                    st.session_state.react_final_result = result_data
                    
                    st.markdown('<div class="react-message answer"><div class="react-label">✅ Complete</div>Analysis finished successfully</div>', unsafe_allow_html=True)
                    add_message("final_answer", content, iteration)
                    
                    with st.expander("📋 Final Results", expanded=True):
                        if isinstance(result_data, dict):
                            st.json(result_data)
                        else:
                            st.text(content[:3000])
                    st.balloons()
                    break
                
                elif step_type == 'error':
                    import html as html_module
                    escaped = html_module.escape(content)
                    st.markdown(f'<div class="react-message error"><div class="react-label">❌ Error</div>{escaped}</div>', unsafe_allow_html=True)
                    add_message("error", content, iteration)
        
        # Finalize
        if st.session_state.react_running:
            st.session_state.react_running = False
            if not st.session_state.react_final_result:
                session.stop_timer()
                session.set_status("stopped")
                session.save()
            update_status("Complete" if st.session_state.react_final_result else "Stopped")
    
    # Handle start button
    if start_btn:
        if not os.path.exists(literature_file):
            st.error(f"❌ File not found: {literature_file}")
        else:
            # Reset state
            st.session_state.react_running = True
            st.session_state.react_start_time = time.time()
            st.session_state.react_status_text = "Starting..."
            st.session_state.react_conversation = []
            st.session_state.react_final_result = None
            
            # Create new session
            session = ReactSession(task=f"Particle physics research from {literature_file}")
            session.literature_file = literature_file
            session.max_iterations = 99999  # No limit
            st.session_state.current_session = session.session_id
            
            # Task prompt
            task = f"""Complete this particle physics research workflow:

PATHS (use absolute paths):
- Literature: {literature_file}
- Scripts: /home/yuntao/Mydata/pythia_workspace/scripts/
- Results: /home/yuntao/Mydata/pythia_workspace/results/

STEPS:
1. Read literature review: {literature_file}
2. Extract future work items for Pythia8 simulation
3. Generate simulation script → /home/yuntao/Mydata/pythia_workspace/scripts/simulate_*.py
4. Execute simulation
5. Write analysis program
6. Save analysis → /home/yuntao/Mydata/pythia_workspace/results/analysis_*.json

TERMINATION: Stop after saving analysis JSON. Provide <answer> with results."""
            
            with chat_container:
                try:
                    run_agent_workflow(task, session)
                except Exception as e:
                    st.error(f"❌ Agent error: {e}")
                    session.add_step("error", str(e))
                    session.stop_timer()
                    session.set_status("error")
                    session.save()
                    st.session_state.react_running = False
                    st.session_state.react_start_time = None
    
    # Show conversation history or welcome
    elif not st.session_state.react_running:
        with chat_container:
            if st.session_state.react_final_result:
                st.markdown("##### ✅ Analysis Complete")
                if isinstance(st.session_state.react_final_result, dict):
                    st.json(st.session_state.react_final_result)
                else:
                    st.text(str(st.session_state.react_final_result)[:3000])
                
                import json
                result_json = json.dumps(st.session_state.react_final_result, indent=2, ensure_ascii=False)
                st.download_button(
                    "📥 Download Results",
                    result_json,
                    file_name=f"react_results_{TIMESTAMP}.json",
                    use_container_width=True
                )
            elif st.session_state.react_conversation:
                st.markdown("**Previous Conversation:**")
                for msg in st.session_state.react_conversation[-10:]:
                    msg_type = msg.get('type', 'info')
                    msg_content = msg.get('content', '')[:200]
                    if msg_type == 'think':
                        st.markdown(f'<div class="react-message think"><div class="react-label">💭 Thinking</div>{msg_content}</div>', unsafe_allow_html=True)
                    elif msg_type == 'action':
                        st.markdown(f'<div class="react-message action"><div class="react-label">⚡ Action</div>{msg_content}</div>', unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align:center; padding:4rem 2rem; color:#6b7280;">
                    <div style="font-size:3rem; margin-bottom:1rem;">🔬</div>
                    <div style="font-size:18px; font-weight:500; margin-bottom:0.5rem;">Automated Physics Research</div>
                    <div style="font-size:14px;">
                        Select a literature review and click <strong>Start</strong><br>
                        The agent will run until completion or you click <strong>Stop</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ============================================================================
# Page 3: Article Generation
# ============================================================================
elif page == "📝 Article Generation":
    st.markdown('<h1 class="gradient-title">Article Generation</h1>', unsafe_allow_html=True)
    st.markdown("Generate research articles from literature review and simulation results.")
    
    # Import result detector
    from result_detector import scan_results, get_results_summary, load_json_result, load_tex_content
    
    # Refresh button and saved articles selector
    col_refresh, col_articles, col_status = st.columns([1, 2, 3])
    with col_refresh:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # Get current results
    summary = get_results_summary()
    results = scan_results()
    
    # Show saved articles selector
    with col_articles:
        article_options = {r['name']: r['path'] for r in results.get('research_articles', [])}
        if article_options:
            selected_article_name = st.selectbox("📄 Saved Articles:", ["🆕 Generate New"] + list(article_options.keys()))
            if selected_article_name != "🆕 Generate New" and selected_article_name:
                selected_saved_article = article_options[selected_article_name]
                # Load and display saved article (only if not currently generating)
                if not st.session_state.get('article_generating', False):
                    saved_content = load_tex_content(selected_saved_article)
                    if saved_content:
                        st.session_state.generated_article = saved_content
                        st.session_state.saved_article_path = selected_saved_article
                        # Try to load Chinese version
                        zh_path = selected_saved_article.replace('research_article_', 'research_article_zh_')
                        if os.path.exists(zh_path):
                            st.session_state.generated_article_zh = load_tex_content(zh_path)
                            st.session_state.saved_article_zh_path = zh_path
                        else:
                            st.session_state.generated_article_zh = None
                            st.session_state.saved_article_zh_path = None
        else:
            st.info("No saved articles yet. Generate one to get started!")
    
    with col_status:
        if summary['ready_for_article']:
            st.success(f"✅ Ready to generate! {summary['counts']['literature_reviews']} reviews, {summary['counts']['simulation_results']} simulations")
        else:
            missing = []
            if not summary['has_reviews']:
                missing.append("literature review")
            if not summary['has_simulations']:
                missing.append("simulation results")
            st.warning(f"⚠️ Missing: {', '.join(missing)}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📚 Source Documents")
        
        # Literature reviews with selection
        if results['literature_reviews']:
            review_options = {r['name']: r['path'] for r in results['literature_reviews']}
            selected_review_name = st.selectbox("Select Literature Review:", list(review_options.keys()))
            selected_review_path = review_options[selected_review_name]
            
            st.success(f"✅ {len(results['literature_reviews'])} review(s) found")
            with st.expander("Preview Review"):
                content = load_tex_content(selected_review_path)
                if content:
                    st.code(content[:2000] + ("..." if len(content) > 2000 else ""), language='latex')
        else:
            st.warning("⚠️ No literature review found")
            st.info("Run the Literature Review Pipeline first, or use the ReAct Agent to generate one.")
            selected_review_path = None
        
        st.markdown("---")
        
        # Simulation results with selection
        if results['simulation_results']:
            sim_options = {r['name']: r['path'] for r in results['simulation_results']}
            selected_sim_name = st.selectbox("Select Simulation Result:", list(sim_options.keys()))
            selected_sim_path = sim_options[selected_sim_name]
            
            st.success(f"✅ {len(results['simulation_results'])} result file(s) found")
            with st.expander("Preview Result"):
                data = load_json_result(selected_sim_path)
                if data:
                    st.json(data if len(str(data)) < 5000 else {"preview": "Large file - showing keys", "keys": list(data.keys()) if isinstance(data, dict) else "list"})
        else:
            st.info("📭 No simulation results yet")
            st.markdown("""
            **To generate simulation results:**
            1. Go to **🤖 ReAct Agent** page
            2. Click **Start Workflow**
            3. The agent will run Pythia8 simulations
            4. Return here and click **Refresh Results**
            """)
            selected_sim_path = None
        
        # Show scripts too
        if results['simulation_scripts']:
            with st.expander(f"📜 Available Scripts ({len(results['simulation_scripts'])})"):
                for script in results['simulation_scripts'][:5]:
                    st.markdown(f"- `{script['name']}`")
    
    with col2:
        st.markdown("### ⚙️ Article Configuration")
        
        title = st.text_input("Article Title:", value="Spinodal Effects in QCD Phase Transitions")
        
        sections = st.multiselect(
            "Include sections:",
            ["Abstract", "Introduction", "Background", "Methodology", "Results", "Discussion", "Conclusion"],
            default=["Abstract", "Introduction", "Methodology", "Results", "Conclusion"]
        )
        
        style = st.selectbox("Citation Style:", ["BibTeX", "IEEE", "APA"])
        
        generate_btn = st.button("📝 Generate Article", use_container_width=True, type="primary")
    
    # Article generation
    if generate_btn:
        if not selected_review_path or not selected_sim_path:
            st.error("❌ Please select both a literature review and simulation results.")
        else:
            # Initialize state
            if 'article_generating' not in st.session_state:
                st.session_state.article_generating = False
            if 'generated_article' not in st.session_state:
                st.session_state.generated_article = None
            if 'generated_article_zh' not in st.session_state:
                st.session_state.generated_article_zh = None
            
            st.session_state.article_generating = True
            
            with st.spinner("🤖 Generating article with AI..."):
                try:
                    from article_generator import generate_article, translate_article_to_chinese
                    
                    # Generate English article
                    # #region agent log
                    log_file = '/home/yuntao/Mydata/.cursor/debug.log'
                    try:
                        import json as json_module
                        with open(log_file, 'a', encoding='utf-8') as log:
                            log.write(json_module.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"G","location":"react_streamlit.py:1256","message":"Before generate_article call","data":{"review":selected_review_path,"sim":selected_sim_path},"timestamp":int(time.time()*1000)}) + '\n')
                    except: pass
                    # #endregion
                    
                    article_en = generate_article(
                        literature_file=selected_review_path,
                        simulation_result_file=selected_sim_path,
                        title=title,
                        sections=sections
                    )
                    
                    # #region agent log
                    try:
                        with open(log_file, 'a', encoding='utf-8') as log:
                            is_error = article_en.startswith("Error")
                            log.write(json_module.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"G","location":"react_streamlit.py:1270","message":"After generate_article","data":{"result_length":len(article_en) if article_en else 0,"is_error":is_error,"first_100":article_en[:100] if article_en else ""},"timestamp":int(time.time()*1000)}) + '\n')
                    except: pass
                    # #endregion
                    
                    # Check if result is an error message
                    if article_en.startswith("Error"):
                        raise Exception(article_en)
                    
                    st.session_state.generated_article = article_en
                    
                    # Generate Chinese translation
                    with st.spinner("🌏 Translating to Chinese..."):
                        article_zh = translate_article_to_chinese(article_en)
                        st.session_state.generated_article_zh = article_zh
                    
                    # Save articles to files
                    from article_generator import save_article, save_article_chinese, get_timestamp
                    timestamp = get_timestamp()
                    
                    saved_en_path = save_article(article_en, title=title, timestamp=timestamp)
                    saved_zh_path = save_article_chinese(article_zh, title=title, timestamp=timestamp)
                    
                    st.session_state.article_generating = False
                    st.session_state.saved_article_path = saved_en_path
                    st.session_state.saved_article_zh_path = saved_zh_path
                    st.success(f"✅ Article generated and saved! English: `{os.path.basename(saved_en_path)}`, Chinese: `{os.path.basename(saved_zh_path)}`")
                    
                except Exception as e:
                    st.error(f"❌ Error generating article: {e}")
                    st.session_state.article_generating = False
    
    # Display generated or loaded article
    if st.session_state.get('generated_article'):
        article_content = st.session_state.generated_article
        
        # Check if content is an error message
        if article_content.startswith("Error"):
            st.error(f"❌ {article_content}")
        else:
            st.markdown("---")
            # Show if this is a loaded article or newly generated
            if st.session_state.get('saved_article_path'):
                st.info(f"📁 Saved to: `{os.path.basename(st.session_state.saved_article_path)}`")
            st.markdown("### 📄 Research Article")
            
            # Language tabs
            tab_en, tab_zh = st.tabs(["🇬🇧 English", "🇨🇳 中文"])
            
            with tab_en:
                col1, col2 = st.columns([3, 1])
                with col1:
                    # Full LaTeX preview with scrollable container
                    escaped_content = html.escape(article_content)
                    st.markdown(f"""
                    <div class="latex-preview">
{escaped_content}
                    </div>
                    """, unsafe_allow_html=True)
            
                with col2:
                    st.markdown("**Actions**")
                    st.download_button(
                        "📥 Download English .tex",
                        article_content,
                        file_name=f"research_article_{TIMESTAMP}.tex",
                        mime="text/plain",
                        key="download_article_en"
                    )
                    
                    # Stats
                    st.markdown("**Statistics**")
                    words = count_text_length(article_content, is_chinese=False)
                    lines = article_content.count('\n')
                    cites = article_content.count('\\cite')
                
                    st.metric("Words", f"{words:,}")
                    st.metric("Lines", f"{lines:,}")
                    st.metric("Citations", cites)
            
            with tab_zh:
                if st.session_state.get('generated_article_zh'):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        # Full Chinese LaTeX preview
                        escaped_content_zh = html.escape(st.session_state.generated_article_zh)
                        st.markdown(f"""
                        <div class="latex-preview">
{escaped_content_zh}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("**Actions**")
                        st.download_button(
                            "📥 Download 中文 .tex",
                            st.session_state.generated_article_zh,
                            file_name=f"research_article_zh_{TIMESTAMP}.tex",
                            mime="text/plain",
                            key="download_article_zh"
                        )
                        
                        # Stats
                        st.markdown("**Statistics**")
                        words_zh = count_text_length(st.session_state.generated_article_zh, is_chinese=True)
                        lines_zh = st.session_state.generated_article_zh.count('\n')
                        cites_zh = st.session_state.generated_article_zh.count('\\cite')
                        
                        st.metric("中文字符", f"{words_zh:,}")
                        st.metric("Lines", f"{lines_zh:,}")
                        st.metric("Citations", cites_zh)
                else:
                    st.info("Chinese translation not available yet.")


# ============================================================================
# Page 4: Workflow Visualization
# ============================================================================
elif page == "🔄 Workflow":
    st.markdown('<h1 class="gradient-title">Workflow Visualization</h1>', unsafe_allow_html=True)
    st.markdown("Complete research workflow from literature review to article generation.")
    
    # Workflow diagram using Streamlit columns
    st.markdown("### 📊 Complete Research Pipeline")
    
    st.markdown("""
    <div class="glass-card">
        <h3 style="text-align: center; color: #06b6d4;">Literature Review → ReAct Agent → Research Article</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Phase 1: Literature Review
    st.markdown("#### 📚 Phase 1: Literature Review Pipeline")
    cols = st.columns(4)
    phase1_steps = [
        ("🎯", "Query Generation", "AI generates 30 search queries"),
        ("📥", "PDF Download", "Fetch papers from arXiv"),
        ("🗄️", "Vector Database", "Create ChromaDB index"),
        ("📝", "3-Stage Review", "Generate LaTeX review")
    ]
    
    for col, (icon, title, desc) in zip(cols, phase1_steps):
        with col:
            st.markdown(f"""
            <div class="step-card">
                <div style="font-size: 2rem;">{icon}</div>
                <h4>{title}</h4>
                <p style="color: #9ca3af; font-size: 0.8rem;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Phase 2: ReAct Agent
    st.markdown("#### 🤖 Phase 2: ReAct Agent Loop")
    cols = st.columns(4)
    phase2_steps = [
        ("📖", "Read Review", "Load literature review"),
        ("🔍", "Extract Items", "Find future work"),
        ("💻", "Generate Code", "Create Pythia8 scripts"),
        ("⚡", "Execute", "Run simulations")
    ]
    
    for col, (icon, title, desc) in zip(cols, phase2_steps):
        with col:
            st.markdown(f"""
            <div class="step-card">
                <div style="font-size: 2rem;">{icon}</div>
                <h4>{title}</h4>
                <p style="color: #9ca3af; font-size: 0.8rem;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Phase 3: Article
    st.markdown("#### 📄 Phase 3: Final Output")
    cols = st.columns(3)
    phase3_steps = [
        ("📊", "Analyze Results", "Process simulation data"),
        ("✍️", "Write Article", "Generate LaTeX paper"),
        ("📤", "Export", "Download final article")
    ]
    
    for col, (icon, title, desc) in zip(cols, phase3_steps):
        with col:
            st.markdown(f"""
            <div class="step-card">
                <div style="font-size: 2rem;">{icon}</div>
                <h4>{title}</h4>
                <p style="color: #9ca3af; font-size: 0.8rem;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Technology stack
    st.markdown("---")
    st.markdown("### 🛠️ Technology Stack")
    
    tech_cols = st.columns(4)
    techs = [
        ("Python", "Core language"),
        ("Pythia8mc", "MC simulation"),
        ("ChromaDB", "Vector store"),
        ("OpenAI API", "LLM integration")
    ]
    
    for col, (tech, desc) in zip(tech_cols, techs):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="font-size: 1.2rem;">{tech}</div>
                <div class="metric-label">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Embed HTML visualization link
    st.markdown("---")
    st.markdown("### 🌐 Full Visualization")
    st.info("Open `react_frontend.html` in a browser for the complete interactive visualization.")
    
    if st.button("📂 Open HTML File Location"):
        st.code("file:///home/yuntao/Mydata/react_frontend.html", language="text")


# Footer - Apple style
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: rgba(0, 0, 0, 0.56); font-size: 12px; line-height: 1.8; padding: 20px 0;">
    RAG文献综述生成系统 · ReAct粒子物理研究系统<br>
    <a href="https://pypi.org/project/pythia8mc/" style="color: #0071e3; text-decoration: none;">Pythia8mc</a> · 
    Built with Streamlit · © 2025
</div>
""", unsafe_allow_html=True)

