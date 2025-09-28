#!/usr/bin/env python3
"""
重启应用脚本
"""

import subprocess
import sys
import time
import os

def kill_python_processes():
    """终止Python进程"""
    try:
        # 在Windows上终止占用5005端口的进程
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        for line in lines:
            if ':5005' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    print(f"终止占用端口5005的进程 PID: {pid}")
                    subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
                    
    except Exception as e:
        print(f"终止进程时出错: {e}")

def start_app():
    """启动应用"""
    print("启动voice_app.py...")
    try:
        # 启动应用
        subprocess.Popen([sys.executable, 'voice_app.py'])
        print("应用启动成功！")
        print("访问地址: http://localhost:5005")
    except Exception as e:
        print(f"启动应用失败: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("🔄 重启AI角色扮演应用")
    print("=" * 50)
    
    # 终止现有进程
    kill_python_processes()
    time.sleep(2)
    
    # 启动新应用
    start_app()
    
    print("=" * 50)
    print("✅ 重启完成")
    print("=" * 50)