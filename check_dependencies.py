#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖检查脚本
检查AI角色扮演网站所需的关键依赖是否已正确安装
"""

import sys

def check_dependencies():
    print("🔍 检查AI角色扮演网站依赖...")
    print("=" * 50)
    
    dependencies = [
        # 核心Web框架
        ("Flask", "flask"),
        ("Flask-SocketIO", "flask_socketio"),
        ("Flask-CORS", "flask_cors"),
        ("Werkzeug", "werkzeug"),
        
        # HTTP和环境配置
        ("Requests", "requests"),
        ("Python-dotenv", "dotenv"),
        
        # 实时通信
        ("WebSockets", "websockets"),
        
        # 音频处理（可选）
        ("Pydub", "pydub"),
        ("NumPy", "numpy"),
        
        # 其他工具
        ("JSON", "json"),
        ("OS", "os"),
        ("Threading", "threading"),
    ]
    
    success_count = 0
    total_count = len(dependencies)
    
    for name, module in dependencies:
        try:
            __import__(module)
            print(f"✅ {name} - 已安装")
            success_count += 1
        except ImportError as e:
            print(f"❌ {name} - 未安装 ({e})")
    
    print("=" * 50)
    print(f"📊 依赖检查结果: {success_count}/{total_count} 已安装")
    
    if success_count == total_count:
        print("🎉 所有依赖都已正确安装！")
        return True
    else:
        print("⚠️  有部分依赖未安装，但核心功能应该仍可正常使用")
        return False

def test_flask_socketio():
    print("\n🧪 测试Flask-SocketIO功能...")
    try:
        from flask import Flask
        from flask_socketio import SocketIO, emit
        
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test'
        socketio = SocketIO(app, cors_allowed_origins="*")
        
        print("✅ Flask-SocketIO基础功能正常")
        return True
    except Exception as e:
        print(f"❌ Flask-SocketIO测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 AI角色扮演网站依赖检查工具")
    print("📍 Python版本:", sys.version)
    
    deps_ok = check_dependencies()
    socketio_ok = test_flask_socketio()
    
    if deps_ok and socketio_ok:
        print("\n🎯 依赖检查通过！您可以启动应用了。")
        sys.exit(0)
    else:
        print("\n⚠️  发现一些问题，但基础功能应该可用。")
        sys.exit(1)