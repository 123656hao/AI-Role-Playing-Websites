#!/usr/bin/env python3
"""
语音识别功能测试脚本
比较标准语音聊天和实时语音聊天的语音识别效果
"""

import os
import sys
import time
import requests
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_voice_upload_api():
    """测试语音上传API"""
    print("🔍 测试语音上传API...")
    
    base_url = "http://localhost:5000"
    
    try:
        # 检查API是否可访问
        response = requests.get(f"{base_url}/api/voice/status", timeout=5)
        if response.status_code == 200:
            voice_data = response.json()
            if voice_data.get('success'):
                print("✅ 语音服务API可访问")
                status = voice_data['status']
                print(f"   - 语音识别配置: {'✅' if status['voice_recognition'] else '❌'}")
                print(f"   - 语音合成配置: {'✅' if status['text_to_speech'] else '❌'}")
                return True
            else:
                print("❌ 语音服务API异常")
                return False
        else:
            print(f"❌ 语音服务API访问失败: {response.status_code}")
            return False
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保应用已启动")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_pages_accessibility():
    """测试页面可访问性"""
    print("\n🔍 测试页面可访问性...")
    
    base_url = "http://localhost:5000"
    pages = {
        "主页": "/",
        "标准语音聊天": "/voice", 
        "实时语音对话": "/realtime"
    }
    
    all_accessible = True
    
    for name, path in pages.items():
        try:
            response = requests.get(f"{base_url}{path}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: {base_url}{path}")
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
                all_accessible = False
        except Exception as e:
            print(f"❌ {name}: 访问失败 - {e}")
            all_accessible = False
    
    return all_accessible

def test_audio_converter_script():
    """测试音频转换器脚本是否可访问"""
    print("\n🔍 测试音频转换器脚本...")
    
    base_url = "http://localhost:5000"
    
    try:
        response = requests.get(f"{base_url}/static/js/audio_converter.js", timeout=5)
        if response.status_code == 200:
            print("✅ 音频转换器脚本可访问")
            # 检查脚本内容
            content = response.text
            if 'AudioConverter' in content and 'convertWebMToWAV' in content:
                print("✅ 音频转换器脚本内容正确")
                return True
            else:
                print("❌ 音频转换器脚本内容不完整")
                return False
        else:
            print(f"❌ 音频转换器脚本访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_character_api():
    """测试角色API"""
    print("\n🔍 测试角色API...")
    
    base_url = "http://localhost:5000"
    
    try:
        response = requests.get(f"{base_url}/api/characters", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                characters = data['characters']
                print(f"✅ 角色API正常，共 {len(characters)} 个角色")
                
                # 显示角色列表
                for char in characters[:3]:  # 只显示前3个
                    print(f"   - {char['name']}: {char.get('description', '无描述')}")
                
                if len(characters) > 3:
                    print(f"   ... 还有 {len(characters) - 3} 个角色")
                
                return True
            else:
                print(f"❌ 角色API返回错误: {data.get('error')}")
                return False
        else:
            print(f"❌ 角色API访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
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
    configured_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            configured_vars.append(var)
            # 显示部分密钥（隐藏敏感信息）
            masked_value = value[:8] + '...' + value[-4:] if len(value) > 12 else value[:4] + '...'
            print(f"✅ {var}: {masked_value}")
    
    if missing_vars:
        print(f"❌ 缺少环境变量: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ 所有必要的环境变量已配置")
        return True

def provide_troubleshooting_tips():
    """提供故障排除建议"""
    print("\n" + "=" * 50)
    print("🛠️ 故障排除建议")
    print("=" * 50)
    
    print("\n📋 如果语音识别不正确，请检查：")
    print("1. 浏览器麦克风权限是否已授权")
    print("2. 录音环境是否安静")
    print("3. 说话是否清晰响亮")
    print("4. 录音时长是否合适（建议3-8秒）")
    print("5. 网络连接是否稳定")
    
    print("\n🔧 技术检查项目：")
    print("1. 音频转换器脚本是否正确加载")
    print("2. WebM到WAV格式转换是否成功")
    print("3. 百度语音识别API配置是否正确")
    print("4. 服务器日志是否有错误信息")
    
    print("\n🌐 浏览器建议：")
    print("1. 推荐使用Chrome或Edge浏览器")
    print("2. 确保浏览器版本较新")
    print("3. 清除浏览器缓存和Cookie")
    print("4. 尝试使用无痕模式")
    
    print("\n📞 获取更多帮助：")
    print("1. 查看浏览器控制台错误信息")
    print("2. 查看服务器终端日志输出")
    print("3. 运行 python test_realtime_voice.py 进行详细测试")

def main():
    """主测试函数"""
    print("🧪 语音识别功能测试")
    print("=" * 50)
    
    # 检查环境配置
    if not check_environment():
        print("\n💡 请在 .env 文件中配置必要的API密钥")
        return
    
    # 等待服务启动
    print("\n⏳ 等待服务启动...")
    time.sleep(2)
    
    # 测试各项功能
    tests = [
        ("语音上传API", test_voice_upload_api),
        ("页面可访问性", test_pages_accessibility),
        ("音频转换器脚本", test_audio_converter_script),
        ("角色API", test_character_api)
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
        print("🎉 所有测试通过！")
        print("\n✨ 语音识别功能应该正常工作")
        print("💡 如果仍有问题，请检查：")
        print("   - 浏览器控制台是否有JavaScript错误")
        print("   - 麦克风权限是否正确授权")
        print("   - 录音质量是否良好")
    else:
        print("⚠️ 部分测试失败，可能影响语音识别功能")
        provide_troubleshooting_tips()

if __name__ == '__main__':
    main()