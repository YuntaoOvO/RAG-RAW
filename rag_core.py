"""
RAG Core Module - 统一核心模块
================================

本模块整合了所有必要的RAG、AI Agent和文献综述功能。

功能模块：
1. RAG功能（带metadata修复）
   - PDF加载和处理
   - 向量数据库创建和查询
   - Metadata清理和兼容性处理

2. AI Agent功能
   - 在线AI对话（基于OpenAI API）
   - 本地AI对话（基于Ollama）

3. 文献综述生成
   - 基于检索结果自动生成文献综述

关键修复：
- ChromaDB metadata兼容性（只支持 str, int, float, bool）
- doc_id自动映射和嵌入
- CUDA加速的BGE-M3模型

作者: AI Assistant
日期: 2025-10-22
版本: 2.0 (整合版)
"""

import os
import re
import json
import requests
import numpy as np
from tqdm import tqdm
from typing import List, Dict, Tuple, Optional, Union

# LangChain imports
from langchain_community.document_loaders import PyPDFLoader
#from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Embedding and Vector DB
from FlagEmbedding import BGEM3FlagModel
import chromadb

# AI Agent imports
from openai import OpenAI
from dotenv import load_dotenv


# ============================================================================
# RAG功能模块
# ============================================================================

def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除非法字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        清理后的安全文件名
    """
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    if len(filename) > 100:
        filename = filename[:100]
    return filename


def sanitize_metadata(meta: Optional[Dict]) -> Dict:
    """
    清理metadata以确保ChromaDB兼容性
    
    ChromaDB只支持 str, int, float, bool 类型的metadata值，
    不支持None、复杂对象等
    
    Args:
        meta: 原始metadata字典
        
    Returns:
        清理后的metadata字典
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
    
    # 确保必要字段存在
    if 'doc_id' not in sanitized:
        sanitized['doc_id'] = 'unknown'
    if 'source' not in sanitized:
        sanitized['source'] = 'unknown'  
    if 'page' not in sanitized:
        sanitized['page'] = 0
        
    return sanitized


def load_pdf(fpath: str = "pdf\\quantum.pdf") -> List:
    """
    加载单个PDF文件
    
    Args:
        fpath: PDF文件路径
        
    Returns:
        文档列表
    """
    loader = PyPDFLoader(fpath)
    doc = loader.load()
    return doc


def load_pdfs(work_dir: str, sur_fix: str = ".pdf") -> Tuple[List, List]:
    """
    批量加载PDF文件
    
    Args:
        work_dir: 工作目录
        sur_fix: 文件后缀
        
    Returns:
        (loaded_docs, failed_files): 加载的文档列表和失败的文件列表
    """
    loaded_docs = []
    failed_files = []
    for file in os.listdir(work_dir):
        if file.endswith(sur_fix):
            try:
                loader = PyPDFLoader(os.path.join(work_dir, file))
                docs = loader.load()
                loaded_docs.extend(docs)
            except Exception as e:
                if "Multiple definitions in dictionary" in str(e):
                    print(f"警告: 文件 {file} 加载失败，原因: {e}")
                else:
                    failed_files.append(file)
    # #region agent log
    import json as _json; open('/home/yuntao/Mydata/.cursor/debug.log','a').write(_json.dumps({"hypothesisId":"A","location":"rag_core.py:load_pdfs_info:exit","message":"load_pdfs_info complete","data":{"loaded_docs_len":len(loaded_docs),"failed_files":failed_files,"info_processed":len(info) if info else 0},"timestamp":__import__('time').time()})+'\n')
    # #endregion
    return loaded_docs, failed_files


