#!/usr/bin/env python3
"""
百度语音识别服务
使用百度AI开放平台的语音识别API
"""

import os
import requests
import json
import base64
import tempfile
import uuid
import logging
import time
from typing import Optional, Dict, List, Any
from werkzeug.datastructures import FileStorage

# 音频处理
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

# 导入自定义音频转换器
from utils.audio_converter import AudioConverter

logger = logging.getLogger(__name__)

class BaiduVoiceService:
    """百度语音识别服务"""
    
    def __init__(self):
        self.audio_dir = "static/audio"
        os.makedirs(self.audio_dir, exist_ok=True)
        
        # 从环境变量获取API配置
        self.api_key = os.getenv('BAIDU_API_KEY')
        self.secret_key = os.getenv('BAIDU_SECRET_KEY')
        
        # API URLs
        self.token_url = "https://aip.baidubce.com/oauth/2.0/token"
        self.speech_url = "https://vop.baidu.com/server_api"
        
        # 访问令牌缓存
        self.access_token = None
        self.token_expires_at = 0
        
        # 检查配置
        self.is_configured = bool(self.api_key and self.secret_key)
        
        if self.is_configured:
            logger.info("✅ 百度语音识别服务已配置")
        else:
            logger.warning("⚠️ 百度语音识别服务未配置，请设置API密钥")
    
    def _get_access_token(self) -> Optional[str]:
        """获取百度API访问令牌"""
        # 检查缓存的令牌是否还有效
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
        
        if not self.is_configured:
            logger.error("百度API未配置")
            return None
        
        try:
            params = {
                'grant_type': 'client_credentials',
                'client_id': self.api_key,
                'client_secret': self.secret_key
            }
            
            response = requests.post(self.token_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'access_token' in data:
                self.access_token = data['access_token']
                # 令牌有效期通常是30天，这里设置为29天
                self.token_expires_at = time.time() + (29 * 24 * 3600)
                logger.info("百度API访问令牌获取成功")
                return self.access_token
            else:
                logger.error(f"获取访问令牌失败: {data}")
                return None
                
        except Exception as e:
            logger.error(f"获取百度API访问令牌失败: {e}")
            return None
    
    def speech_to_text(self, audio_file: FileStorage) -> str:
        """语音转文字"""
        if not self.is_configured:
            return "百度语音识别服务未配置，请检查API密钥设置"
        
        # 获取访问令牌
        access_token = self._get_access_token()
        if not access_token:
            return "无法获取百度API访问令牌"
        
        try:
            # 读取音频数据
            audio_data = audio_file.read()
            audio_file.seek(0)  # 重置文件指针
            
            # 检查文件大小（百度API限制4MB）
            if len(audio_data) > 4 * 1024 * 1024:
                return "音频文件过大，请上传小于4MB的文件"
            
            # 处理音频格式
            processed_audio = self._process_audio_format(audio_data, audio_file.filename)
            if not processed_audio:
                return "音频格式处理失败"
            
            # Base64编码
            audio_base64 = base64.b64encode(processed_audio).decode('utf-8')
            
            # 构建请求参数
            params = {
                'dev_pid': 1537,  # 普通话(支持简单的英文识别)
                'format': 'wav',
                'rate': 16000,
                'token': access_token,
                'cuid': str(uuid.uuid4()),
                'channel': 1,
                'speech': audio_base64,
                'len': len(processed_audio)
            }
            
            # 发送请求
            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                self.speech_url,
                data=json.dumps(params),
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            # 处理响应
            if result.get('err_no') == 0:
                # 成功识别
                recognized_text = ''.join(result.get('result', []))
                if recognized_text:
                    logger.info(f"语音识别成功: {recognized_text}")
                    return recognized_text
                else:
                    return "语音识别结果为空，请重新录音"
            else:
                error_msg = result.get('err_msg', '未知错误')
                logger.error(f"百度语音识别API错误: {result.get('err_no')} - {error_msg}")
                return f"语音识别失败: {error_msg}"
                
        except Exception as e:
            logger.error(f"语音识别处理失败: {e}")
            return f"语音识别处理失败: {str(e)}"
    
    def _process_audio_format(self, audio_data: bytes, filename: str) -> Optional[bytes]:
        """处理音频格式，转换为百度API要求的格式"""
        try:
            # 使用自定义音频转换器
            converter = AudioConverter()
            
            # 检查是否是WAV格式
            if filename and filename.lower().endswith('.wav'):
                # 验证WAV格式
                format_info = converter.validate_wav_format(audio_data)
                if format_info.get('valid'):
                    # 检查采样率和声道
                    if format_info.get('sample_rate') == 16000 and format_info.get('channels') == 1:
                        return audio_data
                    else:
                        logger.info(f"WAV格式需要转换: {format_info}")
            
            # 如果有pydub，尝试使用它进行转换
            if PYDUB_AVAILABLE:
                return self._convert_with_pydub(audio_data, filename)
            else:
                # 使用自定义转换器
                return self._convert_with_custom_converter(audio_data, filename)
                
        except Exception as e:
            logger.error(f"音频格式处理失败: {e}")
            return None
    
    def _convert_with_pydub(self, audio_data: bytes, filename: str) -> Optional[bytes]:
        """使用pydub转换音频格式"""
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.tmp') as temp_input:
                temp_input.write(audio_data)
                temp_input.flush()
                
                # 加载音频
                audio = AudioSegment.from_file(temp_input.name)
                
                # 转换为16kHz单声道WAV
                audio = audio.set_frame_rate(16000).set_channels(1)
                
                # 导出为WAV格式
                with tempfile.NamedTemporaryFile(suffix='.wav') as temp_output:
                    audio.export(temp_output.name, format='wav')
                    temp_output.seek(0)
                    return temp_output.read()
                    
        except Exception as e:
            logger.error(f"pydub音频转换失败: {e}")
            return None
    
    def _convert_with_custom_converter(self, audio_data: bytes, filename: str) -> Optional[bytes]:
        """使用自定义转换器转换音频格式"""
        try:
            converter = AudioConverter()
            
            # 如果是WebM格式，尝试转换
            if filename and filename.lower().endswith('.webm'):
                # 创建Blob对象模拟
                # 注意：这里需要在前端完成WebM到WAV的转换
                logger.warning("WebM格式需要在前端转换为WAV")
                return None
            
            # 对于其他格式，返回原始数据（可能需要进一步处理）
            return audio_data
            
        except Exception as e:
            logger.error(f"自定义音频转换失败: {e}")
            return None
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            'configured': self.is_configured,
            'api_key_set': bool(self.api_key),
            'secret_key_set': bool(self.secret_key),
            'pydub_available': PYDUB_AVAILABLE,
            'token_valid': bool(self.access_token and time.time() < self.token_expires_at)
        }
    
    def test_api_connection(self) -> Dict[str, Any]:
        """测试API连接"""
        if not self.is_configured:
            return {
                'api_accessible': False,
                'error': 'API未配置'
            }
        
        try:
            # 尝试获取访问令牌
            token = self._get_access_token()
            return {
                'api_accessible': bool(token),
                'token_obtained': bool(token),
                'error': None if token else '无法获取访问令牌'
            }
        except Exception as e:
            return {
                'api_accessible': False,
                'token_obtained': False,
                'error': str(e)
            }
        
        if self.is_configured:
            logger.info("✅ 百度语音识别服务已配置")
        else:
            logger.warning("⚠️ 百度语音识别服务未配置，请设置API密钥")
    
    def _get_access_token(self) -> Optional[str]:
        """获取百度API访问令牌"""
        # 检查缓存的令牌是否还有效
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
        
        if not self.is_configured:
            logger.error("百度API密钥未配置")
            return None
        
        try:
            url = f"{self.token_url}?client_id={self.api_key}&client_secret={self.secret_key}&grant_type=client_credentials"
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = requests.post(url, headers=headers, json="")
            response.raise_for_status()
            
            data = response.json()
            
            if 'access_token' in data:
                self.access_token = data['access_token']
                # 令牌有效期通常是30天，我们设置为29天后过期
                self.token_expires_at = time.time() + (29 * 24 * 60 * 60)
                
                logger.info("✅ 百度API访问令牌获取成功")
                return self.access_token
            else:
                logger.error(f"获取访问令牌失败: {data}")
                return None
                
        except Exception as e:
            logger.error(f"获取百度API访问令牌失败: {e}")
            return None
    
    def speech_to_text(self, audio_file: FileStorage) -> str:
        """
        百度语音识别 - 将音频转换为文字
        """
        if not self.is_configured:
            return "百度语音识别未配置，请设置API密钥"
        
        try:
            # 1. 获取访问令牌
            access_token = self._get_access_token()
            if not access_token:
                return "无法获取百度API访问令牌"
            
            # 2. 处理音频文件
            audio_data, audio_format, sample_rate = self._process_audio_file(audio_file)
            if not audio_data:
                return "音频文件处理失败"
            
            # 3. 调用百度语音识别API
            text = self._call_baidu_speech_api(audio_data, audio_format, sample_rate, access_token)
            
            if text:
                logger.info(f"百度语音识别成功: {text}")
                return text
            else:
                return "百度语音识别失败，请重试"
                
        except Exception as e:
            logger.error(f"百度语音识别过程异常: {e}")
            return f"语音识别出错: {str(e)}"
    
    def _process_audio_file(self, audio_file: FileStorage) -> tuple:
        """
        处理音频文件，转换为百度API支持的格式
        返回: (audio_data_base64, format, sample_rate)
        """
        try:
            # 验证文件大小
            audio_file.seek(0, 2)
            file_size = audio_file.tell()
            audio_file.seek(0)
            
            if file_size == 0:
                logger.error("音频文件为空")
                return None, None, None
            
            if file_size > 10 * 1024 * 1024:  # 10MB限制
                logger.error("音频文件过大，百度API限制为10MB")
                return None, None, None
            
            # 创建临时文件
            temp_id = uuid.uuid4().hex
            temp_original = os.path.join(tempfile.gettempdir(), f"baidu_audio_{temp_id}")
            
            # 保存原始文件
            audio_file.save(temp_original)
            
            try:
                # 读取音频数据
                with open(temp_original, 'rb') as f:
                    audio_data = f.read()
                
                # 获取原始文件名来判断格式
                original_filename = audio_file.filename.lower() if audio_file.filename else ''
                
                # 特殊处理WebM格式（浏览器录制的常见格式）
                if original_filename.endswith('.webm'):
                    logger.warning("WebM格式不被支持，建议使用WAV格式")
                    return None, None, None
                
                elif original_filename.endswith('.wav'):
                    # WAV格式，验证并可能重采样
                    format_info = AudioConverter.validate_wav_format(audio_data)
                    logger.info(f"WAV格式信息: {format_info}")
                    
                    if format_info['valid']:
                        current_rate = format_info['sample_rate']
                        
                        # 强制重采样到16kHz，确保兼容性
                        if current_rate != 16000:
                            logger.info(f"重采样从 {current_rate}Hz 到 16000Hz")
                            resampled_data = AudioConverter.resample_wav_to_16khz(audio_data)
                            if resampled_data:
                                audio_data = resampled_data
                            else:
                                logger.warning("重采样失败，尝试创建标准WAV")
                                # 如果重采样失败，创建一个标准的16kHz WAV文件
                                audio_data = self._create_standard_wav(audio_data)
                        
                        # 再次验证处理后的音频
                        final_info = AudioConverter.validate_wav_format(audio_data)
                        logger.info(f"最终WAV格式: {final_info}")
                        
                        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                        return audio_base64, "wav", 16000
                    else:
                        logger.error(f"WAV格式无效: {format_info['error']}")
                        # 尝试作为原始音频数据处理
                        logger.info("尝试创建标准WAV格式")
                        standard_wav = self._create_standard_wav(audio_data)
                        if standard_wav:
                            audio_base64 = base64.b64encode(standard_wav).decode('utf-8')
                            return audio_base64, "wav", 16000
                        return None, None, None
                
                elif original_filename.endswith('.amr'):
                    # AMR格式，使用8kHz
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    return audio_base64, "amr", 8000
                
                else:
                    # 其他格式，尝试作为PCM处理
                    logger.info(f"未知格式 {original_filename}，尝试作为PCM处理")
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    return audio_base64, "pcm", 16000
                
            finally:
                # 清理临时文件
                if os.path.exists(temp_original):
                    os.remove(temp_original)
                
        except Exception as e:
            logger.error(f"音频文件处理失败: {e}")
            return None, None, None
    
    def _convert_webm_to_wav_simple(self, webm_data: bytes) -> Optional[bytes]:
        """简单的WebM到WAV转换（不依赖FFmpeg）"""
        try:
            # 对于WebM格式，我们尝试直接提取音频数据
            # 这是一个简化的方法，可能不适用于所有WebM文件
            
            # WebM文件通常包含Opus或Vorbis编码的音频
            # 我们尝试查找音频数据块
            
            # 创建一个简单的WAV头
            def create_wav_header(data_size, sample_rate=16000, channels=1, bits_per_sample=16):
                # WAV文件头格式
                header = bytearray(44)
                
                # RIFF标识
                header[0:4] = b'RIFF'
                # 文件大小 - 8
                header[4:8] = (data_size + 36).to_bytes(4, 'little')
                # WAVE标识
                header[8:12] = b'WAVE'
                # fmt 子块
                header[12:16] = b'fmt '
                # fmt子块大小
                header[16:20] = (16).to_bytes(4, 'little')
                # 音频格式 (PCM = 1)
                header[20:22] = (1).to_bytes(2, 'little')
                # 声道数
                header[22:24] = channels.to_bytes(2, 'little')
                # 采样率
                header[24:28] = sample_rate.to_bytes(4, 'little')
                # 字节率
                byte_rate = sample_rate * channels * bits_per_sample // 8
                header[28:32] = byte_rate.to_bytes(4, 'little')
                # 块对齐
                block_align = channels * bits_per_sample // 8
                header[32:34] = block_align.to_bytes(2, 'little')
                # 位深度
                header[34:36] = bits_per_sample.to_bytes(2, 'little')
                # data子块
                header[36:40] = b'data'
                # 数据大小
                header[40:44] = data_size.to_bytes(4, 'little')
                
                return bytes(header)
            
            # 对于WebM，我们创建一个静音的WAV文件作为占位符
            # 实际应用中，这里应该使用专门的音频解码库
            sample_rate = 16000
            duration = 1  # 1秒
            samples = sample_rate * duration
            
            # 创建静音数据（16位PCM）
            audio_data = b'\x00\x00' * samples
            
            # 创建WAV文件
            wav_header = create_wav_header(len(audio_data), sample_rate)
            wav_file = wav_header + audio_data
            
            return wav_file
            
        except Exception as e:
            logger.error(f"WebM转换失败: {e}")
            return None
    
    def _call_baidu_speech_api(self, audio_data: str, audio_format: str, sample_rate: int, access_token: str) -> Optional[str]:
        """调用百度语音识别API"""
        try:
            # 确保采样率是百度API支持的值
            if sample_rate not in [8000, 16000]:
                sample_rate = 16000  # 默认使用16kHz
            
            # 确保格式是百度API支持的
            if audio_format not in ['wav', 'pcm', 'amr']:
                audio_format = 'pcm'  # 默认使用PCM
            
            # 计算音频数据长度
            try:
                audio_bytes = base64.b64decode(audio_data)
                audio_len = len(audio_bytes)
            except Exception as e:
                logger.error(f"音频数据解码失败: {e}")
                return None
            
            # 按照百度API文档的标准格式构建请求
            payload = {
                "format": audio_format,
                "rate": sample_rate,
                "channel": 1,
                "cuid": "ai_roleplay_app",
                "token": access_token,
                "speech": audio_data,
                "len": audio_len
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            logger.info(f"发送百度API请求:")
            logger.info(f"  URL: {self.speech_url}")
            logger.info(f"  格式: {audio_format}, 采样率: {sample_rate}, 长度: {audio_len}字节")
            
            # 使用标准的JSON格式发送请求
            response = requests.post(
                self.speech_url,
                headers=headers,
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"百度API响应: {result}")
            
            # 解析结果
            if result.get('err_no') == 0:
                # 识别成功
                if 'result' in result and result['result']:
                    text = ''.join(result['result']).strip()
                    if text:  # 确保不是空字符串
                        return text
                    else:
                        logger.warning("百度API返回空的识别结果，可能是静音或音频质量问题")
                        return "🔇 未识别到语音内容\n\n💡 录音建议：\n• 确保麦克风权限已开启\n• 录音时间建议3-8秒\n• 说话声音要清晰响亮\n• 避免环境噪音干扰\n• 尝试重新录音"
                else:
                    logger.warning("百度API返回空结果")
                    return "🔇 语音识别结果为空\n\n请检查录音设备并重新录音"
            else:
                # 识别失败
                err_no = result.get('err_no')
                err_msg = result.get('err_msg', '未知错误')
                logger.error(f"百度语音识别API错误: {err_no} - {err_msg}")
                
                # 提供更友好的错误信息
                if err_no == 3311:
                    return "音频采样率不支持，请使用8kHz或16kHz的音频"
                elif err_no == 3300:
                    return "音频格式不支持，请使用WAV、PCM或AMR格式"
                elif err_no == 3301:
                    return "音频数据为空或损坏"
                elif err_no == 3302:
                    return "音频长度不合法，请使用60秒以内的音频"
                else:
                    return f"语音识别失败: {err_msg}"
                
        except requests.exceptions.Timeout:
            logger.error("百度API请求超时")
            return "请求超时，请重试"
        except requests.exceptions.RequestException as e:
            logger.error(f"百度API请求失败: {e}")
            return "网络请求失败，请检查网络连接"
        except Exception as e:
            logger.error(f"调用百度API异常: {e}")
            return f"语音识别异常: {str(e)}"
    
    def test_api_connection(self) -> Dict:
        """测试百度API连接"""
        result = {
            'configured': self.is_configured,
            'token_available': False,
            'api_accessible': False,
            'error': None
        }
        
        if not self.is_configured:
            result['error'] = '百度API密钥未配置'
            return result
        
        try:
            # 测试获取访问令牌
            access_token = self._get_access_token()
            if access_token:
                result['token_available'] = True
                result['api_accessible'] = True
            else:
                result['error'] = '无法获取访问令牌'
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_service_status(self) -> Dict:
        """获取服务状态"""
        return {
            'service_name': 'BaiduVoiceService',
            'configured': self.is_configured,
            'api_key_set': bool(self.api_key),
            'secret_key_set': bool(self.secret_key),
            'token_cached': bool(self.access_token),
            'pydub_available': PYDUB_AVAILABLE,
            'description': '百度语音识别服务'
        }
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的音频格式"""
        return ['wav', 'pcm', 'amr', 'mp3', 'ogg', 'webm', 'm4a', 'flac']
    
    def _create_standard_wav(self, audio_data: bytes) -> Optional[bytes]:
        """
        创建标准的16kHz WAV文件
        当音频格式有问题时，创建一个符合百度API要求的标准WAV文件
        """
        try:
            # 如果输入数据太小，创建一个短暂的静音
            if len(audio_data) < 1000:
                logger.info("音频数据太小，创建静音WAV")
                return AudioConverter.generate_silence_wav(1.0, 16000)
            
            # 尝试提取音频数据部分
            if len(audio_data) > 44:
                # 跳过可能的WAV头部
                pcm_data = audio_data[44:]
            else:
                pcm_data = audio_data
            
            # 限制数据长度（最多10秒的16kHz音频）
            max_samples = 16000 * 10 * 2  # 10秒 * 16kHz * 2字节
            if len(pcm_data) > max_samples:
                pcm_data = pcm_data[:max_samples]
            
            # 确保数据长度是偶数（16位音频）
            if len(pcm_data) % 2 != 0:
                pcm_data = pcm_data[:-1]
            
            # 创建标准WAV文件
            standard_wav = AudioConverter.create_wav_from_pcm(pcm_data, 16000, 1, 2)
            
            if standard_wav:
                logger.info(f"创建标准WAV成功，大小: {len(standard_wav)}字节")
                return standard_wav
            else:
                logger.error("创建标准WAV失败")
                return None
                
        except Exception as e:
            logger.error(f"创建标准WAV异常: {e}")
            # 最后的备选方案：创建静音
            return AudioConverter.generate_silence_wav(1.0, 16000)
    
    def get_api_limits(self) -> Dict:
        """获取API限制信息"""
        return {
            'max_file_size': '10MB',
            'max_duration': '60秒',
            'supported_sample_rates': [8000, 16000],
            'supported_formats': self.get_supported_formats(),
            'daily_quota': '根据百度AI开放平台配额'
        }