#!/usr/bin/env python3
"""
启动Web实时语音识别测试
"""

import os
import sys
import webbrowser
import time
import threading
from app import app, start_web_realtime_server, WEBSOCKETS_AVAILABLE

def main():
    """主函数"""
    print("🎤 启动Web实时语音识别测试...")
    print("=" * 50)
    
    if not WEBSOCKETS_AVAILABLE:
        print("❌ WebSocket库未安装，无法启动实时语音服务")
        print("请运行: pip install websockets")
        return
    
    try:
        # 启动Web实时语音服务器
        print("🚀 启动Web实时语音识别服务器...")
        start_web_realtime_server()
        
        # 等待服务器启动
        time.sleep(2)
        
        # 启动Flask应用
        print("🌐 启动Web应用...")
        
        def open_browser():
            time.sleep(3)  # 等待Flask启动
            url = "http://localhost:5000/web_realtime_demo.html"
            print(f"🔗 自动打开浏览器: {url}")
            webbrowser.open(url)
        
        # 在后台线程中打开浏览器
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()
        
        print("📍 访问地址:")
        print("  - 主应用: http://localhost:5000")
        print("  - Web实时语音演示: http://localhost:5000/web_realtime_demo.html")
        print("  - WebSocket服务: ws://localhost:8766")
        print("=" * 50)
        print("💡 使用说明:")
        print("  1. 在浏览器中点击'连接服务'")
        print("  2. 点击'开始录音'进行实时语音识别")
        print("  3. 说中文即可看到实时识别结果")
        print("  4. 按Ctrl+C停止服务")
        print("=" * 50)
        
        # 启动Flask应用
        app.run(
            host='localhost',
            port=5000,
            debug=False,
            use_reloader=False
        )
        
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()