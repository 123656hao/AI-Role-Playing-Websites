#!/usr/bin/env python3
"""
测试环境变量加载
"""

import os
from dotenv import load_dotenv

def test_env_loading():
    """测试环境变量加载"""
    print("=" * 50)
    print("🔧 测试环境变量加载")
    print("=" * 50)
    
    # 加载.env文件
    print("1. 加载.env文件...")
    load_dotenv()
    print("✓ load_dotenv() 执行完成")
    
    # 检查关键环境变量
    env_vars = [
        'BAIDU_API_KEY',
        'BAIDU_SECRET_KEY', 
        'OPENAI_API_KEY',
        'ARK_API_KEY',
        'OPENAI_API_BASE',
        'OPENAI_MODEL'
    ]
    
    print("\n2. 检查环境变量:")
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # 只显示前8个字符，保护敏感信息
            masked_value = value[:8] + "..." if len(value) > 8 else value
            print(f"✓ {var}: {masked_value}")
        else:
            print(f"✗ {var}: 未设置")
    
    # 测试AI服务初始化
    print("\n3. 测试AI服务初始化:")
    try:
        from services.ai_service import AIRoleplayService
        ai_service = AIRoleplayService()
        print("✓ AI服务初始化成功")
        
        # 测试简单对话
        test_character = {
            'name': '测试助手',
            'background': '我是一个测试助手',
            'personality': '友善、乐于助人',
            'expertise': '测试'
        }
        
        response = ai_service.generate_response(test_character, "你好", "test_session")
        if response:
            print(f"✓ AI对话测试成功: {response[:50]}...")
        else:
            print("✗ AI对话测试失败: 无响应")
            
    except Exception as e:
        print(f"✗ AI服务初始化失败: {e}")
    
    # 测试百度语音服务
    print("\n4. 测试百度语音服务:")
    try:
        from services.baidu_voice_service import BaiduVoiceService
        voice_service = BaiduVoiceService()
        print("✓ 百度语音识别服务初始化成功")
    except Exception as e:
        print(f"✗ 百度语音识别服务初始化失败: {e}")
    
    try:
        from services.baidu_tts_service import BaiduTTSService
        tts_service = BaiduTTSService()
        print("✓ 百度语音合成服务初始化成功")
    except Exception as e:
        print(f"✗ 百度语音合成服务初始化失败: {e}")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)

if __name__ == "__main__":
    test_env_loading()