def load_pdfs_info(work_dir: str, info: List[Dict] = []) -> Tuple[List, List]:
    """
    根据info列表加载指定的PDF文件
    
    Args:
        work_dir: PDF文件所在目录
        info: 包含doc_id的字典列表，例如 [{'doc_id':'0903.4335'}, ...]
        
    Returns:
        (loaded_docs, failed_files): 加载的文档列表和失败的文件列表
        
    Example:
        >>> info = [{'doc_id':'0903.4335'}, {'doc_id':'2408.09679'}]
        >>> docs, failed = load_pdfs_info("D:\\App\\Mydata\\download", info=info)
    """
    loaded_docs = []
    failed_files = []

    for item in info:
        arxiv_id = item['doc_id']
        clean_id = sanitize_filename(arxiv_id.split('/')[-1])
        file = os.path.join(work_dir, clean_id + '.pdf')
        
        # Check if file exists first
        if not os.path.exists(file):
            print(f"⚠️  PDF not found: {file}")
            failed_files.append(file)
            continue
            
        try:
            loader = PyPDFLoader(file)
            docs = loader.load()
            loaded_docs.extend(docs)
        except Exception as e:
            if "Multiple definitions in dictionary" in str(e):
                print(f"警告: 文件 {file} 加载失败，原因: {e}")
            else:
                print(f"⚠️  Failed to load PDF: {file}, error: {type(e).__name__}: {str(e)[:100]}")
                failed_files.append(file)
    return loaded_docs, failed_files


def create_vector_db(doc: List,
                     info: List[Dict],
                     chunk_size: int = 1024,
                     chunk_overlap: int = 20,
                     dbname: str = "rag_db",
                     persist_directory: str = 'D:\\App\\Mydata\\ragdb\\',
                     model_path: str = 'C:\\Users\\47577\\bge-m3',
                     batch_size: int = 16,
                     max_length: int = 1024,
                     download_dir: str = "D:\\App\\Mydata\\download",
                     use_cuda: bool = True) -> None:
    """
    创建向量数据库 - 带metadata修复
    
    修复特性：
    1. 从文件路径映射到doc_id（arxiv ID）
    2. 使用sanitize_metadata确保类型兼容
    3. 完整的错误处理
    4. CUDA加速支持
    
    Args:
        doc: 文档列表（从load_pdfs_info获取）
        info: 论文信息列表，包含doc_id
        chunk_size: 文本分块大小
        chunk_overlap: 分块重叠大小
        dbname: 数据库名称
        persist_directory: 数据库持久化目录
        model_path: 嵌入模型路径
        batch_size: 批处理大小
        max_length: 最大序列长度
        download_dir: PDF下载目录
        use_cuda: 是否使用CUDA加速
    """
    print(f"开始创建数据库: {dbname}")
    print(f"CUDA加速: {'已启用' if use_cuda else '未启用'}")
    
    # 加载模型（启用CUDA）
    model = BGEM3FlagModel(model_path, use_fp16=True, device='cuda:0' if use_cuda else 'cpu')
    
    # 创建文本分割器
    r_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    # 创建source到doc_id的映射
    source_to_docid = {}
    for item in info:
        arxiv_id = item['doc_id']
        clean_id = sanitize_filename(arxiv_id.split('/')[-1])
        file_path = os.path.join(download_dir, f"{clean_id}.pdf")
        normalized_path = os.path.normpath(file_path)
        source_to_docid[normalized_path] = arxiv_id
    
    # 为每个文档添加doc_id到metadata
    print(f"\n开始为文档添加doc_id元数据...")
    enriched_count = 0
    failed_to_match = []
    
    for idx, page in enumerate(doc):
        if page.metadata is None:
            page.metadata = {}
        
        source_path = page.metadata.get('source', '')
        normalized_source = os.path.normpath(source_path)
        
        # 匹配doc_id
        matched = False
        if normalized_source in source_to_docid:
            page.metadata['doc_id'] = source_to_docid[normalized_source]
            enriched_count += 1
            matched = True
        else:
            # 备用方案：从文件名推断
            for norm_path, doc_id in source_to_docid.items():
                if os.path.basename(normalized_source) == os.path.basename(norm_path):
                    page.metadata['doc_id'] = doc_id
                    enriched_count += 1
                    matched = True
                    break
        
        if not matched:
            failed_to_match.append((idx, source_path))
            page.metadata['doc_id'] = 'unknown'
    
    print(f"成功为 {enriched_count}/{len(doc)} 个页面添加doc_id")
    if failed_to_match:
        print(f"警告：{len(failed_to_match)} 个页面无法匹配doc_id")
    
    # 分割文档并准备metadata
    splits = []
    metas = []
    
    print(f"\n开始分割文档并准备metadata...")
    for page in tqdm(doc, desc="分割文档"):
        page_splits = r_splitter.split_text(page.page_content)
        splits.extend(page_splits)
        
        for _ in page_splits:
            clean_meta = sanitize_metadata(page.metadata)
            metas.append(clean_meta)
    
    print(f"总分割数量: {len(splits)}")
    print(f"总元数据数量: {len(metas)}")
    
    # 检查唯一doc_id
    doc_ids = [m.get('doc_id', 'unknown') for m in metas]
    unique_doc_ids = set(doc_ids)
    print(f"找到 {len(unique_doc_ids)} 个唯一doc_id")
    
    # 创建向量嵌入
    print(f"\n开始创建向量嵌入...")
    try:
        embeddings = model.encode(splits, 
                            batch_size=batch_size, 
                            max_length=max_length)['dense_vecs']
        print(f"✓ 成功创建 {len(embeddings)} 个向量嵌入")
    except Exception as e:
        print(f"✗ 错误：创建嵌入失败: {e}")
        return
    
    # 添加到ChromaDB
    print(f"\n连接ChromaDB并添加文档...")
    try:
        client = chromadb.PersistentClient(path=persist_directory)
        collection = client.get_or_create_collection(name=dbname)
        
        collection.add(
            ids=["id%s" % j for j in range(len(splits))],
            documents=splits,
            metadatas=metas,
            embeddings=embeddings
        )
        print(f"✓ 成功添加所有文档到数据库")
    except Exception as e:
        print(f"✗ 错误：添加到ChromaDB失败: {e}")
        import traceback
        print(f"详细错误信息:\n{traceback.format_exc()}")
        return
    
    print(f"\n{'='*60}")
    print(f"✓ 成功创建数据库 '{dbname}'")
    print(f"  - 文档块数量: {len(splits)}")
    print(f"  - 唯一doc_id数量: {len(unique_doc_ids)}")
    print(f"{'='*60}")


