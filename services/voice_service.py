"""
语音服务模块 - 处理语音识别和语音合成
"""

import os
import tempfile
import uuid
from typing import Dict, Any, Optional
import threading
from werkzeug.datastructures import FileStorage
import io

# 尝试导入语音相关库，如果失败则禁用语音功能
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    sr = None
    SPEECH_RECOGNITION_AVAILABLE = False
    print("⚠️ SpeechRecognition未安装，语音识别功能将被禁用")

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    pyttsx3 = None
    TTS_AVAILABLE = False
    print("⚠️ pyttsx3未安装，语音合成功能将被禁用")

class VoiceService:
    def __init__(self):
        # 音频文件存储路径
        self.audio_dir = "static/audio"
        os.makedirs(self.audio_dir, exist_ok=True)
        
        # 初始化语音识别器（如果可用）
        if SPEECH_RECOGNITION_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                # 尝试初始化麦克风，如果失败则禁用
                try:
                    self.microphone = sr.Microphone()
                    self.speech_recognition_enabled = True
                except Exception as e:
                    print(f"⚠️ 麦克风初始化失败: {e}")
                    self.speech_recognition_enabled = False
            except Exception as e:
                print(f"⚠️ 语音识别初始化失败: {e}")
                self.speech_recognition_enabled = False
        else:
            self.speech_recognition_enabled = False
        
        # 初始化TTS引擎（如果可用）
        self.tts_enabled = False  # 先设置默认值
        if TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_enabled = True  # 设置为True后再调用setup
                self.setup_tts_engine()
            except Exception as e:
                print(f"⚠️ TTS引擎初始化失败: {e}")
                self.tts_enabled = False
        
        print(f"🎤 语音识别: {'✅ 可用' if self.speech_recognition_enabled else '❌ 不可用'}")
        print(f"🔊 语音合成: {'✅ 可用' if self.tts_enabled else '❌ 不可用'}")
    
    def setup_tts_engine(self):
        """配置TTS引擎"""
        if not self.tts_enabled:
            return
            
        try:
            # 设置语音速度
            self.tts_engine.setProperty('rate', 150)
            
            # 设置音量
            self.tts_engine.setProperty('volume', 0.9)
            
            # 获取可用的语音
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # 优先选择女性声音
                for voice in voices:
                    if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
                else:
                    # 如果没有找到女性声音，使用第一个可用声音
                    self.tts_engine.setProperty('voice', voices[0].id)
        except Exception as e:
            print(f"⚠️ TTS引擎配置失败: {e}")
            self.tts_enabled = False
    
    def _is_wav_file(self, audio_data: bytes) -> bool:
        """检查是否为WAV文件"""
        return audio_data.startswith(b'RIFF') and b'WAVE' in audio_data[:12]
    
    def speech_to_text_with_api(self, audio_file: FileStorage) -> str:
        """使用火山引擎ASR语音识别API进行语音转文字"""
        import requests
        import base64
        import json
        
        try:
            # 读取音频文件数据
            audio_data = audio_file.read()
            audio_file.seek(0)
            
            print(f"🎵 使用火山引擎ASR API识别音频，大小: {len(audio_data)} bytes")
            
            # 获取API配置
            api_key = os.getenv('OPENAI_API_KEY')
            # 火山引擎ASR服务的基础URL
            asr_base = "https://openspeech.bytedance.com/api/v1/vc"
            
            if not api_key:
                raise Exception("未配置语音识别API密钥")
            
            # 方法1: 尝试使用火山引擎ASR API
            try:
                return self._call_volcengine_asr(audio_data, api_key)
            except Exception as asr_error:
                print(f"⚠️ 火山引擎ASR失败: {asr_error}")
                
                # 方法2: 回退到使用豆包模型的文本接口（将音频转为文本描述）
                return self._call_doubao_text_api(audio_data, api_key)
                
        except Exception as e:
            print(f"❌ API语音识别错误: {e}")
            raise Exception(f"语音识别失败: {str(e)}")
    
    def _call_volcengine_asr(self, audio_data: bytes, api_key: str) -> str:
        """调用火山引擎ASR服务"""
        import requests
        
        # 火山引擎ASR API端点
        url = "https://openspeech.bytedance.com/api/v1/vc"
        
        # 准备multipart/form-data请求
        files = {
            'audio': ('audio.wav', audio_data, 'audio/wav')
        }
        
        data = {
            'language': 'zh-CN',
            'format': 'wav',
            'sample_rate': 16000,
            'channel': 1
        }
        
        headers = {
            'Authorization': f'Bearer {api_key}'
        }
        
        print("🔍 调用火山引擎ASR API...")
        response = requests.post(url, files=files, data=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'result' in result and 'text' in result['result']:
                text = result['result']['text']
                print(f"✅ ASR识别成功: {text}")
                return text
            else:
                raise Exception("ASR响应格式错误")
        else:
            raise Exception(f"ASR请求失败: {response.status_code}, {response.text}")
    
    def _call_doubao_text_api(self, audio_data: bytes, api_key: str) -> str:
        """使用豆包文本模型处理语音（备用方案）"""
        import requests
        import base64
        
        api_base = os.getenv('OPENAI_API_BASE', 'https://ark.cn-beijing.volces.com/api/v3')
        model_name = os.getenv('OPENAI_MODEL', 'doubao-seed-1-6-250615')
        
        url = f"{api_base}/chat/completions"
        
        # 将音频编码为base64并作为文本描述发送
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": f"我有一段音频数据（base64编码）：{audio_base64[:100]}...，请帮我识别这段语音的内容。如果无法直接处理音频，请回复'无法处理音频数据'。"
                }
            ],
            "stream": False,
            "temperature": 0.1,
            "max_tokens": 500
        }
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        print("🔍 使用豆包文本模型处理语音...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0].get('message', {}).get('content', '')
                if '无法处理音频数据' in content:
                    raise Exception("豆包模型无法直接处理音频数据")
                return content
            else:
                raise Exception("豆包响应格式错误")
        else:
            raise Exception(f"豆包请求失败: {response.status_code}, {response.text}")
    
    def _convert_audio_to_wav(self, audio_file: FileStorage) -> str:
        """将音频文件转换为WAV格式"""
        # 获取原始文件数据
        audio_data = audio_file.read()
        audio_file.seek(0)  # 重置文件指针
        
        print(f"🎵 原始音频数据大小: {len(audio_data)} bytes")
        
        # 创建临时WAV文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as wav_file:
            wav_path = wav_file.name
        
        # 检查是否已经是WAV格式
        if self._is_wav_file(audio_data):
            print("✅ 检测到WAV格式，直接使用")
            with open(wav_path, 'wb') as f:
                f.write(audio_data)
            return wav_path
        
        # 如果不是WAV格式，尝试使用pydub转换（但不依赖ffmpeg）
        try:
            from pydub import AudioSegment
            from pydub.utils import which
            
            # 检查是否有ffmpeg
            if which("ffmpeg") is None:
                print("⚠️ 未找到ffmpeg，无法处理WebM格式")
                raise Exception("需要安装ffmpeg来处理WebM格式，或使用前端WAV录制")
            
            # 创建原始文件的临时副本
            with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
                temp_path = temp_file.name
                temp_file.write(audio_data)
            
            try:
                print("🔄 尝试使用pydub转换音频...")
                audio_segment = AudioSegment.from_file(temp_path, format="webm")
                
                # 转换为标准WAV格式：16kHz, 单声道, 16位
                print("🔄 转换音频格式...")
                audio_segment = audio_segment.set_frame_rate(16000).set_channels(1).set_sample_width(2)
                
                # 导出为WAV
                audio_segment.export(wav_path, format="wav")
                print(f"✅ 音频转换完成: {wav_path}")
                
                return wav_path
                
            finally:
                # 清理临时文件
                if os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
            
        except ImportError:
            print("⚠️ pydub未安装")
            raise Exception("需要安装pydub库或使用前端WAV录制")
        except Exception as e:
            print(f"❌ 音频转换失败: {e}")
            # 如果转换失败，尝试直接保存原始数据（可能是某种兼容格式）
            try:
                with open(wav_path, 'wb') as f:
                    f.write(audio_data)
                print("⚠️ 转换失败，尝试直接使用原始数据")
                return wav_path
            except:
                raise Exception(f"音频格式转换失败，建议使用前端WAV录制: {e}")

    def speech_to_text_with_api(self, audio_file: FileStorage) -> str:
        """使用字节跳动语音识别API进行语音转文字"""
        import requests
        import json
        import uuid
        
        try:
            # 读取音频文件数据
            audio_data = audio_file.read()
            audio_file.seek(0)
            
            print(f"🎵 使用字节跳动ASR API识别音频，大小: {len(audio_data)} bytes")
            
            # 从配置文件获取API配置
            from services.voice_config_service import VoiceConfigService
            voice_config_service = VoiceConfigService()
            
            # 获取WebSocket配置（包含API密钥）
            ws_config = voice_config_service.get_ws_config()
            headers = ws_config["headers"]
            
            # 字节跳动语音识别API端点
            url = "https://openspeech.bytedance.com/api/v1/vc"
            
            # 准备multipart/form-data请求
            files = {
                'audio': ('audio.wav', audio_data, 'audio/wav')
            }
            
            data = {
                'language': 'zh-CN',
                'format': 'wav',
                'sample_rate': 16000,
                'channel': 1
            }
            
            # 使用配置中的认证信息
            request_headers = {
                'X-Api-App-ID': headers['X-Api-App-ID'],
                'X-Api-Access-Key': headers['X-Api-Access-Key'],
                'X-Api-Resource-Id': headers['X-Api-Resource-Id'],
                'X-Api-App-Key': headers['X-Api-App-Key']
            }
            
            print("🔍 调用字节跳动ASR API...")
            response = requests.post(url, files=files, data=data, headers=request_headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'result' in result and 'text' in result['result']:
                    text = result['result']['text'].strip()
                    print(f"✅ ASR识别成功: {text}")
                    return text
                else:
                    print(f"❌ ASR响应格式错误: {result}")
                    raise Exception("ASR响应格式错误")
            else:
                print(f"❌ ASR请求失败: {response.status_code}, {response.text}")
                raise Exception(f"ASR请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 字节跳动ASR识别错误: {e}")
            raise Exception(f"语音识别失败: {str(e)}")

    def speech_to_text(self, audio_file: FileStorage) -> str:
        """语音转文字 - 优先使用API，失败时回退到本地识别"""
        
        # 首先尝试使用豆包API
        try:
            return self.speech_to_text_with_api(audio_file)
        except Exception as api_error:
            print(f"⚠️ API识别失败，尝试本地识别: {api_error}")
            
            # 如果API失败，回退到本地speech_recognition
            if not self.speech_recognition_enabled:
                raise Exception(f"语音识别不可用: {api_error}")
                
            wav_path = None
            try:
                # 转换音频为WAV格式
                wav_path = self._convert_audio_to_wav(audio_file)
                
                # 验证文件是否存在且有内容
                if not os.path.exists(wav_path) or os.path.getsize(wav_path) == 0:
                    raise Exception("音频文件转换失败或为空")
                
                print(f"🎵 本地处理音频文件: {wav_path}, 大小: {os.path.getsize(wav_path)} bytes")
                
                # 使用speech_recognition进行语音识别
                with sr.AudioFile(wav_path) as source:
                    # 调整环境噪音
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    # 读取音频数据
                    audio_data = self.recognizer.record(source)
                
                # 使用Google语音识别（免费版）
                try:
                    print("🔍 尝试本地中文语音识别...")
                    text = self.recognizer.recognize_google(audio_data, language='zh-CN')
                    print(f"✅ 本地中文识别成功: {text}")
                    return text
                except sr.UnknownValueError:
                    print("🔍 本地中文识别失败，尝试英文识别...")
                    try:
                        text = self.recognizer.recognize_google(audio_data, language='en-US')
                        print(f"✅ 本地英文识别成功: {text}")
                        return text
                    except sr.UnknownValueError:
                        raise Exception("无法识别语音内容，请说话清晰一些或检查录音质量")
                except sr.RequestError as e:
                    raise Exception(f"语音识别服务错误: {e}")
                    
            except Exception as e:
                print(f"❌ 本地语音识别错误: {e}")
                raise Exception(f"语音识别失败: {str(e)}")
            finally:
                # 清理临时文件
                if wav_path and os.path.exists(wav_path):
                    try:
                        os.unlink(wav_path)
                    except:
                        pass
    
    def text_to_speech(self, text: str, character: Optional[Dict[str, Any]] = None) -> str:
        """文字转语音 - 优先使用字节跳动TTS API"""
        try:
            # 首先尝试使用字节跳动TTS API
            return self.text_to_speech_with_api(text, character)
        except Exception as api_error:
            print(f"⚠️ 字节跳动TTS API失败，回退到本地TTS: {api_error}")
            
            # 回退到本地TTS
            if not self.tts_enabled:
                raise Exception(f"语音合成不可用: {api_error}")
                
            try:
                # 生成唯一的音频文件名
                audio_filename = f"tts_{uuid.uuid4().hex}.wav"
                audio_path = os.path.join(self.audio_dir, audio_filename)
                
                # 根据角色调整语音参数
                if character:
                    self._adjust_voice_for_character(character)
                
                # 生成语音文件
                self.tts_engine.save_to_file(text, audio_path)
                self.tts_engine.runAndWait()
                
                # 返回音频文件的URL
                return f"/static/audio/{audio_filename}"
                
            except Exception as e:
                raise Exception(f"语音合成失败: {str(e)}")
    
    def text_to_speech_with_api(self, text: str, character: Optional[Dict[str, Any]] = None) -> str:
        """使用字节跳动TTS API进行语音合成"""
        import requests
        import json
        
        try:
            print(f"🔊 使用字节跳动TTS API合成语音: {text[:50]}...")
            
            # 从配置文件获取API配置和角色配置
            from services.voice_config_service import VoiceConfigService
            voice_config_service = VoiceConfigService()
            
            # 根据角色选择语音类型
            voice_type = "female"  # 默认女声
            if character:
                character_id = character.get('id', '')
                # 根据角色选择合适的语音
                if character_id in ['socrates', 'einstein', 'shakespeare', 'confucius']:
                    voice_type = "male"
                elif character_id in ['marie_curie']:
                    voice_type = "female"
            
            # 获取会话配置
            session_config = voice_config_service.get_session_config(
                character.get('id', 'socrates') if character else 'socrates',
                voice_type
            )
            
            # 字节跳动TTS API端点
            url = "https://openspeech.bytedance.com/api/v1/tts"
            
            # 获取WebSocket配置中的认证信息
            ws_config = voice_config_service.get_ws_config()
            headers = ws_config["headers"]
            
            # 准备TTS请求数据
            tts_data = {
                "text": text,
                "speaker": session_config["tts"]["speaker"],
                "format": "wav",
                "sample_rate": 24000,
                "channel": 1,
                "speed": 1.0,
                "volume": 1.0
            }
            
            # 请求头
            request_headers = {
                'X-Api-App-ID': headers['X-Api-App-ID'],
                'X-Api-Access-Key': headers['X-Api-Access-Key'],
                'X-Api-Resource-Id': headers['X-Api-Resource-Id'],
                'X-Api-App-Key': headers['X-Api-App-Key'],
                'Content-Type': 'application/json'
            }
            
            print("🔍 调用字节跳动TTS API...")
            response = requests.post(url, json=tts_data, headers=request_headers, timeout=30)
            
            if response.status_code == 200:
                # 保存音频文件
                audio_filename = f"tts_bytedance_{uuid.uuid4().hex}.wav"
                audio_path = os.path.join(self.audio_dir, audio_filename)
                
                with open(audio_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ TTS合成成功，保存到: {audio_path}")
                return f"/static/audio/{audio_filename}"
            else:
                print(f"❌ TTS请求失败: {response.status_code}, {response.text}")
                raise Exception(f"TTS请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 字节跳动TTS合成错误: {e}")
            raise Exception(f"语音合成失败: {str(e)}")
    
    def _adjust_voice_for_character(self, character: Dict[str, Any]):
        """根据角色调整语音参数"""
        if not self.tts_enabled:
            return
            
        try:
            character_name = character.get('name', '').lower()
            
            # 根据角色调整语音速度和音调
            if '苏格拉底' in character_name or 'socrates' in character_name:
                # 哲学家 - 较慢的语速，深沉的声音
                self.tts_engine.setProperty('rate', 120)
            elif '哈利' in character_name or 'harry' in character_name:
                # 年轻角色 - 较快的语速
                self.tts_engine.setProperty('rate', 160)
            elif '爱因斯坦' in character_name or 'einstein' in character_name:
                # 科学家 - 中等语速
                self.tts_engine.setProperty('rate', 140)
            else:
                # 默认语速
                self.tts_engine.setProperty('rate', 150)
        except Exception as e:
            print(f"⚠️ 调整语音参数失败: {e}")
    
    def get_available_voices(self) -> list:
        """获取可用的语音列表"""
        if not self.tts_enabled:
            return []
            
        try:
            voices = self.tts_engine.getProperty('voices')
            voice_list = []
            
            for voice in voices:
                voice_info = {
                    'id': voice.id,
                    'name': voice.name,
                    'languages': getattr(voice, 'languages', []),
                    'gender': getattr(voice, 'gender', 'unknown')
                }
                voice_list.append(voice_info)
            
            return voice_list
        except Exception as e:
            print(f"⚠️ 获取语音列表失败: {e}")
            return []
    
    def set_voice(self, voice_id: str):
        """设置特定的语音"""
        if not self.tts_enabled:
            return False
            
        try:
            self.tts_engine.setProperty('voice', voice_id)
            return True
        except Exception:
            return False
    
    def record_audio(self, duration: int = 5) -> str:
        """录制音频（用于实时语音输入）"""
        if not self.speech_recognition_enabled:
            raise Exception("语音录制功能不可用，请检查相关依赖是否已安装")
            
        try:
            with self.microphone as source:
                print("请说话...")
                # 调整环境噪音
                self.recognizer.adjust_for_ambient_noise(source)
                # 录制音频
                audio_data = self.recognizer.listen(source, timeout=duration)
            
            # 保存录制的音频
            audio_filename = f"recorded_{uuid.uuid4().hex}.wav"
            audio_path = os.path.join(self.audio_dir, audio_filename)
            
            with open(audio_path, "wb") as f:
                f.write(audio_data.get_wav_data())
            
            return audio_path
            
        except Exception as e:
            raise Exception(f"录音失败: {str(e)}")
    
    def cleanup_old_audio_files(self, max_age_hours: int = 24):
        """清理旧的音频文件"""
        try:
            import time
            current_time = time.time()
            
            for filename in os.listdir(self.audio_dir):
                file_path = os.path.join(self.audio_dir, filename)
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getctime(file_path)
                    if file_age > max_age_hours * 3600:  # 转换为秒
                        os.remove(file_path)
                        
        except Exception as e:
            print(f"清理音频文件失败: {e}")

# 语音服务的异步包装器
class AsyncVoiceService:
    def __init__(self):
        self.voice_service = VoiceService()
    
    def async_text_to_speech(self, text: str, character: Optional[Dict[str, Any]] = None, callback=None):
        """异步语音合成"""
        def _generate_speech():
            try:
                audio_url = self.voice_service.text_to_speech(text, character)
                if callback:
                    callback(audio_url, None)
            except Exception as e:
                if callback:
                    callback(None, str(e))
        
        thread = threading.Thread(target=_generate_speech)
        thread.daemon = True
        thread.start()
    
    def async_speech_to_text(self, audio_file: FileStorage, callback=None):
        """异步语音识别"""
        def _recognize_speech():
            try:
                text = self.voice_service.speech_to_text(audio_file)
                if callback:
                    callback(text, None)
            except Exception as e:
                if callback:
                    callback(None, str(e))
        
        thread = threading.Thread(target=_recognize_speech)
        thread.daemon = True
        thread.start()