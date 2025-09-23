"""
增强语音服务模块 - 支持实时语音交互
包含字节跳动语音API集成和WebSocket实时通信
"""

import os
import json
import tempfile
import requests
import asyncio
import websockets
import base64
import wave
import io
import threading
import time
from typing import Optional, Dict, Any, Callable, List
import logging
from datetime import datetime
from werkzeug.datastructures import FileStorage

# 尝试导入语音相关库
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("⚠️ SpeechRecognition未安装，语音识别功能将被禁用")

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("⚠️ pyttsx3未安装，本地语音合成功能将被禁用")

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("⚠️ PyAudio未安装，实时语音功能将被禁用")

logger = logging.getLogger(__name__)

class EnhancedVoiceService:
    def __init__(self):
        """初始化增强语音服务"""
        self.audio_dir = "static/audio"
        os.makedirs(self.audio_dir, exist_ok=True)
        
        # 加载语音配置
        self.voice_config = self.load_voice_config()
        
        # 初始化语音识别
        self.init_speech_recognition()
        
        # 初始化语音合成
        self.init_text_to_speech()
        
        # 实时语音相关
        self.websocket_connections = {}
        self.audio_sessions = {}
        self.recording_threads = {}
        
        print("🎙️ 增强语音服务初始化完成")
    
    def load_voice_config(self) -> Dict[str, Any]:
        """加载语音配置"""
        try:
            config_path = os.path.join('config', 'voice_settings.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    print("✅ 语音配置加载成功")
                    return config
        except Exception as e:
            logger.error(f"加载语音配置失败: {e}")
        
        print("⚠️ 使用默认语音配置")
        return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认语音配置"""
        return {
            "api_config": {
                "base_url": "wss://openspeech.bytedance.com/api/v3/realtime/dialogue",
                "app_id": "",
                "access_key": "",
                "app_key": ""
            },
            "voice_speakers": {
                "male": "zh_male_yunzhou_jupiter_bigtts",
                "female": "zh_female_aojiaonvyou_tob"
            },
            "audio_settings": {
                "input": {
                    "chunk": 3200,
                    "format": "pcm",
                    "channels": 1,
                    "sample_rate": 16000
                },
                "output": {
                    "chunk": 3200,
                    "format": "pcm", 
                    "channels": 1,
                    "sample_rate": 24000
                }
            }
        }
    
    def init_speech_recognition(self):
        """初始化语音识别"""
        if SPEECH_RECOGNITION_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                if PYAUDIO_AVAILABLE:
                    self.microphone = sr.Microphone()
                    print("🎤 语音识别: ✅ 完全可用")
                else:
                    self.microphone = None
                    print("🎤 语音识别: ⚠️ 部分可用（无实时录音）")
                self.speech_recognition_enabled = True
            except Exception as e:
                print(f"🎤 语音识别初始化失败: {e}")
                self.speech_recognition_enabled = False
        else:
            self.recognizer = None
            self.microphone = None
            self.speech_recognition_enabled = False
            print("🎤 语音识别: ❌ 不可用")
    
    def init_text_to_speech(self):
        """初始化语音合成"""
        if TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 150)
                self.tts_engine.setProperty('volume', 0.8)
                print("🔊 本地语音合成: ✅ 可用")
                self.tts_enabled = True
            except Exception as e:
                print(f"🔊 本地语音合成初始化失败: {e}")
                self.tts_engine = None
                self.tts_enabled = False
        else:
            self.tts_engine = None
            self.tts_enabled = False
            print("🔊 本地语音合成: ❌ 不可用")
    
    def speech_to_text(self, audio_file: FileStorage) -> str:
        """语音转文字"""
        if not self.speech_recognition_enabled:
            raise Exception("语音识别功能不可用")
        
        try:
            # 保存上传的音频文件
            temp_path = os.path.join(tempfile.gettempdir(), f"audio_{int(time.time())}.wav")
            audio_file.save(temp_path)
            
            # 使用语音识别
            with sr.AudioFile(temp_path) as source:
                audio = self.recognizer.record(source)
            
            # 尝试多种识别方式
            text = None
            
            # 1. 尝试使用字节跳动ASR API（如果配置了）
            if self.voice_config.get('api_config', {}).get('access_key'):
                try:
                    text = self.bytedance_speech_to_text(temp_path)
                    print("✅ 使用字节跳动ASR识别成功")
                except Exception as e:
                    print(f"⚠️ 字节跳动ASR识别失败: {e}")
            
            # 2. 备用：使用Google语音识别
            if not text:
                try:
                    text = self.recognizer.recognize_google(audio, language='zh-CN')
                    print("✅ 使用Google语音识别成功")
                except Exception as e:
                    print(f"⚠️ Google语音识别失败: {e}")
            
            # 3. 备用：使用Sphinx离线识别
            if not text:
                try:
                    text = self.recognizer.recognize_sphinx(audio, language='zh-CN')
                    print("✅ 使用Sphinx离线识别成功")
                except Exception as e:
                    print(f"⚠️ Sphinx离线识别失败: {e}")
            
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            if text:
                return text.strip()
            else:
                raise Exception("所有语音识别方式都失败了")
                
        except Exception as e:
            logger.error(f"语音识别失败: {e}")
            raise Exception(f"语音识别失败: {str(e)}")
    
    def bytedance_speech_to_text(self, audio_path: str) -> str:
        """使用字节跳动ASR API进行语音识别"""
        api_config = self.voice_config.get('api_config', {})
        
        if not all([api_config.get('app_id'), api_config.get('access_key'), api_config.get('app_key')]):
            raise Exception("字节跳动ASR API配置不完整")
        
        # 这里需要实现字节跳动ASR API调用
        # 由于API较复杂，这里先返回占位符
        raise Exception("字节跳动ASR API暂未实现")
    
    def text_to_speech(self, text: str, character: Optional[Dict] = None) -> str:
        """文字转语音"""
        try:
            # 1. 尝试使用字节跳动TTS API
            if self.voice_config.get('api_config', {}).get('access_key'):
                try:
                    audio_url = self.bytedance_text_to_speech(text, character)
                    print("✅ 使用字节跳动TTS合成成功")
                    return audio_url
                except Exception as e:
                    print(f"⚠️ 字节跳动TTS合成失败: {e}")
            
            # 2. 备用：使用本地TTS
            if self.tts_enabled:
                return self.local_text_to_speech(text)
            
            raise Exception("所有语音合成方式都不可用")
            
        except Exception as e:
            logger.error(f"语音合成失败: {e}")
            raise Exception(f"语音合成失败: {str(e)}")
    
    def bytedance_text_to_speech(self, text: str, character: Optional[Dict] = None) -> str:
        """使用字节跳动TTS API进行语音合成"""
        api_config = self.voice_config.get('api_config', {})
        
        if not all([api_config.get('app_id'), api_config.get('access_key'), api_config.get('app_key')]):
            raise Exception("字节跳动TTS API配置不完整")
        
        # 选择语音类型
        voice_type = "female"  # 默认女声
        if character and character.get('id') in self.voice_config.get('character_voice_mapping', {}):
            voice_mapping = self.voice_config['character_voice_mapping'][character['id']]
            voice_type = voice_mapping.get('voice_type', 'female')
        
        speaker = self.voice_config.get('voice_speakers', {}).get(voice_type, 'zh_female_aojiaonvyou_tob')
        
        # 这里需要实现字节跳动TTS API调用
        # 由于API较复杂，这里先返回占位符
        raise Exception("字节跳动TTS API暂未实现")
    
    def local_text_to_speech(self, text: str) -> str:
        """使用本地TTS引擎进行语音合成"""
        if not self.tts_enabled:
            raise Exception("本地TTS引擎不可用")
        
        try:
            # 生成音频文件名
            audio_filename = f"tts_{int(time.time())}_{hash(text) % 10000}.wav"
            audio_path = os.path.join(self.audio_dir, audio_filename)
            
            # 使用pyttsx3生成语音
            self.tts_engine.save_to_file(text, audio_path)
            self.tts_engine.runAndWait()
            
            # 返回音频文件URL
            return f"/static/audio/{audio_filename}"
            
        except Exception as e:
            logger.error(f"本地TTS合成失败: {e}")
            raise Exception(f"本地TTS合成失败: {str(e)}")
    
    async def start_realtime_voice_session(self, session_id: str, character_config: Dict, 
                                         message_callback: Callable[[str, Dict], None]) -> Dict:
        """启动实时语音会话"""
        try:
            if not PYAUDIO_AVAILABLE:
                raise Exception("PyAudio不可用，无法启动实时语音会话")
            
            # 创建音频会话配置
            session_config = {
                'session_id': session_id,
                'character': character_config,
                'callback': message_callback,
                'status': 'initializing',
                'created_at': datetime.now()
            }
            
            self.audio_sessions[session_id] = session_config
            
            # 如果配置了字节跳动API，尝试建立WebSocket连接
            if self.voice_config.get('api_config', {}).get('access_key'):
                ws_config = await self.create_bytedance_websocket(session_id, character_config)
                session_config['websocket'] = ws_config
                session_config['status'] = 'connected'
                print(f"✅ 实时语音会话 {session_id} 创建成功（字节跳动API）")
            else:
                # 使用本地处理
                session_config['status'] = 'local_mode'
                print(f"✅ 实时语音会话 {session_id} 创建成功（本地模式）")
            
            return {
                'session_id': session_id,
                'status': session_config['status'],
                'config': session_config
            }
            
        except Exception as e:
            logger.error(f"启动实时语音会话失败: {e}")
            raise Exception(f"启动实时语音会话失败: {str(e)}")
    
    async def create_bytedance_websocket(self, session_id: str, character_config: Dict) -> Dict:
        """创建字节跳动WebSocket连接配置"""
        api_config = self.voice_config.get('api_config', {})
        
        # 构建WebSocket连接配置
        ws_config = {
            'url': api_config.get('base_url', ''),
            'headers': {
                'Authorization': f"Bearer {api_config.get('access_key', '')}",
                'Content-Type': 'application/json'
            },
            'session_config': {
                'app_id': api_config.get('app_id', ''),
                'session_id': session_id,
                'character': character_config,
                'audio_settings': self.voice_config.get('audio_settings', {})
            }
        }
        
        return ws_config
    
    def process_realtime_audio(self, session_id: str, audio_data: bytes) -> Dict:
        """处理实时音频数据"""
        try:
            if session_id not in self.audio_sessions:
                raise Exception(f"会话 {session_id} 不存在")
            
            session = self.audio_sessions[session_id]
            
            # 根据会话状态处理音频
            if session['status'] == 'connected':
                # 使用字节跳动API处理
                return self.process_bytedance_audio(session_id, audio_data)
            elif session['status'] == 'local_mode':
                # 使用本地处理
                return self.process_local_audio(session_id, audio_data)
            else:
                raise Exception(f"会话状态无效: {session['status']}")
                
        except Exception as e:
            logger.error(f"处理实时音频失败: {e}")
            return {'error': str(e)}
    
    def process_bytedance_audio(self, session_id: str, audio_data: bytes) -> Dict:
        """使用字节跳动API处理音频"""
        # 这里需要实现字节跳动实时语音API调用
        # 由于API较复杂，这里先返回占位符
        return {
            'type': 'audio_processed',
            'session_id': session_id,
            'message': '字节跳动实时语音API暂未实现'
        }
    
    def process_local_audio(self, session_id: str, audio_data: bytes) -> Dict:
        """使用本地方式处理音频"""
        try:
            # 保存音频数据到临时文件
            temp_path = os.path.join(tempfile.gettempdir(), f"realtime_{session_id}_{int(time.time())}.wav")
            
            with open(temp_path, 'wb') as f:
                f.write(audio_data)
            
            # 使用本地语音识别
            if self.speech_recognition_enabled:
                with sr.AudioFile(temp_path) as source:
                    audio = self.recognizer.record(source)
                
                try:
                    text = self.recognizer.recognize_google(audio, language='zh-CN')
                    
                    # 清理临时文件
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    
                    return {
                        'type': 'speech_recognized',
                        'session_id': session_id,
                        'text': text
                    }
                except Exception as e:
                    return {
                        'type': 'recognition_error',
                        'session_id': session_id,
                        'error': str(e)
                    }
            else:
                return {
                    'type': 'error',
                    'session_id': session_id,
                    'error': '语音识别不可用'
                }
                
        except Exception as e:
            logger.error(f"本地音频处理失败: {e}")
            return {
                'type': 'error',
                'session_id': session_id,
                'error': str(e)
            }
    
    def stop_realtime_voice_session(self, session_id: str) -> bool:
        """停止实时语音会话"""
        try:
            if session_id in self.audio_sessions:
                session = self.audio_sessions[session_id]
                
                # 关闭WebSocket连接（如果有）
                if 'websocket' in session:
                    # 这里需要实现WebSocket关闭逻辑
                    pass
                
                # 停止录音线程（如果有）
                if session_id in self.recording_threads:
                    # 这里需要实现录音线程停止逻辑
                    del self.recording_threads[session_id]
                
                # 删除会话
                del self.audio_sessions[session_id]
                
                print(f"✅ 实时语音会话 {session_id} 已停止")
                return True
            else:
                print(f"⚠️ 会话 {session_id} 不存在")
                return False
                
        except Exception as e:
            logger.error(f"停止实时语音会话失败: {e}")
            return False
    
    def get_session_status(self, session_id: str) -> Optional[Dict]:
        """获取会话状态"""
        return self.audio_sessions.get(session_id)
    
    def list_active_sessions(self) -> List[Dict]:
        """列出所有活跃会话"""
        return [
            {
                'session_id': sid,
                'status': session['status'],
                'character': session.get('character', {}),
                'created_at': session['created_at'].isoformat()
            }
            for sid, session in self.audio_sessions.items()
        ]
    
    def cleanup_expired_sessions(self, max_age_hours: int = 24):
        """清理过期会话"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.audio_sessions.items():
            age = current_time - session['created_at']
            if age.total_seconds() > max_age_hours * 3600:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.stop_realtime_voice_session(session_id)
        
        if expired_sessions:
            print(f"🧹 清理了 {len(expired_sessions)} 个过期语音会话")
        
        return len(expired_sessions)