#!/usr/bin/env python3
"""
本地语音识别服务
使用SpeechRecognition库实现本地语音识别功能，无需API密钥
"""

import os
import logging
import tempfile
import uuid
from typing import Optional, Dict, Any
from werkzeug.datastructures import FileStorage

# 尝试导入SpeechRecognition库
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

logger = logging.getLogger(__name__)

class LocalSTTService:
    """本地语音识别服务，使用SpeechRecognition库实现"""
    
    def __init__(self):
        """初始化本地语音识别服务"""
        self.audio_dir = "static/audio"
        os.makedirs(self.audio_dir, exist_ok=True)
        
        # 检查SpeechRecognition是否可用
        self.is_configured = SR_AVAILABLE
        
        if self.is_configured:
            # 创建识别器
            self.recognizer = sr.Recognizer()
            logger.info("✅ 本地语音识别服务初始化成功")
        else:
            logger.warning("⚠️ 本地语音识别服务未配置，请安装speech_recognition库")
    
    def speech_to_text(self, audio_file: FileStorage) -> str:
        """语音转文字"""
        if not self.is_configured:
            return "本地语音识别服务未配置，请安装speech_recognition库"
        
        try:
            # 读取音频数据
            audio_data = audio_file.read()
            audio_file.seek(0)  # 重置文件指针
            
            # 保存临时文件
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_audio_path = temp_file.name
            
            try:
                # 使用SpeechRecognition进行识别
                with sr.AudioFile(temp_audio_path) as source:
                    # 调整识别参数
                    self.recognizer.pause_threshold = 0.8  # 静音阈值
                    self.recognizer.energy_threshold = 300  # 能量阈值
                    
                    # 读取音频数据
                    audio = self.recognizer.record(source)
                    
                    # 尝试多种识别引擎
                    text = self._try_recognition_engines(audio)
                    
                    if text:
                        logger.info(f"语音识别成功: {text}")
                        return text
                    else:
                        return "未能识别语音内容，请尝试说得更清晰或使用其他语音识别服务"
            
            finally:
                # 清理临时文件
                try:
                    os.unlink(temp_audio_path)
                except:
                    pass
                
        except Exception as e:
            logger.error(f"语音识别处理失败: {e}")
            return f"语音识别处理失败: {str(e)}"
    
    def _try_recognition_engines(self, audio) -> str:
        """尝试多种识别引擎"""
        # 首先尝试Google（需要网络连接）
        try:
            text = self.recognizer.recognize_google(audio, language="zh-CN")
            if text:
                logger.info("使用Google引擎识别成功")
                return text
        except Exception as e:
            logger.warning(f"Google语音识别失败: {e}")
        
        # 尝试Sphinx（离线，英文）
        try:
            text = self.recognizer.recognize_sphinx(audio)
            if text:
                logger.info("使用Sphinx引擎识别成功")
                return text
        except Exception as e:
            logger.warning(f"Sphinx语音识别失败: {e}")
        
        # 尝试Azure（如果配置了密钥）
        azure_key = os.getenv('AZURE_SPEECH_KEY')
        azure_region = os.getenv('AZURE_SPEECH_REGION')
        if azure_key and azure_region:
            try:
                text = self.recognizer.recognize_azure(audio, key=azure_key, location=azure_region, language="zh-CN")
                if text:
                    logger.info("使用Azure引擎识别成功")
                    return text
            except Exception as e:
                logger.warning(f"Azure语音识别失败: {e}")
        
        # 尝试Whisper（如果安装了）
        try:
            import whisper
            model = whisper.load_model("base")
            
            # 保存临时文件
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            with open(temp_path, 'wb') as f:
                f.write(audio.get_wav_data())
            
            # 使用Whisper识别
            result = model.transcribe(temp_path, language="zh")
            text = result["text"]
            
            # 清理临时文件
            os.unlink(temp_path)
            
            if text:
                logger.info("使用Whisper引擎识别成功")
                return text
                
        except ImportError:
            logger.warning("Whisper未安装，跳过")
        except Exception as e:
            logger.warning(f"Whisper语音识别失败: {e}")
        
        # 所有引擎都失败了
        return ""
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        status = {
            'configured': self.is_configured,
            'sr_available': SR_AVAILABLE,
            'engines': []
        }
        
        # 检查可用的引擎
        if self.is_configured:
            # 检查Google
            try:
                status['engines'].append({
                    'name': 'Google Speech Recognition',
                    'available': True,
                    'requires_network': True
                })
            except:
                pass
            
            # 检查Sphinx
            try:
                import pocketsphinx
                status['engines'].append({
                    'name': 'CMU Sphinx',
                    'available': True,
                    'requires_network': False
                })
            except ImportError:
                status['engines'].append({
                    'name': 'CMU Sphinx',
                    'available': False,
                    'requires_network': False
                })
            
            # 检查Whisper
            try:
                import whisper
                status['engines'].append({
                    'name': 'OpenAI Whisper',
                    'available': True,
                    'requires_network': False
                })
            except ImportError:
                status['engines'].append({
                    'name': 'OpenAI Whisper',
                    'available': False,
                    'requires_network': False
                })
            
            # 检查Azure
            azure_key = os.getenv('AZURE_SPEECH_KEY')
            azure_region = os.getenv('AZURE_SPEECH_REGION')
            status['engines'].append({
                'name': 'Microsoft Azure',
                'available': bool(azure_key and azure_region),
                'requires_network': True
            })
        
        return status
    
    def test_stt_service(self) -> Dict[str, Any]:
        """测试语音识别服务"""
        if not self.is_configured:
            return {
                'service_available': False,
                'error': '语音识别服务未配置'
            }
        
        # 检查可用引擎
        status = self.get_service_status()
        available_engines = [e for e in status['engines'] if e['available']]
        
        return {
            'service_available': self.is_configured,
            'available_engines': available_engines,
            'offline_available': any(not e['requires_network'] for e in available_engines),
            'error': None if available_engines else '没有可用的语音识别引擎'
        }
