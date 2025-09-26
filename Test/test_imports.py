#!/usr/bin/env python3
"""
测试导入是否正常
"""

print("开始测试导入...")

try:
    print("1. 测试基础库导入...")
    import os
    import json
    import logging
    from datetime import datetime
    from flask import Flask
    from flask_socketio import SocketIO
    from werkzeug.utils import secure_filename
    import uuid
    from dotenv import load_dotenv
    print("✅ 基础库导入成功")
    
    print("2. 加载环境变量...")
    load_dotenv()
    print("✅ 环境变量加载成功")
    
    print("3. 测试服务导入...")
    
    print("   - 导入AI服务...")
    from services.ai_service import AIRoleplayService
    print("   ✅ AI服务导入成功")
    
    print("   - 导入角色服务...")
    from services.character_service import CharacterService
    print("   ✅ 角色服务导入成功")
    
    print("   - 导入语音识别服务...")
    from services.baidu_voice_service import BaiduVoiceService
    print("   ✅ 语音识别服务导入成功")
    
    print("   - 导入语音合成服务...")
    from services.baidu_tts_service import BaiduTTSService
    print("   ✅ 语音合成服务导入成功")
    
    print("4. 测试服务初始化...")
    
    print("   - 初始化AI服务...")
    ai_service = AIRoleplayService()
    print("   ✅ AI服务初始化成功")
    
    print("   - 初始化角色服务...")
    character_service = CharacterService()
    print("   ✅ 角色服务初始化成功")
    
    print("   - 初始化语音识别服务...")
    voice_service = BaiduVoiceService()
    print("   ✅ 语音识别服务初始化成功")
    
    print("   - 初始化语音合成服务...")
    tts_service = BaiduTTSService()
    print("   ✅ 语音合成服务初始化成功")
    
    print("\n🎉 所有导入和初始化测试通过！")
    
except Exception as e:
    print(f"\n❌ 导入测试失败: {e}")
    import traceback
    traceback.print_exc()