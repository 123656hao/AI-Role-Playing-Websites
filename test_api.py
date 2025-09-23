#!/usr/bin/env python3
"""
测试豆包API连接
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_api():
    print("🔍 测试豆包API连接...")
    
    # 从环境变量获取配置
    api_key = os.getenv('ARK_API_KEY') or os.getenv('OPENAI_API_KEY')
    api_base = os.getenv('OPENAI_API_BASE', 'https://ark.cn-beijing.volces.com/api/v3')
    model = os.getenv('OPENAI_MODEL', 'doubao-seed-1-6-250615')
    
    print(f"API Key: {api_key[:10]}...{api_key[-10:] if api_key else 'None'}")
    print(f"API Base: {api_base}")
    print(f"Model: {model}")
    print()
    
    if not api_key:
        print("❌ 未找到API密钥，请检查环境变量配置")
        return False
    
    try:
        # 初始化客户端
        client = OpenAI(
            api_key=api_key,
            base_url=api_base
        )
        
        print("📤 发送测试请求...")
        
        # 发送测试请求
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": "你好，请简单介绍一下自己。"
                }
            ],
            max_tokens=100
        )
        
        print("✅ API测试成功!")
        print(f"回复: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False

if __name__ == "__main__":
    test_api()