def query_vector_db(questions: Union[str, List[str]],
                    collection_name: str,
                    top_k: int = 20,
                    persist_directory: str = 'D:\\App\\Mydata\\ragdb\\',
                    model_path: str = 'C:\\Users\\47577\\bge-m3',
                    batch_size: int = 4,
                    max_length: int = 1024,
                    use_cuda: bool = True) -> Tuple[List, List]:
    """
    查询向量数据库
    
    Args:
        questions: 查询问题（字符串或列表）
        collection_name: 集合名称
        top_k: 返回结果数量
        persist_directory: 数据库目录
        model_path: 模型路径
        batch_size: 批处理大小
        max_length: 最大序列长度
        use_cuda: 是否使用CUDA加速
        
    Returns:
        (documents, metadata): 文档列表和对应的元数据列表
    """
    client = chromadb.PersistentClient(path=persist_directory)
    collection = client.get_or_create_collection(name=collection_name)
    
    # 加载模型（启用CUDA）
    model = BGEM3FlagModel(model_path, use_fp16=True, device='cuda:0' if use_cuda else 'cpu')

    if isinstance(questions, str):
        questions = [questions]

    embeddings = model.encode(questions,
                              batch_size=batch_size,
                              max_length=max_length)['dense_vecs']
    
    results = collection.query(
        query_embeddings=embeddings,
        n_results=top_k)

    res = []
    meta_data = []
    for doc in results["documents"]:
        res.extend(doc)
    for doc in results["metadatas"]:
        meta_data.extend(doc)

    return res, meta_data


# ============================================================================
# AI Agent功能模块
# ============================================================================

# 加载环境变量
load_dotenv('D://Agents//arxiv_vectordb-master//API.env')


