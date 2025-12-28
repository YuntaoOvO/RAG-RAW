@echo off
REM ============================================================================
REM RAG-RAW 项目安装脚本 (Windows)
REM ============================================================================
REM 功能：
REM   1. 检测Python版本
REM   2. 创建虚拟环境 ai_scientist_env
REM   3. 安装项目依赖
REM   4. 创建必要的目录结构
REM   5. 创建 .env 配置文件模板
REM   6. 提供激活虚拟环境的说明
REM
REM 使用方法：
REM   setup.bat
REM ============================================================================

setlocal enabledelayedexpansion

REM 获取项目根目录（脚本所在目录）
set "PROJECT_ROOT=%~dp0"
set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"
set "VENV_NAME=ai_scientist_env"
set "VENV_PATH=%PROJECT_ROOT%\%VENV_NAME%"

echo.
echo ========================================
echo RAG-RAW 项目安装向导
echo ========================================
echo.

REM ============================================================================
REM 步骤 1: 检测Python版本
REM ============================================================================
echo [INFO] 步骤 1/6: 检测Python环境...

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到 python，请先安装 Python 3.10 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [SUCCESS] Python 版本: %PYTHON_VERSION% ✓
echo.

REM ============================================================================
REM 步骤 2: 创建虚拟环境
REM ============================================================================
echo [INFO] 步骤 2/6: 创建虚拟环境...

if exist "%VENV_PATH%" (
    echo [WARNING] 虚拟环境已存在: %VENV_PATH%
    set /p RECREATE="是否删除并重新创建? (y/N): "
    if /i "!RECREATE!"=="y" (
        echo [INFO] 删除现有虚拟环境...
        rmdir /s /q "%VENV_PATH%"
        set SKIP_VENV_CREATE=false
    ) else (
        echo [INFO] 使用现有虚拟环境
        set SKIP_VENV_CREATE=true
    )
) else (
    set SKIP_VENV_CREATE=false
)

if "!SKIP_VENV_CREATE!"=="false" (
    echo [INFO] 创建虚拟环境: %VENV_PATH%
    python -m venv "%VENV_PATH%"
    if errorlevel 1 (
        echo [ERROR] 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo [SUCCESS] 虚拟环境创建成功 ✓
) else (
    echo [SUCCESS] 使用现有虚拟环境 ✓
)
echo.

REM ============================================================================
REM 步骤 3: 激活虚拟环境并升级pip
REM ============================================================================
echo [INFO] 步骤 3/6: 激活虚拟环境并升级pip...

call "%VENV_PATH%\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] 虚拟环境激活失败
    pause
    exit /b 1
)

echo [INFO] 升级 pip...
python -m pip install --upgrade pip --quiet
echo [SUCCESS] pip 升级完成 ✓
echo.

REM ============================================================================
REM 步骤 4: 安装项目依赖
REM ============================================================================
echo [INFO] 步骤 4/6: 安装项目依赖...

if not exist "%PROJECT_ROOT%\requirements.txt" (
    echo [ERROR] 未找到 requirements.txt 文件
    pause
    exit /b 1
)

echo [INFO] 安装核心依赖包（这可能需要几分钟）...
pip install -r "%PROJECT_ROOT%\requirements.txt"
if errorlevel 1 (
    echo [WARNING] 部分依赖安装可能失败，请检查错误信息
)

echo [INFO] 安装可选依赖...
pip install pythia8mc >nul 2>&1
if errorlevel 1 (
    echo [WARNING] pythia8mc 安装失败（可选，可稍后手动安装）
) else (
    echo [SUCCESS] pythia8mc 安装成功
)

echo [SUCCESS] 依赖安装完成 ✓
echo.

REM ============================================================================
REM 步骤 5: 创建必要的目录结构
REM ============================================================================
echo [INFO] 步骤 5/6: 创建项目目录结构...

set DIRS=output output\react_sessions pythia_workspace pythia_workspace\scripts pythia_workspace\events pythia_workspace\results pythia_workspace\figures ragdb pdfs bib models

