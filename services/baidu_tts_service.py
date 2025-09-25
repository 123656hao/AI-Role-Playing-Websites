#!/usr/bin/env python3
"""
百度语音合成服务
使用百度AI开放平台的语音合成API
"""

import os
import requests
import json
import base64
import tempfile
import uuid
import logging
import time
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class BaiduTTSService:
    """百度语音合成服务"""
    
    def __init__(self):
        self.audio_dir = "static/audio"
        os.makedirs(self.audio_dir, exist_ok=True)
        
        # 从环境变量获取API配置
        self.api_key = os.getenv('BAIDU_API_KEY')
        self.secret_key = os.getenv('BAIDU_SECRET_KEY')
        
        # API URLs
        self.token_url = "https://aip.baidubce.com/oauth/2.0/token"
        self.tts_url = "https://tsn.baidu.com/text2audio"
        
        # 访问令牌缓存
        self.access_token = None
        self.token_expires_at = 0
        
        # 检查配置
        self.is_configured = bool(self.api_key and self.secret_key)
        
        if self.is_configured:
            logger.info("✅ 百度语音合成服务已配置")
        else:
            logger.warning("⚠️ 百度语音合成服务未配置，请设置API密钥")
    
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
                logger.info("百度TTS API访问令牌获取成功")
                return self.access_token
            else:
                logger.error(f"获取TTS访问令牌失败: {data}")
                return None
                
        except Exception as e:
            logger.error(f"获取百度TTS API访问令牌失败: {e}")
            return None
    
    def text_to_speech(self, text: str, character: Optional[Dict] = None) -> Optional[str]:
        """文字转语音"""
        if not self.is_configured:
            logger.warning("百度语音合成服务未配置")
            return {
                'success': False,
                'error': '百度语音合成服务未配置'
            }
        
        if not text or len(text.strip()) == 0:
            logger.warning("文本为空，跳过语音合成")
            return {
                'success': False,
                'error': '文本为空'
            }
        
        # 获取访问令牌
        access_token = self._get_access_token()
        if not access_token:
            logger.error("无法获取百度TTS API访问令牌")
            return {
                'success': False,
                'error': '无法获取百度TTS API访问令牌'
            }
        
        try:
            # 选择语音参数
            voice_params = self._get_voice_params(character)
            
            # 构建请求参数
            params = {
                'tex': text[:1024],  # 百度TTS限制1024字符
                'tok': access_token,
                'cuid': str(uuid.uuid4()),
                'ctp': 1,  # 客户端类型
                'lan': 'zh',  # 语言
                **voice_params
            }
            
            # 发送请求
            response = requests.post(
                self.tts_url,
                data=params,
                timeout=30
            )
            
            response.raise_for_status()
            
            # 检查响应类型
            content_type = response.headers.get('Content-Type', '')
            
            if 'audio' in content_type:
                # 成功获取音频数据
                audio_filename = f"tts_{uuid.uuid4().hex[:8]}.mp3"
                audio_path = os.path.join(self.audio_dir, audio_filename)
                
                # 保存音频文件
                with open(audio_path, 'wb') as f:
                    f.write(response.content)
                
                # 返回标准化的结果
                audio_url = f"/static/audio/{audio_filename}"
                logger.info(f"语音合成成功: {audio_url}")
                return {
                    'success': True,
                    'audio_path': audio_path,
                    'audio_url': audio_url
                }
                
            else:
                # 可能是错误响应
                try:
                    error_data = response.json()
                    error_msg = error_data.get('err_msg', '未知错误')
                    logger.error(f"百度TTS API错误: {error_data.get('err_no')} - {error_msg}")
                except:
                    logger.error(f"百度TTS API响应异常: {response.text[:200]}")
                return {
                    'success': False,
                    'error': '百度TTS API响应异常'
                }
                
        except Exception as e:
            logger.error(f"语音合成处理失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_voice_params(self, character: Optional[Dict] = None) -> Dict[str, Any]:
        """根据角色获取语音参数"""
        # 默认语音参数
        params = {
            'spd': 5,  # 语速 0-15
            'pit': 5,  # 音调 0-15
            'vol': 5,  # 音量 0-15
            'per': 0   # 发音人 0-女声，1-男声，3-情感合成-度逍遥，4-情感合成-度丫丫
        }
        
        if character:
            # 根据角色性别和特点调整语音参数
            gender = character.get('gender', 'female')
            personality = character.get('personality', '')
            
            if gender == 'male':
                params['per'] = 1  # 男声
            elif '活泼' in personality or '开朗' in personality:
                params['per'] = 4  # 度丫丫（活泼女声）
                params['spd'] = 6  # 稍快语速
            elif '优雅' in personality or '温柔' in personality:
                params['per'] = 0  # 标准女声
                params['spd'] = 4  # 稍慢语速
                params['pit'] = 6  # 稍高音调
            else:
                params['per'] = 0  # 默认女声
        
        return params
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            'configured': self.is_configured,
            'api_key_set': bool(self.api_key),
            'secret_key_set': bool(self.secret_key),
            'token_valid': bool(self.access_token and time.time() < self.token_expires_at)
        }
    
    def test_tts_service(self) -> Dict[str, Any]:
        """测试TTS服务"""
        if not self.is_configured:
            return {
                'service_available': False,
                'error': 'TTS服务未配置'
            }
        
        try:
            # 尝试获取访问令牌
            token = self._get_access_token()
            if not token:
                return {
                    'service_available': False,
                    'error': '无法获取访问令牌'
                }
            
            # 尝试合成一个简短的测试文本
            test_result = self.text_to_speech("测试", None)
            
            return {
                'service_available': bool(test_result),
                'token_obtained': True,
                'test_synthesis': bool(test_result),
                'error': None if test_result else '测试合成失败'
            }
            
        except Exception as e:
            return {
                'service_available': False,
                'token_obtained': False,
                'test_synthesis': False,
                'error': str(e)
            }
    
    def get_supported_voices(self) -> List[Dict[str, Any]]:
        """获取支持的语音列表"""
        return [
            {'id': 0, 'name': '度小美', 'gender': 'female', 'description': '标准女声'},
            {'id': 1, 'name': '度小宇', 'gender': 'male', 'description': '标准男声'},
            {'id': 3, 'name': '度逍遥', 'gender': 'male', 'description': '情感合成男声'},
            {'id': 4, 'name': '度丫丫', 'gender': 'female', 'description': '情感合成女声'}
        ]
        
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
                
                logger.info("✅ 百度TTS访问令牌获取成功")
                return self.access_token
            else:
                logger.error(f"获取访问令牌失败: {data}")
                return None
                
        except Exception as e:
            logger.error(f"获取百度TTS访问令牌失败: {e}")
            return None
    
    def text_to_speech(self, text: str, character: Dict = None) -> Optional[str]:
        """
        百度语音合成 - 将文字转换为语音
        
        Args:
            text: 要合成的文字
            character: 角色信息（用于选择合适的语音）
        
        Returns:
            音频文件的URL路径，如果失败返回None
        """
        if not self.is_configured:
            logger.error("百度语音合成未配置")
            return None
        
        if not text or not text.strip():
            logger.error("合成文本为空")
            return None
        
        try:
            # 1. 获取访问令牌
            access_token = self._get_access_token()
            if not access_token:
                logger.error("无法获取百度TTS访问令牌")
                return None
            
            # 2. 选择合适的语音
            voice_params = self._get_voice_params(character)
            
            # 3. 调用百度语音合成API
            audio_data = self._call_baidu_tts_api(text, voice_params, access_token)
            
            if audio_data:
                # 4. 保存音频文件
                audio_url = self._save_audio_file(audio_data)
                logger.info(f"语音合成成功: {audio_url}")
                return audio_url
            else:
                logger.error("百度语音合成失败")
                return None
                
        except Exception as e:
            logger.error(f"语音合成过程异常: {e}")
            return None
    
    def _get_voice_params(self, character: Dict = None) -> Dict:
        """
        根据角色选择合适的语音参数
        
        Args:
            character: 角色信息
        
        Returns:
            语音参数字典
        """
        # 默认参数
        params = {
            'per': 0,    # 发音人选择，0为女声，1为男声，3为情感合成-度逍遥，4为情感合成-度丫丫
            'spd': 5,    # 语速，取值0-15，默认为5中语速
            'pit': 5,    # 音调，取值0-15，默认为5中音调
            'vol': 5,    # 音量，取值0-15，默认为5中音量
            'aue': 3     # 音频编码，3为mp3格式，4为pcm-16k，5为pcm-8k，6为wav
        }
        
        if character:
            character_name = character.get('name', '').lower()
            
            # 根据角色名称选择合适的语音
            if any(name in character_name for name in ['苏格拉底', '孔子', '爱因斯坦']):
                # 哲学家和科学家使用男声
                params['per'] = 1  # 男声
                params['spd'] = 4  # 稍慢的语速
                params['pit'] = 4  # 稍低的音调
            elif any(name in character_name for name in ['玛丽', '居里', '李老师']):
                # 女性角色使用女声
                params['per'] = 0  # 女声
                params['spd'] = 5  # 正常语速
                params['pit'] = 6  # 稍高的音调
            elif '哈利' in character_name:
                # 年轻角色使用活泼的声音
                params['per'] = 4  # 度丫丫（活泼女声）
                params['spd'] = 6  # 稍快的语速
                params['pit'] = 6  # 较高的音调
            elif '莎士比亚' in character_name:
                # 文学家使用富有感情的声音
                params['per'] = 3  # 度逍遥（情感男声）
                params['spd'] = 4  # 稍慢的语速
                params['pit'] = 5  # 中等音调
        
        return params
    
    def _call_baidu_tts_api(self, text: str, voice_params: Dict, access_token: str) -> Optional[bytes]:
        """调用百度语音合成API"""
        try:
            # 构建请求参数
            params = {
                'tok': access_token,
                'tex': text,
                'per': voice_params['per'],
                'spd': voice_params['spd'],
                'pit': voice_params['pit'],
                'vol': voice_params['vol'],
                'aue': voice_params['aue'],
                'cuid': 'ai_roleplay_tts',
                'lan': 'zh',  # 语言选择，zh为中文
                'ctp': 1      # 客户端类型选择，web端填写固定值1
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': '*/*'
            }
            
            logger.info(f"发送百度TTS请求: 文本长度={len(text)}, 发音人={voice_params['per']}")
            
            # 发送请求
            response = requests.post(
                self.tts_url,
                data=params,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            
            # 检查响应内容类型
            content_type = response.headers.get('Content-Type', '')
            
            if 'audio' in content_type:
                # 成功返回音频数据
                logger.info("百度TTS合成成功")
                return response.content
            else:
                # 返回错误信息
                try:
                    error_info = response.json()
                    logger.error(f"百度TTS API错误: {error_info}")
                except:
                    logger.error(f"百度TTS API错误: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("百度TTS API请求超时")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"百度TTS API请求失败: {e}")
            return None
        except Exception as e:
            logger.error(f"调用百度TTS API异常: {e}")
            return None
    
    def _save_audio_file(self, audio_data: bytes) -> str:
        """保存音频文件并返回URL"""
        try:
            # 生成唯一的文件名
            file_id = uuid.uuid4().hex
            filename = f"tts_{file_id}.mp3"
            file_path = os.path.join(self.audio_dir, filename)
            
            # 保存音频文件
            with open(file_path, 'wb') as f:
                f.write(audio_data)
            
            # 返回相对URL路径
            audio_url = f"/static/audio/{filename}"
            logger.info(f"音频文件已保存: {file_path}")
            
            return audio_url
            
        except Exception as e:
            logger.error(f"保存音频文件失败: {e}")
            return None
    
    def test_tts_service(self) -> Dict:
        """测试语音合成服务"""
        result = {
            'configured': self.is_configured,
            'token_available': False,
            'tts_working': False,
            'error': None
        }
        
        if not self.is_configured:
            result['error'] = '百度TTS API密钥未配置'
            return result
        
        try:
            # 测试获取访问令牌
            access_token = self._get_access_token()
            if access_token:
                result['token_available'] = True
                
                # 测试语音合成
                test_text = "你好，这是语音合成测试。"
                audio_url = self.text_to_speech(test_text)
                
                if audio_url:
                    result['tts_working'] = True
                else:
                    result['error'] = '语音合成测试失败'
            else:
                result['error'] = '无法获取访问令牌'
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_service_status(self) -> Dict:
        """获取服务状态"""
        return {
            'service_name': 'BaiduTTSService',
            'configured': self.is_configured,
            'api_key_set': bool(self.api_key),
            'secret_key_set': bool(self.secret_key),
            'token_cached': bool(self.access_token),
            'audio_dir': self.audio_dir,
            'description': '百度语音合成服务'
        }
    
    def get_supported_voices(self) -> Dict:
        """获取支持的语音列表"""
        return {
            0: {'name': '度小美', 'gender': 'female', 'description': '标准女声'},
            1: {'name': '度小宇', 'gender': 'male', 'description': '标准男声'},
            3: {'name': '度逍遥', 'gender': 'male', 'description': '情感男声'},
            4: {'name': '度丫丫', 'gender': 'female', 'description': '情感女声'}
        }
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """清理旧的音频文件"""
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            cleaned_count = 0
            
            for filename in os.listdir(self.audio_dir):
                if filename.startswith('tts_') and filename.endswith('.mp3'):
                    file_path = os.path.join(self.audio_dir, filename)
                    file_age = current_time - os.path.getctime(file_path)
                    
                    if file_age > max_age_seconds:
                        os.remove(file_path)
                        cleaned_count += 1
            
            logger.info(f"清理了 {cleaned_count} 个旧音频文件")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"清理音频文件失败: {e}")
            return 0