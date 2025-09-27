#!/usr/bin/env python3
"""
实时语音处理器
支持连续语音识别和实时对话
"""

import json
import asyncio
import logging
import time
import uuid
import base64
import tempfile
import os
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from threading import Thread, Event
import queue

logger = logging.getLogger(__name__)

class RealtimeVoiceHandler:
    """实时语音处理器"""
    
    def __init__(self, voice_service, ai_service, tts_service):
        self.voice_service = voice_service
        self.ai_service = ai_service
        self.tts_service = tts_service
        
        # 活跃会话
        self.active_sessions = {}
        
        # 音频处理队列
        self.audio_queue = queue.Queue()
        self.processing_thread = None
        self.stop_event = Event()
        
        # 启动音频处理线程
        self.start_processing_thread()
    
    def start_processing_thread(self):
        """启动音频处理线程"""
        if self.processing_thread is None or not self.processing_thread.is_alive():
            self.stop_event.clear()
            self.processing_thread = Thread(target=self._audio_processing_worker, daemon=True)
            self.processing_thread.start()
            logger.info("音频处理线程已启动")
    
    def stop_processing_thread(self):
        """停止音频处理线程"""
        self.stop_event.set()
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=5)
            logger.info("音频处理线程已停止")
    
    def _audio_processing_worker(self):
        """音频处理工作线程"""
        while not self.stop_event.is_set():
            try:
                # 从队列获取音频处理任务
                task = self.audio_queue.get(timeout=1)
                if task is None:
                    continue
                
                session_id = task['session_id']
                audio_data = task['audio_data']
                callback = task['callback']
                
                # 处理音频
                result = self._process_audio_chunk(session_id, audio_data)
                
                # 回调结果
                if callback:
                    callback(result)
                
                self.audio_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"音频处理线程异常: {e}")
    
    def create_session(self, character_id: str, character: Dict, callback: Callable) -> str:
        """创建实时语音会话"""
        session_id = str(uuid.uuid4())
        
        session = {
            'session_id': session_id,
            'character_id': character_id,
            'character': character,
            'callback': callback,
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'conversation_history': [],
            'audio_buffer': b'',
            'is_active': True,
            'continuous_mode': False,
            'silence_detection': True,
            'auto_response': True
        }
        
        self.active_sessions[session_id] = session
        logger.info(f"创建实时语音会话: {session_id} for {character['name']}")
        
        return session_id
    
    def update_session_config(self, session_id: str, config: Dict):
        """更新会话配置"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.update(config)
            session['last_activity'] = datetime.now()
            logger.info(f"更新会话配置: {session_id}")
    
    def process_audio_stream(self, session_id: str, audio_data: bytes, callback: Callable = None):
        """处理音频流数据"""
        if session_id not in self.active_sessions:
            logger.error(f"会话不存在: {session_id}")
            return
        
        session = self.active_sessions[session_id]
        session['last_activity'] = datetime.now()
        
        # 将音频处理任务加入队列
        task = {
            'session_id': session_id,
            'audio_data': audio_data,
            'callback': callback or session['callback']
        }
        
        try:
            self.audio_queue.put(task, timeout=1)
        except queue.Full:
            logger.warning(f"音频处理队列已满，丢弃音频数据: {session_id}")
    
    def _process_audio_chunk(self, session_id: str, audio_data: bytes) -> Dict:
        """处理音频块 - 直接处理完整的音频文件"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return {'error': '会话不存在'}
            
            # 直接处理音频数据，不进行累积
            # 假设audio_data是完整的音频文件数据（WebM或WAV格式）
            return self._recognize_speech_from_data(session_id, audio_data)
            
        except Exception as e:
            logger.error(f"处理音频块失败: {e}")
            return {'error': str(e)}
    
    def _detect_silence(self, audio_data: bytes) -> bool:
        """检测静音"""
        try:
            # 简单的静音检测：检查最后1秒的音频
            if len(audio_data) < 32000:  # 少于1秒
                return False
            
            # 取最后1秒的音频数据
            last_second = audio_data[-32000:]
            
            # 计算音频能量
            energy = 0
            for i in range(0, len(last_second), 2):
                if i + 1 < len(last_second):
                    sample = int.from_bytes(last_second[i:i+2], 'little', signed=True)
                    energy += sample * sample
            
            # 平均能量
            avg_energy = energy / (len(last_second) // 2)
            
            # 静音阈值
            silence_threshold = 1000000  # 可调整
            
            return avg_energy < silence_threshold
            
        except Exception as e:
            logger.error(f"静音检测失败: {e}")
            return False
    
    def _recognize_speech_from_data(self, session_id: str, audio_data: bytes) -> Dict:
        """从音频数据直接进行语音识别"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return {'error': '会话不存在'}
            
            if len(audio_data) == 0:
                return {'error': '音频数据为空'}
            
            # 创建临时文件保存音频数据
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file.flush()
                
                try:
                    # 使用与标准语音聊天相同的方式创建FileStorage对象
                    from werkzeug.datastructures import FileStorage
                    from io import BytesIO
                    
                    # 创建FileStorage对象（与标准语音聊天相同的方式）
                    file_storage = FileStorage(
                        stream=BytesIO(audio_data),
                        filename='recording.webm',
                        content_type='audio/webm'
                    )
                    
                    # 语音识别
                    recognized_text = self.voice_service.speech_to_text(file_storage)
                    
                    if recognized_text and not recognized_text.startswith('语音识别') and not recognized_text.startswith('百度'):
                        # 识别成功，生成AI回复
                        ai_response = self._generate_ai_response(session, recognized_text)
                        
                        return {
                            'type': 'speech_recognized',
                            'text': recognized_text,
                            'ai_response': ai_response,
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        return {
                            'type': 'recognition_failed',
                            'error': recognized_text or '语音识别失败',
                            'timestamp': datetime.now().isoformat()
                        }
                
                finally:
                    # 清理临时文件
                    try:
                        os.unlink(temp_file.name)
                    except:
                        pass
            
        except Exception as e:
            logger.error(f"语音识别失败: {e}")
            return {'error': str(e)}

    def _recognize_speech(self, session_id: str) -> Dict:
        """执行语音识别"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return {'error': '会话不存在'}
            
            audio_buffer = session['audio_buffer']
            if len(audio_buffer) == 0:
                return {'error': '音频缓冲区为空'}
            
            # 清空缓冲区
            session['audio_buffer'] = b''
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                # 创建WAV文件
                wav_data = self._create_wav_from_pcm(audio_buffer)
                temp_file.write(wav_data)
                temp_file.flush()
                
                try:
                    # 使用与标准语音聊天相同的方式创建FileStorage对象
                    from werkzeug.datastructures import FileStorage
                    from io import BytesIO
                    
                    # 读取临时文件内容
                    with open(temp_file.name, 'rb') as f:
                        file_content = f.read()
                    
                    # 创建FileStorage对象（与标准语音聊天相同的方式）
                    file_storage = FileStorage(
                        stream=BytesIO(file_content),
                        filename='recording.wav',
                        content_type='audio/wav'
                    )
                    
                    # 语音识别
                    recognized_text = self.voice_service.speech_to_text(file_storage)
                    
                    if recognized_text and not recognized_text.startswith('语音识别'):
                        # 识别成功，生成AI回复
                        ai_response = self._generate_ai_response(session, recognized_text)
                        
                        return {
                            'type': 'speech_recognized',
                            'text': recognized_text,
                            'ai_response': ai_response,
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        return {
                            'type': 'recognition_failed',
                            'error': recognized_text or '语音识别失败',
                            'timestamp': datetime.now().isoformat()
                        }
                
                finally:
                    # 清理临时文件
                    try:
                        os.unlink(temp_file.name)
                    except:
                        pass
            
        except Exception as e:
            logger.error(f"语音识别失败: {e}")
            return {'error': str(e)}
    
    def _create_wav_from_pcm(self, pcm_data: bytes, sample_rate: int = 16000) -> bytes:
        """从PCM数据创建WAV文件"""
        try:
            # WAV文件头
            wav_header = bytearray(44)
            
            # RIFF标识
            wav_header[0:4] = b'RIFF'
            # 文件大小
            file_size = len(pcm_data) + 36
            wav_header[4:8] = file_size.to_bytes(4, 'little')
            # WAVE标识
            wav_header[8:12] = b'WAVE'
            # fmt子块
            wav_header[12:16] = b'fmt '
            # fmt子块大小
            wav_header[16:20] = (16).to_bytes(4, 'little')
            # 音频格式 (PCM = 1)
            wav_header[20:22] = (1).to_bytes(2, 'little')
            # 声道数
            wav_header[22:24] = (1).to_bytes(2, 'little')
            # 采样率
            wav_header[24:28] = sample_rate.to_bytes(4, 'little')
            # 字节率
            byte_rate = sample_rate * 1 * 2
            wav_header[28:32] = byte_rate.to_bytes(4, 'little')
            # 块对齐
            wav_header[32:34] = (2).to_bytes(2, 'little')
            # 位深度
            wav_header[34:36] = (16).to_bytes(2, 'little')
            # data子块
            wav_header[36:40] = b'data'
            # 数据大小
            wav_header[40:44] = len(pcm_data).to_bytes(4, 'little')
            
            return bytes(wav_header) + pcm_data
            
        except Exception as e:
            logger.error(f"创建WAV文件失败: {e}")
            raise
    
    def _generate_ai_response(self, session: Dict, user_text: str) -> Optional[Dict]:
        """生成AI回复"""
        try:
            character = session['character']
            
            # 生成文字回复
            ai_text = self.ai_service.generate_response(
                character, 
                user_text, 
                session['session_id']
            )
            
            # 记录对话历史
            session['conversation_history'].append({
                'user': user_text,
                'ai': ai_text,
                'timestamp': datetime.now().isoformat()
            })
            
            # 生成语音回复
            audio_url = None
            if session.get('auto_response', True):
                try:
                    tts_result = self.tts_service.text_to_speech(ai_text, character)
                    if tts_result and tts_result.get('success'):
                        audio_url = tts_result.get('audio_url')
                except Exception as e:
                    logger.warning(f"语音合成失败: {e}")
            
            return {
                'text': ai_text,
                'audio_url': audio_url,
                'character': character,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"生成AI回复失败: {e}")
            return None
    
    def end_session(self, session_id: str):
        """结束会话"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session['is_active'] = False
            del self.active_sessions[session_id]
            logger.info(f"结束实时语音会话: {session_id}")
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """获取会话信息"""
        session = self.active_sessions.get(session_id)
        if session:
            return {
                'session_id': session_id,
                'character': session['character'],
                'created_at': session['created_at'].isoformat(),
                'last_activity': session['last_activity'].isoformat(),
                'conversation_count': len(session['conversation_history']),
                'is_active': session['is_active']
            }
        return None
    
    def cleanup_inactive_sessions(self, max_idle_minutes: int = 30):
        """清理不活跃的会话"""
        current_time = datetime.now()
        inactive_sessions = []
        
        for session_id, session in self.active_sessions.items():
            idle_time = (current_time - session['last_activity']).total_seconds() / 60
            if idle_time > max_idle_minutes:
                inactive_sessions.append(session_id)
        
        for session_id in inactive_sessions:
            self.end_session(session_id)
            logger.info(f"清理不活跃会话: {session_id}")
        
        return len(inactive_sessions)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            'active_sessions': len(self.active_sessions),
            'queue_size': self.audio_queue.qsize(),
            'processing_thread_alive': self.processing_thread.is_alive() if self.processing_thread else False,
            'sessions': [
                {
                    'session_id': sid,
                    'character': session['character']['name'],
                    'created_at': session['created_at'].isoformat(),
                    'conversation_count': len(session['conversation_history'])
                }
                for sid, session in self.active_sessions.items()
            ]
        }
    
    def __del__(self):
        """析构函数"""
        self.stop_processing_thread()