class Agent:
    """
    AI对话代理 - 在线版本（基于OpenAI API）
    
    使用DeepSeek Chat模型进行对话
    """
    
    def __init__(self, prompt: str):
        """
        初始化Agent
        
        Args:
            prompt: 系统提示词
        """
        self.model = OpenAI(api_key=os.getenv("MIMO_API_KEY"),
                            base_url=os.getenv("BASE_URL"))
        self.prompt = prompt
        self.messages = [{"role": "system", "content": prompt}]

    def chat(self, user_input: str, context: str = "", 
             stream: bool = True, temperature: float = 0.6):
        """
        进行对话
        
        Args:
            user_input: 用户输入
            context: 上下文信息
            stream: 是否流式输出
            temperature: 温度参数
            
        Returns:
            流式响应对象或完整响应文本
        """
        user_message = f"{user_input}."
        
        if context:
            user_message = f"已知\n:{context}" + "\n" + user_message
        
        self.messages.append({"role": "user", "content": user_message})
        
        response = self.model.chat.completions.create(
            model="mimo-v2-flash",
            messages=self.messages,
            temperature=temperature,
            stream=stream)
        
        if stream:
            return response
        else:
            self.messages.append(response.choices[0].message)
            return response.choices[0].message.content

    def collect_message(self, gen_txt: str):
        """
        保存消息到历史记录
        
        Args:
            gen_txt: 生成的文本
        """
        self.messages.append({"role": "assistant", "content": gen_txt})


class AgentLocal:
    """
    AI对话代理 - 本地版本（基于Ollama）
    
    使用本地运行的Ollama服务进行对话
    """
    
    def __init__(self, prompt: str):
        """
        初始化本地Agent
        
        Args:
            prompt: 系统提示词
        """
        self.prompt = prompt
        self.messages = [{"role": "system", "content": prompt}]

    def chat(self, user_input: str, context: str = "", 
             stream: bool = False, temperature: float = 0.6):
        """
        进行对话
        
        Args:
            user_input: 用户输入
            context: 上下文信息
            stream: 是否流式输出（本地版本暂不支持）
            temperature: 温度参数
            
        Returns:
            响应文本或None（如果请求失败）
        """
        user_message = f"{user_input}."
        
        if context:
            user_message = f"已知\n:{context}" + "\n" + user_message
        
        self.messages.append({"role": "user", "content": user_message})
        
        url = "http://localhost:11434/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        data = {
            "model": "deepseek-r1:1.5b",
            "messages": self.messages
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            response_data = response.json()
            self.messages.append(response_data['choices'][0]['message'])
            return response_data['choices'][0]['message']['content']
        else:
            print(f"请求失败，状态码：{response.status_code}")
            return None

    def collect_message(self, gen_txt: str):
        """
        保存消息到历史记录
        
        Args:
            gen_txt: 生成的文本
        """
        self.messages.append({"role": "assistant", "content": gen_txt})


# ============================================================================
# 文献综述功能模块
# ============================================================================

def clean_generated_text(gen_text: str) -> str:
    """
    清理生成的文本，去除 <think> 标签及其内容
    
    Args:
        gen_text: 生成的原始文本
        
    Returns:
        清理后的文本
    """
    return re.sub(r'<think>.*?</think>', '', gen_text, flags=re.DOTALL).strip()


