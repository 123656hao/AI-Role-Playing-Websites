# Git设置指南

由于系统未安装Git，请按照以下步骤完成代码提交：

## 方法一：安装Git后自动执行

### 1. 安装Git
访问 [Git官网](https://git-scm.com/download/windows) 下载并安装Git for Windows

### 2. 运行自动化脚本
安装Git后，在项目目录下运行以下任一脚本：

**批处理脚本（推荐）：**
```cmd
setup_git.bat
```

**PowerShell脚本：**
```powershell
.\setup_git.ps1
```

## 方法二：手动执行Git命令

### 1. 打开Git Bash或命令提示符

### 2. 执行以下命令：

```bash
# 初始化Git仓库
git init

# 添加远程仓库
git remote add origin https://github.com/123656hao/AI-Role-Playing-Websites.git

# 添加所有文件
git add .

# 提交代码
git commit -m "初次提交"

# 设置主分支
git branch -M main

# 推送到远程仓库
git push -u origin main
```

## 方法三：使用GitHub Desktop

### 1. 下载GitHub Desktop
访问 [GitHub Desktop官网](https://desktop.github.com/) 下载并安装

### 2. 操作步骤：
1. 打开GitHub Desktop
2. 选择 "Add an Existing Repository from your Hard Drive"
3. 选择项目文件夹
4. 点击 "Publish repository"
5. 设置仓库名称为 "AI-Role-Playing-Websites"
6. 取消勾选 "Keep this code private"（如果要公开）
7. 点击 "Publish Repository"

## 注意事项

1. **确保.gitignore文件存在**，避免提交敏感文件
2. **不要提交.env文件**，其中包含API密钥
3. **检查仓库权限**，确保有推送权限
4. **首次推送可能需要GitHub认证**

## 文件说明

项目已创建以下文件帮助Git操作：
- `.gitignore` - 忽略不需要版本控制的文件
- `setup_git.bat` - Windows批处理自动化脚本
- `setup_git.ps1` - PowerShell自动化脚本
- `README.md` - 项目说明文档

## 验证提交

提交成功后，访问以下地址验证：
https://github.com/123656hao/AI-Role-Playing-Websites

应该能看到所有项目文件已上传到仓库。