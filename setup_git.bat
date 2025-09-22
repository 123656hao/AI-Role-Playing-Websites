@echo off
echo 正在初始化Git仓库并推送到远程...

REM 初始化Git仓库
git init

REM 添加远程仓库
git remote add origin https://github.com/123656hao/AI-Role-Playing-Websites.git

REM 创建.gitignore文件
echo __pycache__/ > .gitignore
echo *.pyc >> .gitignore
echo .env >> .gitignore
echo logs/ >> .gitignore
echo static/audio/ >> .gitignore
echo .vscode/ >> .gitignore
echo .idea/ >> .gitignore
echo node_modules/ >> .gitignore

REM 添加所有文件
git add .

REM 提交代码
git commit -m "初次提交"

REM 设置主分支
git branch -M main

REM 推送到远程仓库
git push -u origin main

echo 完成！代码已推送到GitHub仓库
pause