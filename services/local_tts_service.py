#!/usr/bin/env python3
"""
本地语音合成服务
使用pyttsx3库实现本地TTS功能，无需API密钥
"""

import os
import uuid
import logging
import tempfile
import threading
from typing import Optional, Dict, Any, List

# 尝试导入pyttsx3库
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

# 尝试导入gTTS库作为备选
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

logger = logging.getLogger(__name__)

class LocalTTSService:
    """本地语音合成服务，使用pyttsx3或gTTS实现"""
    
    def __init__(self):
        """初始化本地TTS服务"""
        self.audio_dir = "static/audio"
        os.makedirs(self.audio_dir, exist_ok=True)
        
        # 检查可用的TTS引擎
        self.engine_type = self._detect_tts_engine()
        self.engine = None
        self.is_configured = False
        
        # 初始化TTS引擎
        if self.engine_type == "pyttsx3":
            try:
                self.engine = pyttsx3.init()
                self.is_configured = True
                logger.info("✅ 本地TTS服务(pyttsx3)初始化成功")
            except Exception as e:
                logger.error(f"❌ pyttsx3初始化失败: {e}")
        elif self.engine_type == "gtts":
            self.is_configured = True
            logger.info("✅ 本地TTS服务(gTTS)初始化成功")
        else:
            logger.warning("⚠️ 未找到可用的TTS引擎，请安装pyttsx3或gTTS")
    
    def _detect_tts_engine(self) -> str:
        """检测可用的TTS引擎"""
        if PYTTSX3_AVAILABLE:
            return "pyttsx3"
        elif GTTS_AVAILABLE:
            return "gtts"
        else:
            return "none"
    
    def text_to_speech(self, text: str, character: Optional[Dict] = None) -> Dict[str, Any]:
        """文字转语音，返回标准格式的结果"""
        if not self.is_configured:
            logger.warning("本地TTS服务未配置")
            return {
                'success': False,
                'error': '本地TTS服务未配置，请安装pyttsx3或gTTS'
            }
        
        if not text or len(text.strip()) == 0:
            logger.warning("文本为空，跳过语音合成")
            return {
                'success': False,
                'error': '文本为空'
            }
        
        try:
            # 根据角色获取语音参数
            voice_params = self._get_voice_params(character)
            
            # 生成唯一文件名
            audio_filename = f"tts_{uuid.uuid4().hex[:8]}.mp3"
            audio_path = os.path.join(self.audio_dir, audio_filename)
            
            # 使用对应的TTS引擎合成语音
            if self.engine_type == "pyttsx3":
                success = self._synthesize_with_pyttsx3(text, audio_path, voice_params)
            elif self.engine_type == "gtts":
                success = self._synthesize_with_gtts(text, audio_path, voice_params)
            else:
                return {
                    'success': False,
                    'error': '未找到可用的TTS引擎'
                }
            
            if success:
                # 返回标准化的结果
                audio_url = f"/static/audio/{audio_filename}"
                logger.info(f"语音合成成功: {audio_url}")
                return {
                    'success': True,
                    'audio_path': audio_path,
                    'audio_url': audio_url
                }
            else:
                return {
                    'success': False,
                    'error': '语音合成失败'
                }
                
        except Exception as e:
            logger.error(f"语音合成处理失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _synthesize_with_pyttsx3(self, text: str, output_path: str, voice_params: Dict) -> bool:
        """使用pyttsx3合成语音"""
        try:
            # 设置语音参数
            self.engine.setProperty('rate', voice_params['rate'])  # 语速
            self.engine.setProperty('volume', voice_params['volume'])  # 音量
            
            # 设置声音（如果有可用的声音）
            voices = self.engine.getProperty('voices')
            if voices:
                # 根据性别选择声音
                gender = voice_params.get('gender', 'female')
                voice_index = 0  # 默认使用第一个声音
                
                # 尝试找到匹配性别的声音
                for i, voice in enumerate(voices):
                    voice_name = voice.name.lower()
                    if gender == 'female' and ('female' in voice_name or 'woman' in voice_name or 'girl' in voice_name):
                        voice_index = i
                        break
                    elif gender == 'male' and ('male' in voice_name or 'man' in voice_name or 'boy' in voice_name):
                        voice_index = i
                        break
                
                # 设置选择的声音
                if voice_index < len(voices):
                    self.engine.setProperty('voice', voices[voice_index].id)
            
            # 使用临时文件进行转换
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            # 合成语音到临时文件
            self.engine.save_to_file(text, temp_path)
            self.engine.runAndWait()
            
            # 转换为MP3格式（如果有pydub）
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_wav(temp_path)
                audio.export(output_path, format="mp3")
            except ImportError:
                # 如果没有pydub，直接复制WAV文件
                import shutil
                shutil.copy(temp_path, output_path)
            
            # 清理临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            
            return os.path.exists(output_path)
            
        except Exception as e:
            logger.error(f"pyttsx3合成失败: {e}")
            return False
    
    def _synthesize_with_gtts(self, text: str, output_path: str, voice_params: Dict) -> bool:
        """使用gTTS合成语音"""
        try:
            # 设置语言（默认中文）
            lang = voice_params.get('lang', 'zh-cn')
            
            # 使用gTTS合成语音
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(output_path)
            
            return os.path.exists(output_path)
            
        except Exception as e:
            logger.error(f"gTTS合成失败: {e}")
            return False
    
    def _get_voice_params(self, character: Optional[Dict] = None) -> Dict[str, Any]:
        """根据角色获取语音参数"""
        # 默认语音参数
        params = {
            'rate': 150,  # 语速 (pyttsx3: 50-300)
            'volume': 1.0,  # 音量 (0.0-1.0)
            'pitch': 1.0,  # 音调 (不是所有引擎都支持)
            'gender': 'female',  # 性别
            'lang': 'zh-cn'  # 语言
        }
        
        if character:
            character_name = character.get('name', '').lower()
            gender = character.get('gender', 'female')
            personality = character.get('personality', '')
            
            # 根据角色名称和性别选择合适的语音
            if gender == 'male' or any(name in character_name for name in ['苏格拉底', '孔子', '爱因斯坦', '莎士比亚']):
                # 男性角色
                params['gender'] = 'male'
                params['rate'] = 140  # 稍慢的语速
            elif '活泼' in personality or '开朗' in personality:
                # 活泼角色
                params['rate'] = 170  # 稍快语速
            elif '优雅' in personality or '温柔' in personality:
                # 优雅角色
                params['rate'] = 130  # 稍慢语速
        
        return params
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            'configured': self.is_configured,
            'engine_type': self.engine_type,
            'pyttsx3_available': PYTTSX3_AVAILABLE,
            'gtts_available': GTTS_AVAILABLE
        }
    
    def test_tts_service(self) -> Dict[str, Any]:
        """测试TTS服务"""
        if not self.is_configured:
            return {
                'service_available': False,
                'error': 'TTS服务未配置'
            }
        
        try:
            # 尝试合成一个简短的测试文本
            test_result = self.text_to_speech("测试", None)
            
            return {
                'service_available': bool(test_result and test_result.get('success')),
                'engine_type': self.engine_type,
                'test_synthesis': bool(test_result and test_result.get('success')),
                'error': None if (test_result and test_result.get('success')) else '测试合成失败'
            }
            
        except Exception as e:
            return {
                'service_available': False,
                'engine_type': self.engine_type,
                'test_synthesis': False,
                'error': str(e)
            }
    
    def get_supported_voices(self) -> List[Dict[str, Any]]:
        """获取支持的语音列表"""
        voices = []
        
        if self.engine_type == "pyttsx3" and self.engine:
            try:
                engine_voices = self.engine.getProperty('voices')
                for i, voice in enumerate(engine_voices):
                    # 判断性别
                    gender = 'unknown'
                    if 'female' in voice.name.lower() or 'woman' in voice.name.lower() or 'girl' in voice.name.lower():
                        gender = 'female'
                    elif 'male' in voice.name.lower() or 'man' in voice.name.lower() or 'boy' in voice.name.lower():
                        gender = 'male'
                    
                    voices.append({
                        'id': i,
                        'name': voice.name,
                        'gender': gender,
                        'description': f'本地语音 ({voice.name})'
                    })
            except Exception as e:
                logger.error(f"获取pyttsx3语音列表失败: {e}")
        
        # 如果没有找到语音，添加默认语音
        if not voices:
            voices = [
                {'id': 0, 'name': '默认女声', 'gender': 'female', 'description': '本地TTS默认女声'},
                {'id': 1, 'name': '默认男声', 'gender': 'male', 'description': '本地TTS默认男声'}
            ]
        
        return voices
