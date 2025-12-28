#!/bin/bash

# ============================================================================
# RAG-RAW 项目安装脚本
# ============================================================================
# 功能：
#   1. 检测Python版本
#   2. 创建虚拟环境 ai_scientist_env
#   3. 安装项目依赖
#   4. 创建必要的目录结构
#   5. 创建 .env 配置文件模板
#   6. 提供激活虚拟环境的说明
#
# 使用方法：
#   bash setup.sh
#   或
#   chmod +x setup.sh && ./setup.sh
# ============================================================================

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 打印标题
print_title() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
}

# 获取项目根目录（脚本所在目录）
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_NAME="(ai_scientist_env)"
VENV_PATH="${PROJECT_ROOT}/${VENV_NAME}"

print_title "RAG-RAW 项目安装向导"

# ============================================================================
# 步骤 1: 检测Python版本
# ============================================================================
print_info "步骤 1/6: 检测Python环境..."

if ! command -v python3 &> /dev/null; then
    print_error "未找到 python3，请先安装 Python 3.10 或更高版本"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    print_error "Python 版本过低: $PYTHON_VERSION"
    print_error "需要 Python 3.10 或更高版本"
    exit 1
fi

print_success "Python 版本: $PYTHON_VERSION ✓"

# 检测是否已安装 venv 模块
if ! python3 -m venv --help &> /dev/null; then
    print_error "Python venv 模块未安装"
    print_info "在 Ubuntu/Debian 上运行: sudo apt-get install python3-venv"
    print_info "在 CentOS/RHEL 上运行: sudo yum install python3-venv"
    exit 1
fi

# ============================================================================
# 步骤 2: 创建虚拟环境
# ============================================================================
print_info "步骤 2/6: 创建虚拟环境..."

if [ -d "$VENV_PATH" ]; then
    print_warning "虚拟环境已存在: $VENV_PATH"
    read -p "是否删除并重新创建? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "删除现有虚拟环境..."
        rm -rf "$VENV_PATH"
    else
        print_info "使用现有虚拟环境"
        SKIP_VENV_CREATE=true
    fi
fi

if [ "$SKIP_VENV_CREATE" != true ]; then
    print_info "创建虚拟环境: $VENV_PATH"
    python3 -m venv "$VENV_PATH"
    print_success "虚拟环境创建成功 ✓"
else
    print_success "使用现有虚拟环境 ✓"
fi

# ============================================================================
# 步骤 3: 激活虚拟环境并升级pip
# ============================================================================
print_info "步骤 3/6: 激活虚拟环境并升级pip..."

# 激活虚拟环境
source "${VENV_PATH}/bin/activate"

# 升级pip
print_info "升级 pip..."
pip install --upgrade pip --quiet

print_success "pip 升级完成 ✓"

# ============================================================================
# 步骤 4: 安装项目依赖
# ============================================================================
print_info "步骤 4/6: 安装项目依赖..."

if [ ! -f "${PROJECT_ROOT}/requirements.txt" ]; then
    print_error "未找到 requirements.txt 文件"
    exit 1
fi

print_info "安装核心依赖包（这可能需要几分钟）..."
pip install -r "${PROJECT_ROOT}/requirements.txt"

# 安装可选依赖
print_info "安装可选依赖..."
pip install pythia8mc 2>/dev/null || print_warning "pythia8mc 安装失败（可选，可稍后手动安装）"

print_success "依赖安装完成 ✓"

# ============================================================================
# 步骤 5: 创建必要的目录结构
# ============================================================================
print_info "步骤 5/6: 创建项目目录结构..."

DIRS=(
    "${PROJECT_ROOT}/output"
    "${PROJECT_ROOT}/output/react_sessions"
    "${PROJECT_ROOT}/pythia_workspace"
    "${PROJECT_ROOT}/pythia_workspace/scripts"
    "${PROJECT_ROOT}/pythia_workspace/events"
    "${PROJECT_ROOT}/pythia_workspace/results"
    "${PROJECT_ROOT}/pythia_workspace/figures"
    "${PROJECT_ROOT}/ragdb"
    "${PROJECT_ROOT}/pdfs"
    "${PROJECT_ROOT}/bib"
    "${PROJECT_ROOT}/models"
)

for dir in "${DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        print_info "创建目录: $dir"
    fi
done

print_success "目录结构创建完成 ✓"

# ============================================================================
# 步骤 6: 创建 .env 配置文件模板
# ============================================================================
print_info "步骤 6/6: 创建配置文件..."

