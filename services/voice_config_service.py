"""
语音配置服务模块 - 管理语音大模型配置
"""

import uuid
import json
import os
from typing import Dict, Any, Optional
from .character_service import CharacterService

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("警告: pyaudio未安装，音频功能将受限")


class VoiceConfigService:
    def __init__(self, config_file: str = "config/voice_settings.json"):
        self.character_service = CharacterService()
        self.config_file = config_file
        self.settings = self._load_settings()
        
        # 从配置文件加载设置
        api_config = self.settings.get("api_config", {})
        
        # 基础WebSocket连接配置
        self.ws_connect_config = {
            "base_url": api_config.get("base_url", "wss://openspeech.bytedance.com/api/v3/realtime/dialogue"),
            "headers": {
                "X-Api-App-ID": api_config.get("app_id", "2440934313"),
                "X-Api-Access-Key": api_config.get("access_key", "snJDH6bnvjspmGT-zSyGUceWVs7O9xNK"),
                "X-Api-Resource-Id": api_config.get("resource_id", "volc.speech.dialog"),
                "X-Api-App-Key": api_config.get("app_key", "PlgvMymc7f3tQnJ6"),
                "X-Api-Connect-Id": str(uuid.uuid4()),
            }
        }
        
        # 音频配置
        audio_settings = self.settings.get("audio_settings", {})
        input_settings = audio_settings.get("input", {})
        output_settings = audio_settings.get("output", {})
        
        # 音频输入配置
        self.input_audio_config = {
            "chunk": input_settings.get("chunk", 3200),
            "format": input_settings.get("format", "pcm"),
            "channels": input_settings.get("channels", 1),
            "sample_rate": input_settings.get("sample_rate", 16000),
            "bit_size": pyaudio.paInt16 if PYAUDIO_AVAILABLE else 16
        }
        
        # 音频输出配置
        self.output_audio_config = {
            "chunk": output_settings.get("chunk", 3200),
            "format": output_settings.get("format", "pcm"),
            "channels": output_settings.get("channels", 1),
            "sample_rate": output_settings.get("sample_rate", 24000),
            "bit_size": pyaudio.paFloat32 if PYAUDIO_AVAILABLE else 32
        }
        
        # 语音角色映射
        self.voice_speakers = self.settings.get("voice_speakers", {
            "male": "zh_male_yunzhou_jupiter_bigtts",
            "female": "zh_female_aojiaonvyou_tob",
            "custom": "S_XXXXXX"
        })
    
    def _load_settings(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not os.path.exists(self.config_file):
            print(f"配置文件 {self.config_file} 不存在，使用默认配置")
            return {}
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return {}
    
    def get_session_config(self, character_id: str, voice_type: str = "female") -> Dict[str, Any]:
        """
        根据角色ID生成会话配置
        
        Args:
            character_id: 角色ID
            voice_type: 语音类型 (male/female/custom)
        
        Returns:
            完整的会话配置
        """
        character = self.character_service.get_character_by_id(character_id)
        if not character:
            raise ValueError(f"角色 {character_id} 不存在")
        
        # 构建系统角色描述
        system_role = self._build_system_role(character)
        speaking_style = self._build_speaking_style(character)
        character_manifest = self._build_character_manifest(character)
        
        # 选择语音
        speaker = self.voice_speakers.get(voice_type, self.voice_speakers["female"])
        
        start_session_req = {
            "asr": {
                "extra": {
                    "end_smooth_window_ms": 1500,
                }
            },
            "tts": {
                "speaker": speaker,
                "audio_config": {
                    "channel": 1,
                    "format": "pcm",
                    "sample_rate": 24000
                }
            },
            "dialog": {
                "bot_name": character["name"],
                "system_role": system_role,
                "speaking_style": speaking_style,
                "location": {
                    "city": "北京"
                },
                "extra": {
                    "strict_audit": False,
                    "audit_response": "支持客户自定义安全审核回复话术。",
                    "recv_timeout": 10,
                    "input_mod": "audio"
                }
            }
        }
        
        # 如果是自定义音色，添加character_manifest
        if voice_type == "custom" and character_manifest:
            start_session_req["dialog"]["character_manifest"] = character_manifest
        
        return start_session_req
    
    def _build_system_role(self, character: Dict[str, Any]) -> str:
        """构建系统角色描述"""
        personality = character.get("personality", "")
        background = character.get("background", "")
        
        system_role = f"你是{character['name']}。"
        
        if background:
            system_role += f"背景：{background} "
        
        if personality:
            system_role += f"性格特点：{personality}"
        
        return system_role
    
    def _build_speaking_style(self, character: Dict[str, Any]) -> str:
        """构建说话风格"""
        character_id = character.get("id", "")
        
        # 首先检查配置文件中的角色语音映射
        character_voice_mapping = self.settings.get("character_voice_mapping", {})
        if character_id in character_voice_mapping:
            mapped_style = character_voice_mapping[character_id].get("speaking_style")
            if mapped_style:
                return mapped_style
        
        # 其次使用角色自带的说话风格
        speaking_style = character.get("speaking_style", "")
        if speaking_style:
            return speaking_style
        
        # 最后根据角色类别设置默认说话风格
        category = character.get("category", "")
        if category == "philosophy":
            speaking_style = "语言深刻富有哲理，喜欢通过提问引导思考，语调沉稳。"
        elif category == "science":
            speaking_style = "表达严谨准确，善于用简单的比喻解释复杂概念，语调自信。"
        elif category == "literature":
            speaking_style = "语言优美富有诗意，表达生动形象，语调富有感情。"
        elif category == "education":
            speaking_style = "表达清晰耐心，循循善诱，语调温和亲切。"
        else:
            speaking_style = "语言自然流畅，表达真诚友善，语调温和。"
        
        return speaking_style
    
    def _build_character_manifest(self, character: Dict[str, Any]) -> Optional[str]:
        """构建角色清单（用于自定义音色）"""
        # 这里可以根据角色信息构建详细的角色清单
        # 目前返回None，如果需要自定义音色可以扩展
        return None
    
    def get_ws_config(self) -> Dict[str, Any]:
        """获取WebSocket连接配置"""
        # 每次获取时生成新的连接ID
        config = self.ws_connect_config.copy()
        config["headers"]["X-Api-Connect-Id"] = str(uuid.uuid4())
        return config
    
    def get_input_audio_config(self) -> Dict[str, Any]:
        """获取音频输入配置"""
        return self.input_audio_config.copy()
    
    def get_output_audio_config(self) -> Dict[str, Any]:
        """获取音频输出配置"""
        return self.output_audio_config.copy()
    
    def get_available_voices(self) -> Dict[str, str]:
        """获取可用的语音类型"""
        return self.voice_speakers.copy()
    
    def update_voice_speaker(self, voice_type: str, speaker_id: str):
        """更新语音音色"""
        if voice_type in self.voice_speakers:
            self.voice_speakers[voice_type] = speaker_id
    
    def create_character_voice_config(self, character_id: str, 
                                    voice_type: str = "female",
                                    custom_speaking_style: str = None) -> Dict[str, Any]:
        """
        为特定角色创建完整的语音配置
        
        Args:
            character_id: 角色ID
            voice_type: 语音类型
            custom_speaking_style: 自定义说话风格
        
        Returns:
            包含所有配置的字典
        """
        character = self.character_service.get_character_by_id(character_id)
        if not character:
            raise ValueError(f"角色 {character_id} 不存在")
        
        session_config = self.get_session_config(character_id, voice_type)
        
        # 如果提供了自定义说话风格，覆盖默认的
        if custom_speaking_style:
            session_config["dialog"]["speaking_style"] = custom_speaking_style
        
        return {
            "ws_config": self.get_ws_config(),
            "session_config": session_config,
            "input_audio_config": self.get_input_audio_config(),
            "output_audio_config": self.get_output_audio_config(),
            "character_info": character
        }