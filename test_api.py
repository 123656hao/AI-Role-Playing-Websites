#!/usr/bin/env python3
"""
测试API端点
"""

import requests
import json

def test_characters_api():
    """测试角色API"""
    try:
        # 测试不同端口
        ports = [5000, 5001, 5002]
        
        for port in ports:
            url = f"http://localhost:{port}/api/characters"
            print(f"测试端口 {port}: {url}")
            
            try:
                response = requests.get(url, timeout=5)
                print(f"  状态码: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"  成功! 角色数量: {len(data.get('characters', []))}")
                    print(f"  角色列表: {[c['name'] for c in data.get('characters', [])]}")
                    return port
                else:
                    print(f"  失败: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                print(f"  连接失败: 端口 {port} 无服务")
            except Exception as e:
                print(f"  错误: {e}")
        
        print("所有端口测试完毕，未找到可用的API服务")
        return None
        
    except Exception as e:
        print(f"测试失败: {e}")
        return None

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 测试角色API端点")
    print("=" * 50)
    
    working_port = test_characters_api()
    
    if working_port:
        print(f"\n✅ 找到工作端口: {working_port}")
    else:
        print(f"\n❌ 未找到工作的API服务")
        print("请确保roleplay_app.py正在运行")