def literature_review(user_input: str, 
                     gen_time_txt: str, 
                     gen_logic_txt: str,
                     use_stream: bool = False) -> str:
    """
    生成文献综述
    
    基于时间线信息和逻辑连接信息生成学术文献综述
    
    Args:
        user_input: 研究主题
        gen_time_txt: 时间线信息
        gen_logic_txt: 逻辑连接信息
        use_stream: 是否使用流式输出
        
    Returns:
        生成的文献综述文本（如果use_stream=True则返回响应对象）
    """
    prompt = '''
            - Role: You are a professional Physicist and an excellent literature review writer who is meticulous and rigorous, specializing in academic research.

            - Skills: Analyze the user's research topic and the timeline information and the logical connections of the research results 
                    which had been generated from the articles in the vectordatabase, and write an excellent literature review using the given information only.
                    DO NOT include external knowledge or assumptions. All content must be traceable to the given sources.

            - Constraints: 
                - Write a literature review in the specified format, without any additional text or commentary.
                - Use only the information provided by the user. Do not include external knowledge or assumptions. All content must be traceable to the given sources.
            
            - Task:
                - Summarize the cause, development, and key findings of each research effort.
                - Identify and explain the logical connections, contradictions, or consensus among the studies.
                - Discuss the evolution of ideas or methodologies within the topic.
                - Highlight contributions to the field and potential areas for future research.
            
            - Format:
                - Write in clear, formal academic English.
                - Structure the review thematically, chronologically, or methodologically, as appropriate.
                - Include in-text citations for each source (e.g., [1], [2]) as referenced in the provided materials.
                - Avoid bullet points or numbered lists—use continuous prose with coherent paragraphs.
            
            - Note: Return the literature review in English. Do not add any information outside what is provided.
            '''
    
    agent = Agent(prompt)
    context = (f"The topic input by user is {str(user_input)}. "
              f"The timeline information is {str(gen_time_txt)}. "
              f"The logical connections of the research results are {str(gen_logic_txt)}. "
              f"Now write a literature review in the specified format:")
    
    gen_text = agent.chat(user_input, context=context, stream=use_stream)
    
    if not use_stream:
        gen_text = clean_generated_text(gen_text)
    
    return gen_text


# ============================================================================
# 辅助工具函数
# ============================================================================

def verify_metadata(collection_name: str,
                   persist_directory: str = 'D:\\App\\Mydata\\ragdb\\',
                   num_samples: int = 5) -> None:
    """
    验证数据库中的metadata是否正确存储
    
    Args:
        collection_name: 集合名称
        persist_directory: 数据库目录
        num_samples: 检查的样本数量
    """
    client = chromadb.PersistentClient(path=persist_directory)
    collection = client.get_collection(name=collection_name)
    
    print(f"\n=== 验证数据库 '{collection_name}' 的metadata ===")
    print(f"文档总数: {collection.count()}")
    
    # 获取样本
    sample_ids = [f"id{i}" for i in range(num_samples)]
    sample_results = collection.get(ids=sample_ids, include=["metadatas"])
    
    print(f"\n前{num_samples}个文档的metadata:")
    all_valid = True
    for i, meta in enumerate(sample_results['metadatas']):
        print(f"\nid{i}:")
        print(f"  Metadata: {meta}")
        if meta and 'doc_id' in meta and meta['doc_id'] != 'unknown':
            print(f"  ✓ doc_id: {meta['doc_id']}")
        else:
            print(f"  ✗ metadata缺失或无效")
            all_valid = False
    
    if all_valid:
        print(f"\n✓ 所有样本的metadata都正确嵌入！")
    else:
        print(f"\n✗ 部分样本的metadata有问题，请检查。")


# ============================================================================
# 模块信息
# ============================================================================

__version__ = "2.0"
__author__ = "AI Assistant"
__all__ = [
    # RAG功能
    'sanitize_filename',
    'sanitize_metadata',
    'load_pdf',
    'load_pdfs',
    'load_pdfs_info',
    'create_vector_db',
    'query_vector_db',
    # AI Agent
    'Agent',
    'AgentLocal',
    # 文献综述
    'literature_review',
    'clean_generated_text',
    # 工具函数
    'verify_metadata'
]


if __name__ == "__main__":
    print("="*70)
    print("RAG Core Module v2.0 - 统一核心模块")
    print("="*70)
    print("\n可用功能：")
    print("1. RAG功能: load_pdfs_info, create_vector_db, query_vector_db")
    print("2. AI Agent: Agent (在线), AgentLocal (本地)")
    print("3. 文献综述: literature_review")
    print("4. 工具函数: verify_metadata")
    print("\n使用示例:")
    print("  from rag_core import create_vector_db, query_vector_db, Agent")
    print("\n详细文档请查看 README_COMPLETE.md")

