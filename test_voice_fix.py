#!/usr/bin/env python3
"""
测试语音修复 - 验证虚拟人物语音回答功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.character_service import CharacterService
from services.ai_service import AIRoleplayService
from services.baidu_tts_service import BaiduTTSService

def test_character_voice_response():
    """测试角色语音回答功能"""
    print("=== 测试角色语音回答功能 ===")
    
    try:
        # 初始化服务
        character_service = CharacterService()
        ai_service = AIRoleplayService()
        tts_service = BaiduTTSService()
        
        # 获取一个测试角色
        characters = character_service.get_all_characters()
        if not characters:
            print("❌ 没有找到角色数据")
            return False
        
        test_character = characters[0]  # 使用第一个角色
        print(f"✅ 使用测试角色: {test_character['name']}")
        
        # 测试AI回答
        test_message = "你好，请介绍一下你自己"
        print(f"📝 测试消息: {test_message}")
        
        ai_response = ai_service.generate_response(test_character, test_message, "test_session")
        if ai_response:
            print(f"🤖 AI回答: {ai_response}")
        else:
            print("❌ AI回答生成失败")
            return False
        
        # 测试语音合成
        print("🔊 测试语音合成...")
        tts_result = tts_service.text_to_speech(ai_response, test_character)
        
        if tts_result:
            if isinstance(tts_result, dict):
                if tts_result.get('success'):
                    print(f"✅ 语音合成成功: {tts_result.get('audio_url')}")
                    return True
                else:
                    print(f"❌ 语音合成失败: {tts_result.get('error')}")
                    return False
            else:
                print(f"✅ 语音合成成功: {tts_result}")
                return True
        else:
            print("❌ 语音合成失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")
        return False

def test_voice_params():
    """测试不同角色的语音参数"""
    print("\n=== 测试角色语音参数 ===")
    
    try:
        character_service = CharacterService()
        tts_service = BaiduTTSService()
        
        characters = character_service.get_all_characters()
        
        for character in characters[:3]:  # 测试前3个角色
            voice_params = tts_service._get_voice_params(character)
            print(f"角色: {character['name']}")
            print(f"  语音参数: {voice_params}")
            print(f"  发音人: {voice_params['per']} ({'男声' if voice_params['per'] == 1 else '女声' if voice_params['per'] == 0 else '情感合成'})")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ 测试语音参数时出现异常: {e}")
        return False

if __name__ == "__main__":
    print("开始测试语音修复功能...\n")
    
    # 测试角色语音回答
    test1_result = test_character_voice_response()
    
    # 测试语音参数
    test2_result = test_voice_params()
    
    print("\n=== 测试结果 ===")
    print(f"角色语音回答测试: {'✅ 通过' if test1_result else '❌ 失败'}")
    print(f"语音参数测试: {'✅ 通过' if test2_result else '❌ 失败'}")
    
    if test1_result and test2_result:
        print("\n🎉 所有测试通过！语音修复功能正常工作。")
    else:
        print("\n⚠️ 部分测试失败，请检查配置和服务状态。")