ENV_FILE="${PROJECT_ROOT}/.env"
ENV_TEMPLATE="${PROJECT_ROOT}/.env.template"

if [ ! -f "$ENV_FILE" ]; then
    cat > "$ENV_FILE" << 'EOF'
# ============================================================================
# RAG-RAW 环境变量配置
# ============================================================================
# 请填写您的API密钥
# ============================================================================

# MIMO API 配置（推荐）
MIMO_API_KEY=your_mimo_api_key_here
# 如果使用MIMO API，无需设置下面的OPENAI配置

# OpenAI API 配置（可选）
# OPENAI_API_KEY=your_openai_api_key_here
# OPENAI_API_BASE=https://api.openai.com/v1

# 自定义API配置（可选）
# CUSTOM_API_KEY=your_custom_api_key_here
# CUSTOM_API_BASE=https://your-api-endpoint.com/v1

# ============================================================================
# 模型路径配置（可选，如果使用默认路径可忽略）
# ============================================================================
# BGE_MODEL_PATH=/path/to/bge-m3
EOF
    print_success ".env 文件已创建 ✓"
    print_warning "请编辑 .env 文件并填写您的API密钥"
else
    print_info ".env 文件已存在，跳过创建"
fi

# 创建 .env.template 作为参考
cat > "$ENV_TEMPLATE" << 'EOF'
# ============================================================================
# RAG-RAW 环境变量配置模板
# ============================================================================
# 复制此文件为 .env 并填写实际值
# ============================================================================

MIMO_API_KEY=your_mimo_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here
# OPENAI_API_BASE=https://api.openai.com/v1
EOF

print_success "配置文件创建完成 ✓"

# ============================================================================
# 安装完成提示
# ============================================================================
print_title "安装完成！"

echo ""
print_success "项目已成功安装到: $PROJECT_ROOT"
echo ""

# 检测操作系统类型
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    ACTIVATE_CMD="${VENV_NAME}\\Scripts\\activate"
    OS_TYPE="Windows"
else
    ACTIVATE_CMD="source ${VENV_NAME}/bin/activate"
    OS_TYPE="Linux/MacOS"
fi

print_info "下一步操作："
echo ""
echo "1. 激活虚拟环境："
echo -e "   ${GREEN}${ACTIVATE_CMD}${NC}"
echo ""
echo "2. 配置API密钥："
echo -e "   编辑 ${YELLOW}.env${NC} 文件，填写您的API密钥"
echo ""
echo "3. （可选）下载BGE-M3模型："
echo "   模型下载地址: https://huggingface.co/BAAI/bge-m3"
echo "   建议保存到: ${PROJECT_ROOT}/models/bge-m3"
echo ""
echo "4. 运行项目："
echo -e "   ${GREEN}streamlit run react_streamlit.py${NC}"
echo ""

# 提供快速激活脚本
ACTIVATE_SCRIPT="${PROJECT_ROOT}/activate_env.sh"
if [ "$OS_TYPE" != "Windows" ]; then
    cat > "$ACTIVATE_SCRIPT" << EOF
#!/bin/bash
# 快速激活虚拟环境脚本
source "${VENV_PATH}/bin/activate"
echo "虚拟环境已激活: ${VENV_NAME}"
echo "项目目录: ${PROJECT_ROOT}"
echo ""
echo "运行项目: streamlit run react_streamlit.py"
echo "退出虚拟环境: deactivate"
EOF
    chmod +x "$ACTIVATE_SCRIPT"
    print_info "已创建快速激活脚本: activate_env.sh"
    echo ""
fi

# Windows批处理文件
ACTIVATE_BAT="${PROJECT_ROOT}/activate_env.bat"
cat > "$ACTIVATE_BAT" << EOF
@echo off
REM 快速激活虚拟环境脚本 (Windows)
call "${VENV_NAME}\\Scripts\\activate.bat"
echo 虚拟环境已激活: ${VENV_NAME}
echo 项目目录: ${PROJECT_ROOT}
echo.
echo 运行项目: streamlit run react_streamlit.py
echo 退出虚拟环境: deactivate
EOF

print_info "已创建Windows激活脚本: activate_env.bat"
echo ""

print_warning "重要提示："
echo "  - 每次使用项目前，请先激活虚拟环境"
echo "  - 确保已配置 .env 文件中的API密钥"
echo "  - 如需GPU加速，请安装CUDA版本的PyTorch"
echo ""

print_success "安装完成！祝您使用愉快！"
echo ""

