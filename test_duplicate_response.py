#!/usr/bin/env python3
"""
测试重复回复问题修复
"""

import os
import sys
import time
import requests
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_chat_api():
    """测试聊天API是否只返回一个回复"""
    print("🔍 测试聊天API...")
    
    base_url = "http://localhost:5000"
    
    try:
        # 测试文字聊天
        chat_data = {
            "message": "你好，请简单介绍一下自己",
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
                print(f"   - AI回复: {result['response'][:100]}...")
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

def test_websocket_events():
    """测试WebSocket事件是否正确"""
    print("\n🔍 测试WebSocket事件配置...")
    
    # 检查主页面是否正确加载
    base_url = "http://localhost:5000"
    
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            content = response.text
            
            # 检查是否包含正确的事件监听器
            if "socket.on('chat_response'" in content:
                print("✅ chat_response 事件监听器存在")
            else:
                print("❌ chat_response 事件监听器缺失")
                return False
            
            # 检查是否注释掉了重复的事件监听器
            if "// socket.on('ai_response'" in content or "socket.on('ai_response'" not in content:
                print("✅ ai_response 重复事件监听器已处理")
            else:
                print("❌ ai_response 重复事件监听器仍存在")
                return False
            
            # 检查是否注释掉了tts_result事件监听器
            if "// socket.on('tts_result'" in content or "socket.on('tts_result'" not in content:
                print("✅ tts_result 重复事件监听器已处理")
            else:
                print("❌ tts_result 重复事件监听器仍存在")
                return False
            
            return True
        else:
            print(f"❌ 主页面访问失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ WebSocket事件测试失败: {e}")
        return False

def test_character_loading():
    """测试角色加载"""
    print("\n🔍 测试角色加载...")
    
    base_url = "http://localhost:5000"
    
    try:
        response = requests.get(f"{base_url}/api/characters", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                characters = data['characters']
                print(f"✅ 角色加载成功，共 {len(characters)} 个角色")
                
                # 显示前几个角色
                for i, char in enumerate(characters[:3]):
                    print(f"   {i+1}. {char['name']} - {char.get('category', '未分类')}")
                
                return True
            else:
                print(f"❌ 角色加载失败: {data.get('error')}")
                return False
        else:
            print(f"❌ 角色API访问失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 角色加载测试失败: {e}")
        return False

def check_backend_events():
    """检查后端事件发送是否统一"""
    print("\n🔍 检查后端事件发送...")
    
    try:
        # 读取voice_app.py文件
        with open('voice_app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否统一使用chat_response事件
        chat_response_count = content.count("emit('chat_response'")
        ai_response_count = content.count("emit('ai_response'")
        tts_result_count = content.count("emit('tts_result'")
        
        print(f"   - chat_response 事件发送次数: {chat_response_count}")
        print(f"   - ai_response 事件发送次数: {ai_response_count}")
        print(f"   - tts_result 事件发送次数: {tts_result_count}")
        
        if chat_response_count >= 2 and ai_response_count == 0 and tts_result_count == 0:
            print("✅ 后端事件发送已统一使用 chat_response")
            return True
        else:
            print("❌ 后端事件发送未完全统一")
            return False
            
    except Exception as e:
        print(f"❌ 后端事件检查失败: {e}")
        return False

def provide_usage_tips():
    """提供使用建议"""
    print("\n" + "=" * 50)
    print("💡 使用建议")
    print("=" * 50)
    
    print("\n🎯 修复内容:")
    print("1. 统一了WebSocket事件处理，避免重复显示AI回复")
    print("2. chat_message 和 voice_message 都使用 chat_response 事件")
    print("3. 移除了重复的 ai_response 和 tts_result 事件监听器")
    print("4. 确保每个用户消息只产生一个AI回复")
    
    print("\n🔧 技术细节:")
    print("- 前端只监听 chat_response 事件")
    print("- 后端统一发送 chat_response 事件")
    print("- 音频URL通过 chat_response 事件一起发送")
    print("- 避免了事件监听器重复处理")
    
    print("\n🌐 测试方法:")
    print("1. 访问 http://localhost:5000")
    print("2. 选择任意AI角色开始对话")
    print("3. 发送文字消息，观察是否只有一个AI回复")
    print("4. 使用语音输入，观察是否只有一个AI回复")
    print("5. 检查是否有语音播放功能")

def main():
    """主测试函数"""
    print("🧪 重复回复问题修复测试")
    print("=" * 50)
    
    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(2)
    
    # 测试各项功能
    tests = [
        ("后端事件发送统一性", check_backend_events),
        ("WebSocket事件配置", test_websocket_events),
        ("角色加载", test_character_loading),
        ("聊天API", test_chat_api)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed_tests += 1
        else:
            print(f"❌ {test_name} 测试失败")
    
    # 显示测试结果
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed_tests}/{total_tests} 通过")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！重复回复问题已修复")
        print("\n✨ 现在与虚拟人物对话时应该只会看到一个回复")
    else:
        print("⚠️ 部分测试失败，可能仍有重复回复问题")
    
    provide_usage_tips()

if __name__ == '__main__':
    main()