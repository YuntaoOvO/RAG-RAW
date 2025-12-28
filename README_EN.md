# ⚛️  RAG-RAW
Based on the project arxivdb, we developed RAGRAP(Retrieval-Augmented Generation with Reason-Acting Workflow). With high spirits, we are here providing a LLM-powered workflow for deeper and more practical research, enabling AI to work like a graduate student instead of following their whimsies.


# RAG Literature Review & ReAct Multi-field Physics Research System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![Pythia8](https://img.shields.io/badge/Pythia8mc-8.3+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**An Autonomous Knowledge Discovery Agent System Based on Large Language Models**

English | [简体中文](README.md)

</div>

---

## 📖 Overview

This project implements a complete **Autonomous Knowledge Discovery Agent System**. It integrates arXiv literature into a vector database for semantic retrieval and information integration, generating effective, comprehensive, and traceable literature review reports. Through the ReAct workflow, it empowers large language models with tool-using capabilities, enabling autonomous preliminary quantitative exploration of potential future research directions identified in generated literature reviews.

### 🎯 Core Features

1. **Literature Review Pipeline**
   - AI automatically generates 30 arXiv search queries based on user's research topic
   - Automatic PDF download of relevant academic papers
   - Build ChromaDB vector database using BGE-M3 embedding model
   - Three-stage progressive literature review generation (Draft 1 → Draft 2 → Final)
   - Bilingual output support (English + Chinese)

2. **ReAct Agent Workflow (Reason-Act Agent)**
   - Implementation of Reason-Act loop reasoning framework
   - Tool-augmented AI capabilities (file I/O, code execution, Pythia8 simulation, etc.)
   - Autonomous extraction of future research directions from literature reviews
   - Automatic generation and execution of Pythia8 Monte Carlo simulation scripts
   - Generation of matplotlib visualizations
   - Structured analysis results in JSON format

3. **Research Paper Generation**
   - Integration of literature review and simulation results
   - Automatic generation of LaTeX research papers
   - Correct referencing of generated figures
   - Bilingual version support (English + Chinese)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    RAG Literature Review System                  │
├─────────────────────────────────────────────────────────────────┤
│  Phase 1: Literature Review Pipeline                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │ Query    │→ │ PDF      │→ │ Vector   │→ │ 3-Stage Review   │ │
│  │ Generate │  │ Download │  │ Database │  │ Generation       │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  Phase 2: ReAct Agent Loop                                       │
│  ┌──────┐  ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌─────────┐  │
│  │ Read │→ │ Extract │→ │ Generate │→ │ Execute │→ │ Analyze │  │
│  │      │  │ Future  │  │ Pythia8  │  │ Simul.  │  │ Results │  │
│  └──────┘  └─────────┘  └──────────┘  └─────────┘  └─────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  Phase 3: Article Generation                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Combine      │→ │ Generate     │→ │ Output LaTeX Article │   │
│  │ Review+Sim   │  │ With Figures │  │ (EN + ZH)            │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Mydata/
├── react_streamlit.py          # Main Streamlit application
├── react_workflow.html         # Workflow visualization page
├── react_frontend.html         # Interactive frontend page
├── article_generator.py        # Research paper generator
├── result_detector.py          # Result detection and loading utility
├── react_session.py            # ReAct session management
├── rag_core.py                 # RAG core functionality module
│
├── step1_query_gen.py          # Step 1: Query generation
├── step2_download.py           # Step 2: PDF download
├── step3_vectordb.py           # Step 3: Vector database
├── step4_generate.py           # Step 4: Literature review generation
│
├── react/                      # ReAct agent modules
│   ├── __init__.py
│   ├── agent.py                # Original ReAct agent
│   ├── agent_v2.py             # Refactored ReAct agent (recommended)
│   ├── config.py               # Configuration file
│   ├── tools/                  # Tool collection
│   │   ├── file_reader.py      # File reading tool
│   │   ├── file_writer.py      # File writing tool
│   │   ├── code_executor.py    # Code execution tool
│   │   ├── pythia_tool.py      # Pythia8 simulation tool
│   │   └── analyzer.py         # Analysis tool
│   └── prompts/                # Prompt templates
│       ├── researcher.py
│       └── writer.py
│
├── pythia_workspace/           # Pythia8 workspace
│   ├── scripts/                # Generated simulation scripts
│   ├── events/                 # Event data
│   ├── results/                # Analysis results JSON
│   └── figures/                # Generated figures
│
├── output/                     # Output directory
│   ├── final_review_*.tex      # Final literature reviews
│   ├── research_article_*.tex  # Research papers
│   └── react_sessions/         # ReAct session records
│
└── .env                        # Environment variable configuration
```

---

## 🚀 Quick Start

### 1. Requirements

- Python 3.10+
- CUDA (optional, for GPU acceleration)

### 2. Installation

```bash
# Clone repository
git clone <repository-url>
cd Mydata

