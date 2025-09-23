@echo off
echo ========================================
echo AI角色扮演聊天网站 - 环境恢复脚本
echo ========================================
echo.

echo [1/6] 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo [2/6] 创建虚拟环境...
if not exist ".venv" (
    python -m venv .venv
    echo 虚拟环境已创建
) else (
    echo 虚拟环境已存在
)

echo [3/6] 激活虚拟环境...
call .venv\Scripts\activate.bat

echo [4/6] 升级pip...
python -m pip install --upgrade pip

echo [5/6] 安装项目依赖...
pip install -r requirements.txt

echo [6/6] 创建必要目录...
if not exist "static\audio" mkdir static\audio
if not exist "logs" mkdir logs
if not exist "static\images" mkdir static\images

echo.
echo ========================================
echo 环境恢复完成！
echo ========================================
echo.
echo 下一步操作:
echo 1. 编辑 .env 文件，填入你的豆包AI API密钥
echo 2. 检查 config\voice_settings.json 中的语音API配置
echo 3. 运行 python app.py 启动应用
echo 4. 访问 http://localhost:5000
echo.
echo 按任意键继续...
pause > nul