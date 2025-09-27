#!/usr/bin/env python3
"""
简化的应用启动脚本
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def main():
    """启动应用"""
    print("🚀 启动AI角色扮演应用...")
    
    # 创建必要目录
    dirs = ['static/audio', 'data', 'logs']
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ 确保目录存在: {dir_path}")
    
    # 检查.env文件
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️ .env 文件不存在，创建示例文件...")
        with open('.env', 'w', encoding='utf-8') as f:
            f.write("""# AI API配置
ARK_API_KEY=your_api_key_here
OPENAI_API_BASE=https://ark.cn-beijing.volces.com/api/v3
OPENAI_MODEL=doubao-seed-1-6-250615

# 应用配置
SECRET_KEY=ai-roleplay-secret-2024
""")
        print("📝 已创建 .env 示例文件")
    
    try:
        # 启动Flask应用
        print("🌐 启动服务器...")
        os.system("python app.py")
        
    except KeyboardInterrupt:
        print("\n🛑 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())