# Install Python dependencies
pip install -r requirements.txt

# Install Pythia8 Monte Carlo simulator
pip install pythia8mc

# Download BGE-M3 embedding model (for vector retrieval)
# Model path: /home/yuntao/bge-m3
```

### 3. Configure API Keys

Create `.env` file:

```env
MIMO_API_KEY=your_api_key_here
# Or use OpenAI-compatible API
OPENAI_API_KEY=your_openai_key
OPENAI_API_BASE=https://api.openai.com/v1
```

### 4. Run Application

```bash
# Start Streamlit app
streamlit run react_streamlit.py

# Or run pipeline separately
python step1_query_gen.py
python step2_download.py
python step3_vectordb.py
python step4_generate.py
```

---

## 📚 User Guide

### Literature Review Generation

1. Open **📚 Literature Review** page
2. Enter research topic (e.g., "Spinodal effects in QCD phase transitions")
3. Click **Run Full Pipeline** to run the complete pipeline
4. Wait for completion and download LaTeX files

### ReAct Agent Research

1. Open **🤖 ReAct Agent** page
2. Select a generated literature review file
3. Click **Start** to launch automatic research workflow
4. The agent will automatically:
   - Read the literature review
   - Extract future research directions
   - Generate Pythia8 simulation scripts
   - Execute simulations and analyze results
   - Generate visualization figures

### Paper Generation

1. Open **📝 Article Generation** page
2. Select literature review and simulation result files
3. Configure paper title and sections
4. Click **Generate Article** to generate LaTeX paper

---

## 🔧 ReAct Agent Tools

| Tool Name | Description |
|-----------|-------------|
| `read_file` | Read .tex, .py, .json files |
| `write_file` | Create or modify files |
| `run_code` | Execute Python code |
| `pythia_generate` | Generate Pythia8 simulation scripts |
| `pythia_api` | Get Pythia8 API documentation |
| `extract_future_work` | Extract future research directions from literature |
| `parse_results` | Parse simulation results |
| `list_files` | List directory files |

---

## 🎨 Interface Preview

### Streamlit Main Interface

- **Literature Review Pipeline**: Four-step visual progress
- **ReAct Agent**: Real-time streaming conversation interface
- **Paper Generation**: LaTeX preview and download
- **Workflow Visualization**: Interactive flowchart

### HTML Visualization

Open these files for static visualizations:

- `react_workflow.html` - Complete workflow diagram
- `react_frontend.html` - Interactive feature demonstration

---

## 🔬 Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit, HTML/CSS/JS |
| LLM | OpenAI API (compatible) |
| Vector Database | ChromaDB |
| Embedding Model | BGE-M3 |
| Monte Carlo Simulation | Pythia8mc |
| Document Format | LaTeX, BibTeX |
| Visualization | Matplotlib |

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

---

## 👥 Authors

- **Li Yuntao** - Central China Normal University, School of Physics Science and Technology
- **Wu Yaling** - Central China Normal University, School of Physics Science and Technology

Major: Physics (Base Class)

---

## 🙏 Acknowledgments

- [Pythia8](https://pythia.org/) - High-energy physics Monte Carlo event generator
- [ChromaDB](https://www.trychroma.com/) - Open-source vector database
- [BGE-M3](https://huggingface.co/BAAI/bge-m3) - Multilingual embedding model
- [Streamlit](https://streamlit.io/) - Python data application framework

---

<div align="center">

**⚛️ RAG Literature Review & ReAct Particle Physics Research System**

Central China Normal University, School of Physics Science and Technology © 2025

</div>
