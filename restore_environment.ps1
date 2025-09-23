# AI角色扮演聊天网站 - 环境恢复脚本 (PowerShell版本)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI角色扮演聊天网站 - 环境恢复脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Python环境
Write-Host "[1/6] 检查Python环境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python版本: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "错误: 未找到Python，请先安装Python 3.8+" -ForegroundColor Red
    Read-Host "按Enter键退出"
    exit 1
}

# 创建虚拟环境
Write-Host "[2/6] 创建虚拟环境..." -ForegroundColor Yellow
if (-not (Test-Path ".venv")) {
    python -m venv .venv
    Write-Host "虚拟环境已创建" -ForegroundColor Green
} else {
    Write-Host "虚拟环境已存在" -ForegroundColor Green
}

# 激活虚拟环境
Write-Host "[3/6] 激活虚拟环境..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"

# 升级pip
Write-Host "[4/6] 升级pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# 安装依赖
Write-Host "[5/6] 安装项目依赖..." -ForegroundColor Yellow
pip install -r requirements.txt

# 创建必要目录
Write-Host "[6/6] 创建必要目录..." -ForegroundColor Yellow
$directories = @("static\audio", "logs", "static\images")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "创建目录: $dir" -ForegroundColor Green
    } else {
        Write-Host "目录已存在: $dir" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "环境恢复完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步操作:" -ForegroundColor Yellow
Write-Host "1. 编辑 .env 文件，填入你的豆包AI API密钥" -ForegroundColor White
Write-Host "2. 检查 config\voice_settings.json 中的语音API配置" -ForegroundColor White
Write-Host "3. 运行 python app.py 启动应用" -ForegroundColor White
Write-Host "4. 访问 http://localhost:5000" -ForegroundColor White
Write-Host ""
Read-Host "按Enter键继续"