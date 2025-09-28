#!/usr/bin/env python3
"""
启动实时语音对话应用
增强版语音聊天功能
"""

import os
import sys
import webbrowser
import time
from threading import Timer

def check_dependencies():
    """检查依赖包"""
    required_packages = [
        'flask',
        'flask-socketio',
        'requests',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少以下依赖包:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_env_file():
    """检查环境配置文件"""
    if not os.path.exists('../.env'):
        print("⚠️ 未找到 .env 配置文件")
        print("请创建 .env 文件并配置以下参数:")
        print("""
# Flask应用配置
SECRET_KEY=your-secret-key-here

# AI服务配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://ark.cn-beijing.volces.com/api/v3
OPENAI_MODEL=doubao-seed-1-6-250615

# 百度语音API配置
BAIDU_API_KEY=your_baidu_api_key_here
BAIDU_SECRET_KEY=your_baidu_secret_key_here
        """)
        return False
    
    return True

def open_browser():
    """延迟打开浏览器"""
    time.sleep(2)  # 等待服务器启动
    try:
        webbrowser.open('http://localhost:5000/realtime')
        print("🌐 浏览器已打开实时语音对话页面")
    except Exception as e:
        print(f"⚠️ 无法自动打开浏览器: {e}")
        print("请手动访问: http://localhost:5000/realtime")

def main():
    """主函数"""
    print("🚀 启动实时语音对话应用")
    print("=" * 50)
    
    # 检查依赖
    print("🔍 检查依赖包...")
    if not check_dependencies():
        sys.exit(1)
    print("✅ 依赖包检查完成")
    
    # 检查配置文件
    print("🔍 检查配置文件...")
    if not check_env_file():
        print("💡 配置完成后请重新运行此脚本")
        sys.exit(1)
    print("✅ 配置文件检查完成")
    
    # 导入应用
    try:
        from voice_app import app, socketio
        print("✅ 应用模块加载成功")
    except ImportError as e:
        print(f"❌ 应用模块加载失败: {e}")
        sys.exit(1)
    
    # 设置浏览器自动打开
    timer = Timer(2.0, open_browser)
    timer.start()
    
    print("\n🎤 实时语音对话功能特性:")
    print("   ✨ 连续语音识别")
    print("   🎯 智能静音检测")
    print("   🔄 自动对话循环")
    print("   🎨 实时音频可视化")
    print("   ⌨️ 空格键快捷操作")
    print("   🎭 多角色语音合成")
    
    print("\n🌐 服务地址:")
    print("   - 实时语音对话: http://localhost:5000/realtime")
    print("   - 标准语音聊天: http://localhost:5000/")
    
    print("\n💡 使用提示:")
    print("   1. 选择AI角色")
    print("   2. 点击麦克风按钮开始对话")
    print("   3. 开启连续模式进行自然对话")
    print("   4. 使用空格键快速开始/停止录音")
    
    print("\n🔧 故障排除:")
    print("   - 确保麦克风权限已授权")
    print("   - 检查网络连接")
    print("   - 验证API密钥配置")
    
    print("\n" + "=" * 50)
    print("🎉 启动Web服务器...")
    
    try:
        # 启动应用
        socketio.run(
            app,
            host='0.0.0.0',
            port=5000,
            debug=False,
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()