for %%d in (%DIRS%) do (
    set "DIR_PATH=%PROJECT_ROOT%\%%d"
    if not exist "!DIR_PATH!" (
        mkdir "!DIR_PATH!" >nul 2>&1
        echo [INFO] 创建目录: !DIR_PATH!
    )
)

echo [SUCCESS] 目录结构创建完成 ✓
echo.

REM ============================================================================
REM 步骤 6: 创建 .env 配置文件模板
REM ============================================================================
echo [INFO] 步骤 6/6: 创建配置文件...

set "ENV_FILE=%PROJECT_ROOT%\.env"

if not exist "%ENV_FILE%" (
    (
        echo # ============================================================================
        echo # RAG-RAW 环境变量配置
        echo # ============================================================================
        echo # 请填写您的API密钥
        echo # ============================================================================
        echo.
        echo # MIMO API 配置（推荐）
        echo MIMO_API_KEY=your_mimo_api_key_here
        echo # 如果使用MIMO API，无需设置下面的OPENAI配置
        echo.
        echo # OpenAI API 配置（可选）
        echo # OPENAI_API_KEY=your_openai_api_key_here
        echo # OPENAI_API_BASE=https://api.openai.com/v1
        echo.
        echo # 自定义API配置（可选）
        echo # CUSTOM_API_KEY=your_custom_api_key_here
        echo # CUSTOM_API_BASE=https://your-api-endpoint.com/v1
        echo.
        echo # ============================================================================
        echo # 模型路径配置（可选，如果使用默认路径可忽略）
        echo # ============================================================================
        echo # BGE_MODEL_PATH=/path/to/bge-m3
    ) > "%ENV_FILE%"
    echo [SUCCESS] .env 文件已创建 ✓
    echo [WARNING] 请编辑 .env 文件并填写您的API密钥
) else (
    echo [INFO] .env 文件已存在，跳过创建
)

REM 创建 .env.template
(
    echo # ============================================================================
    echo # RAG-RAW 环境变量配置模板
    echo # ============================================================================
    echo # 复制此文件为 .env 并填写实际值
    echo # ============================================================================
    echo.
    echo MIMO_API_KEY=your_mimo_api_key_here
    echo # OPENAI_API_KEY=your_openai_api_key_here
    echo # OPENAI_API_BASE=https://api.openai.com/v1
) > "%PROJECT_ROOT%\.env.template"

echo [SUCCESS] 配置文件创建完成 ✓
echo.

REM ============================================================================
REM 安装完成提示
REM ============================================================================
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo [SUCCESS] 项目已成功安装到: %PROJECT_ROOT%
echo.

echo [INFO] 下一步操作：
echo.
echo 1. 激活虚拟环境：
echo    %VENV_NAME%\Scripts\activate
echo.
echo 2. 配置API密钥：
echo    编辑 .env 文件，填写您的API密钥
echo.
echo 3. （可选）下载BGE-M3模型：
echo    模型下载地址: https://huggingface.co/BAAI/bge-m3
echo    建议保存到: %PROJECT_ROOT%\models\bge-m3
echo.
echo 4. 运行项目：
echo    streamlit run react_streamlit.py
echo.

REM 创建快速激活脚本
(
    echo @echo off
    echo REM 快速激活虚拟环境脚本 (Windows)
    echo call "%VENV_NAME%\Scripts\activate.bat"
    echo echo 虚拟环境已激活: %VENV_NAME%
    echo echo 项目目录: %PROJECT_ROOT%
    echo echo.
    echo echo 运行项目: streamlit run react_streamlit.py
    echo echo 退出虚拟环境: deactivate
) > "%PROJECT_ROOT%\activate_env.bat"

echo [INFO] 已创建快速激活脚本: activate_env.bat
echo.

echo [WARNING] 重要提示：
echo   - 每次使用项目前，请先激活虚拟环境
echo   - 确保已配置 .env 文件中的API密钥
echo   - 如需GPU加速，请安装CUDA版本的PyTorch
echo.

echo [SUCCESS] 安装完成！祝您使用愉快！
echo.

pause

