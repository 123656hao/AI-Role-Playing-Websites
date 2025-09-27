"""
语音聊天示例 - 展示如何使用语音配置服务
"""

import asyncio
import json
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.voice_config_service import VoiceConfigService


async def main():
    # 初始化语音配置服务
    voice_service = VoiceConfigService()
    
    # 获取所有可用角色
    characters = voice_service.character_service.get_all_characters()
    print("可用角色:")
    for char in characters:
        print(f"- {char['id']}: {char['name']} ({char['category']})")
    
    print("\n" + "="*50)
    
    # 为苏格拉底创建语音配置
    print("为苏格拉底创建语音配置:")
    socrates_config = voice_service.create_character_voice_config(
        character_id="socrates",
        voice_type="male"
    )
    
    print("WebSocket配置:")
    print(json.dumps(socrates_config["ws_config"], indent=2, ensure_ascii=False))
    
    print("\n会话配置:")
    print(json.dumps(socrates_config["session_config"], indent=2, ensure_ascii=False))
    
    print("\n" + "="*50)
    
    # 为哈利·波特创建语音配置（使用自定义说话风格）
    print("为哈利·波特创建语音配置:")
    harry_config = voice_service.create_character_voice_config(
        character_id="harry_potter",
        voice_type="male",
        custom_speaking_style="充满活力和好奇心，经常使用魔法世界的术语，语调年轻而热情。"
    )
    
    print("会话配置:")
    print(json.dumps(harry_config["session_config"], indent=2, ensure_ascii=False))
    
    print("\n" + "="*50)
    
    # 为孔子创建语音配置
    print("为孔子创建语音配置:")
    confucius_config = voice_service.create_character_voice_config(
        character_id="confucius",
        voice_type="male"
    )
    
    print("会话配置:")
    print(json.dumps(confucius_config["session_config"], indent=2, ensure_ascii=False))
    
    print("\n音频配置:")
    print("输入音频配置:", confucius_config["input_audio_config"])
    print("输出音频配置:", confucius_config["output_audio_config"])


if __name__ == "__main__":
    asyncio.run(main())