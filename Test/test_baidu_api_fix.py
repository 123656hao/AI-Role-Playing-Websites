#!/usr/bin/env python3
"""
测试修复后的百度语音识别API
"""

import os
import logging
from dotenv import load_dotenv
from services.baidu_voice_service import BaiduVoiceService
from werkzeug.datastructures import FileStorage
import io

# 加载环境变量
load_dotenv()

# 配置详细日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_baidu_api():
    """测试百度API"""
    print("🧪 测试修复后的百度语音识别API")
    print("=" * 50)
    
    # 创建语音服务实例
    service = BaiduVoiceService()
    
    # 检查配置
    print("📋 检查API配置:")
    print(f"  API Key: {service.api_key[:10]}..." if service.api_key else "  API Key: 未设置")
    print(f"  Secret Key: {service.secret_key[:10]}..." if service.secret_key else "  Secret Key: 未设置")
    print(f"  配置状态: {'✅ 已配置' if service.is_configured else '❌ 未配置'}")
    
    if not service.is_configured:
        print("❌ API密钥未配置，请检查.env文件")
        return
    
    # 测试访问令牌
    print("\n🔑 测试访问令牌:")
    token = service._get_access_token()
    if token:
        print(f"  访问令牌: {token[:20]}...")
        print("  ✅ 访问令牌获取成功")
    else:
        print("  ❌ 访问令牌获取失败")
        return
    
    # 读取测试文件
    print("\n📁 读取测试音频文件:")
    try:
        with open('test_standard_16k.wav', 'rb') as f:
            file_data = f.read()
        
        print(f"  文件大小: {len(file_data)} 字节")
        print("  ✅ 测试文件读取成功")
        
        # 创建FileStorage对象
        file_obj = FileStorage(
            stream=io.BytesIO(file_data),
            filename='test_standard_16k.wav',
            content_type='audio/wav'
        )
        
        # 测试语音识别
        print("\n🎤 开始语音识别测试:")
        result = service.speech_to_text(file_obj)
        
        print(f"\n📊 识别结果:")
        print(f"  结果: {result}")
        
        if result and not result.startswith('语音识别') and not result.startswith('音频'):
            print("  ✅ 语音识别成功")
        else:
            print("  ❌ 语音识别失败")
            
    except FileNotFoundError:
        print("  ❌ 测试文件不存在，请先运行 python test_audio_format.py 创建测试文件")
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")

if __name__ == '__main__':
    test_baidu_api()