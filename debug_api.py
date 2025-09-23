#!/usr/bin/env python3
"""
API调试脚本 - 检查AI服务配置和连接
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

def check_api_config():
    """检查API配置"""
    print("🔍 检查API配置...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    api_base = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
    model = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    print(f"API密钥: {'✅ 已配置' if api_key and api_key != 'your_doubao_api_key_here' else '❌ 未配置或使用默认值'}")
    print(f"API端点: {api_base}")
    print(f"使用模型: {model}")
    
    if not api_key or api_key == 'your_doubao_api_key_here':
        print("\n❌ 错误: API密钥未正确配置")
        print("请编辑 .env 文件，将 OPENAI_API_KEY 设置为你的真实豆包API密钥")
        return False
    
    return True

def test_api_connection():
    """测试API连接"""
    print("\n🌐 测试API连接...")
    
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        api_base = os.getenv('OPENAI_API_BASE')
        model = os.getenv('OPENAI_MODEL')
        
        client = OpenAI(
            api_key=api_key,
            base_url=api_base
        )
        
        print("正在发送测试请求...")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "你好，请简单回复一下"}
            ],
            max_tokens=50
        )
        
        reply = response.choices[0].message.content
        print(f"✅ API连接成功!")
        print(f"测试回复: {reply}")
        return True
        
    except Exception as e:
        print(f"❌ API连接失败: {e}")
        return False

def main():
    print("=" * 50)
    print("🔧 AI角色扮演聊天 - API调试工具")
    print("=" * 50)
    
    # 检查配置
    config_ok = check_api_config()
    
    if config_ok:
        # 测试连接
        connection_ok = test_api_connection()
        
        if connection_ok:
            print("\n🎉 所有检查都通过！AI服务应该可以正常工作。")
        else:
            print("\n⚠️ API连接失败，请检查:")
            print("1. API密钥是否正确")
            print("2. 网络连接是否正常")
            print("3. API端点是否可访问")
    else:
        print("\n📝 配置步骤:")
        print("1. 获取豆包API密钥")
        print("2. 编辑 .env 文件")
        print("3. 将 OPENAI_API_KEY=你的真实API密钥")
        print("4. 重新启动应用")

if __name__ == '__main__':
    main()