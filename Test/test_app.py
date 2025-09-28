#!/usr/bin/env python3
"""
测试应用启动
"""

print("开始测试应用启动...")

try:
    print("1. 导入基础模块...")
    import os
    from dotenv import load_dotenv
    from flask import Flask
    from flask_socketio import SocketIO
    
    print("2. 加载环境变量...")
    load_dotenv()
    
    print("3. 创建Flask应用...")
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'test-secret')
    
    print("4. 创建SocketIO...")
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    print("5. 导入服务...")
    from services.ai_service import AIRoleplayService
    from services.character_service import CharacterService
    from services.baidu_voice_service import BaiduVoiceService
    from services.baidu_tts_service import BaiduTTSService
    
    print("6. 初始化服务...")
    ai_service = AIRoleplayService()
    character_service = CharacterService()
    voice_service = BaiduVoiceService()
    tts_service = BaiduTTSService()
    
    print("7. 定义路由...")
    @app.route('/')
    def index():
        return "Hello World!"
    
    print("8. 启动应用...")
    print("🚀 测试应用启动成功！")
    print("📱 访问地址: http://localhost:5000")
    
    # 启动应用
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()