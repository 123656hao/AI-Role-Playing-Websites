# PowerShell脚本：初始化Git仓库并推送到远程

Write-Host "正在初始化Git仓库并推送到远程..." -ForegroundColor Green

try {
    # 检查Git是否安装
    $gitVersion = git --version 2>$null
    if (-not $gitVersion) {
        Write-Host "错误: Git未安装。请先安装Git: https://git-scm.com/download/windows" -ForegroundColor Red
        Read-Host "按任意键退出"
        exit 1
    }
    
    Write-Host "Git版本: $gitVersion" -ForegroundColor Yellow

    # 初始化Git仓库
    Write-Host "初始化Git仓库..." -ForegroundColor Cyan
    git init

    # 添加远程仓库
    Write-Host "添加远程仓库..." -ForegroundColor Cyan
    git remote add origin https://github.com/123656hao/AI-Role-Playing-Websites.git

    # 检查是否已有.gitignore文件
    if (-not (Test-Path ".gitignore")) {
        Write-Host "创建.gitignore文件..." -ForegroundColor Cyan
        @"
__pycache__/
*.pyc
.env
logs/
static/audio/
.vscode/
.idea/
node_modules/
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8
    }

    # 添加所有文件
    Write-Host "添加文件到Git..." -ForegroundColor Cyan
    git add .

    # 提交代码
    Write-Host "提交代码..." -ForegroundColor Cyan
    git commit -m "初次提交"

    # 设置主分支
    Write-Host "设置主分支..." -ForegroundColor Cyan
    git branch -M main

    # 推送到远程仓库
    Write-Host "推送到远程仓库..." -ForegroundColor Cyan
    git push -u origin main

    Write-Host "完成！代码已成功推送到GitHub仓库" -ForegroundColor Green
    Write-Host "仓库地址: https://github.com/123656hao/AI-Role-Playing-Websites" -ForegroundColor Yellow

} catch {
    Write-Host "错误: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "请检查网络连接和GitHub仓库权限" -ForegroundColor Yellow
}

Read-Host "按任意键退出"