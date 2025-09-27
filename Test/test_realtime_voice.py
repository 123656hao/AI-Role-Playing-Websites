#!/usr/bin/env python3
"""
实时语音功能测试脚本
"""

import os
import sys
import time
import requests
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_basic_services():
    """测试基础服务"""
    print("🔍 测试基础服务...")
    
    base_url = "http://localhost:5000"
    
    try:
        # 测试健康检查
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ 健康检查通过")
            print(f"   - 语音识别: {'✅' if health_data['services']['voice_recognition'] else '❌'}")
            print(f"   - 语音合成: {'✅' if health_data['services']['text_to_speech'] else '❌'}")
            print(f"   - AI服务: {'✅' if health_data['services']['ai_service'] else '❌'}")
        else:
            print("❌ 健康检查失败")
            return False
        
        # 测试角色API
        response = requests.get(f"{base_url}/api/characters", timeout=5)
        if response.status_code == 200:
            characters_data = response.json()
            if characters_data.get('success'):
                print(f"✅ 角色服务正常，共 {len(characters_data['characters'])} 个角色")
            else:
                print("❌ 角色服务异常")
                return False
        else:
            print("❌ 角色API访问失败")
            return False
        
        # 测试语音服务状态
        response = requests.get(f"{base_url}/api/voice/status", timeout=5)
        if response.status_code == 200:
            voice_data = response.json()
            if voice_data.get('success'):
                print("✅ 语音服务状态正常")
            else:
                print("❌ 语音服务状态异常")
                return False
        else:
            print("❌ 语音服务状态API访问失败")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保应用已启动")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_chat_api():
    """测试聊天API"""
    print("\n🔍 测试聊天API...")
    
    base_url = "http://localhost:5000"
    
    try:
        # 测试文字聊天
        chat_data = {
            "message": "你好，这是一个测试消息",
            "character_id": "assistant"
        }
        
        response = requests.post(
            f"{base_url}/api/chat",
            json=chat_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 聊天API测试成功")
                print(f"   - AI回复: {result['response'][:50]}...")
                print(f"   - 角色: {result['character']['name']}")
                if result.get('audio_url'):
                    print("   - 语音合成: ✅")
                else:
                    print("   - 语音合成: ❌")
                return True
            else:
                print(f"❌ 聊天API返回错误: {result.get('error')}")
                return False
        else:
            print(f"❌ 聊天API请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 聊天API测试失败: {e}")
        return False

def test_realtime_pages():
    """测试实时语音页面"""
    print("\n🔍 测试实时语音页面...")
    
    base_url = "http://localhost:5000"
    
    try:
        # 测试实时语音页面
        response = requests.get(f"{base_url}/realtime", timeout=5)
        if response.status_code == 200:
            print("✅ 实时语音页面可访问")
        else:
            print(f"❌ 实时语音页面访问失败: {response.status_code}")
            return False
        
        # 测试标准语音页面
        response = requests.get(f"{base_url}/voice", timeout=5)
        if response.status_code == 200:
            print("✅ 标准语音页面可访问")
        else:
            print(f"❌ 标准语音页面访问失败: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 页面测试失败: {e}")
        return False

def check_environment():
    """检查环境配置"""
    print("🔍 检查环境配置...")
    
    required_vars = [
        'BAIDU_API_KEY',
        'BAIDU_SECRET_KEY',
        'OPENAI_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 缺少环境变量: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ 环境变量配置完整")
        return True

def main():
    """主测试函数"""
    print("🧪 实时语音功能测试")
    print("=" * 50)
    
    # 检查环境配置
    if not check_environment():
        print("\n💡 请在 .env 文件中配置必要的API密钥")
        return
    
    # 等待服务启动
    print("\n⏳ 等待服务启动...")
    time.sleep(2)
    
    # 测试基础服务
    if not test_basic_services():
        print("\n❌ 基础服务测试失败")
        print("💡 请确保 voice_app.py 已启动并正常运行")
        return
    
    # 测试聊天API
    if not test_chat_api():
        print("\n❌ 聊天API测试失败")
        return
    
    # 测试页面访问
    if not test_realtime_pages():
        print("\n❌ 页面访问测试失败")
        return
    
    print("\n" + "=" * 50)
    print("🎉 所有测试通过！")
    print("\n📱 可以访问以下页面:")
    print("   - 实时语音对话: http://localhost:5000/realtime")
    print("   - 标准语音聊天: http://localhost:5000/voice")
    print("   - 主页: http://localhost:5000/")
    
    print("\n💡 使用建议:")
    print("   1. 使用Chrome或Edge浏览器获得最佳体验")
    print("   2. 确保麦克风权限已授权")
    print("   3. 在安静环境中进行语音测试")
    print("   4. 开启连续模式体验自然对话")

if __name__ == '__main__':
    main()