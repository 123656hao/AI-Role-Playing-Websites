"""
WebSocket处理器 - 处理实时语音通信
"""

import json
import asyncio
import websockets
import logging
from typing import Dict, Any, Set, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class WebSocketHandler:
    def __init__(self, voice_service, ai_service):
        self.voice_service = voice_service
        self.ai_service = ai_service
        self.connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.sessions: Dict[str, Dict] = {}
        
    async def handle_connection(self, websocket, path):
        """处理WebSocket连接"""
        connection_id = str(uuid.uuid4())
        self.connections[connection_id] = websocket
        
        print(f"🔌 新的WebSocket连接: {connection_id}")
        
        try:
            await self.send_message(websocket, {
                'type': 'connection_established',
                'connection_id': connection_id,
                'timestamp': datetime.now().isoformat()
            })
            
            async for message in websocket:
                await self.handle_message(connection_id, websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            print(f"🔌 WebSocket连接关闭: {connection_id}")
        except Exception as e:
            logger.error(f"WebSocket连接错误: {e}")
        finally:
            await self.cleanup_connection(connection_id)
    
    async def handle_message(self, connection_id: str, websocket, message: str):
        """处理WebSocket消息"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            print(f"📨 收到消息类型: {message_type} from {connection_id}")
            
            if message_type == 'start_voice_session':
                await self.handle_start_voice_session(connection_id, websocket, data)
            elif message_type == 'audio_data':
                await self.handle_audio_data(connection_id, websocket, data)
            elif message_type == 'stop_voice_session':
                await self.handle_stop_voice_session(connection_id, websocket, data)
            elif message_type == 'text_message':
                await self.handle_text_message(connection_id, websocket, data)
            elif message_type == 'ping':
                await self.handle_ping(connection_id, websocket, data)
            else:
                await self.send_error(websocket, f"未知消息类型: {message_type}")
                
        except json.JSONDecodeError:
            await self.send_error(websocket, "无效的JSON格式")
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            await self.send_error(websocket, f"处理消息失败: {str(e)}")
    
    async def handle_start_voice_session(self, connection_id: str, websocket, data: Dict):
        """处理开始语音会话"""
        try:
            character_id = data.get('character_id')
            session_config = data.get('config', {})
            
            if not character_id:
                await self.send_error(websocket, "缺少character_id")
                return
            
            # 创建语音会话
            session_id = str(uuid.uuid4())
            
            # 获取角色信息
            from services.character_service import CharacterService
            character_service = CharacterService()
            character = character_service.get_character_by_id(character_id)
            
            if not character:
                await self.send_error(websocket, f"角色不存在: {character_id}")
                return
            
            # 启动实时语音会话
            voice_session = await self.voice_service.start_realtime_voice_session(
                session_id, 
                character,
                self.create_message_callback(connection_id, websocket)
            )
            
            # 保存会话信息
            self.sessions[connection_id] = {
                'session_id': session_id,
                'character_id': character_id,
                'character': character,
                'voice_session': voice_session,
                'created_at': datetime.now()
            }
            
            await self.send_message(websocket, {
                'type': 'voice_session_started',
                'session_id': session_id,
                'character': character,
                'config': voice_session.get('config', {}),
                'timestamp': datetime.now().isoformat()
            })
            
            print(f"🎤 语音会话已启动: {session_id} for {character['name']}")
            
        except Exception as e:
            logger.error(f"启动语音会话失败: {e}")
            await self.send_error(websocket, f"启动语音会话失败: {str(e)}")
    
    async def handle_audio_data(self, connection_id: str, websocket, data: Dict):
        """处理音频数据"""
        try:
            if connection_id not in self.sessions:
                await self.send_error(websocket, "没有活跃的语音会话")
                return
            
            session = self.sessions[connection_id]
            session_id = session['session_id']
            
            # 获取音频数据
            audio_base64 = data.get('audio_data')
            if not audio_base64:
                await self.send_error(websocket, "缺少音频数据")
                return
            
            # 解码音频数据
            import base64
            audio_bytes = base64.b64decode(audio_base64)
            
            # 处理音频数据
            result = self.voice_service.process_realtime_audio(session_id, audio_bytes)
            
            if 'error' in result:
                await self.send_error(websocket, result['error'])
            else:
                # 如果识别到文字，生成AI回复
                if result.get('type') == 'speech_recognized':
                    text = result.get('text', '')
                    if text.strip():
                        await self.process_user_speech(connection_id, websocket, text)
                
                # 发送处理结果
                await self.send_message(websocket, {
                    'type': 'audio_processed',
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                })
            
        except Exception as e:
            logger.error(f"处理音频数据失败: {e}")
            await self.send_error(websocket, f"处理音频数据失败: {str(e)}")
    
    async def process_user_speech(self, connection_id: str, websocket, text: str):
        """处理用户语音识别结果，生成AI回复"""
        try:
            session = self.sessions[connection_id]
            character = session['character']
            
            # 生成AI回复
            ai_response = self.ai_service.generate_response(
                character, 
                text, 
                session['session_id']
            )
            
            # 发送文字回复
            await self.send_message(websocket, {
                'type': 'ai_text_response',
                'text': ai_response,
                'character': character['name'],
                'timestamp': datetime.now().isoformat()
            })
            
            # 生成语音回复
            try:
                audio_url = self.voice_service.text_to_speech(ai_response, character)
                await self.send_message(websocket, {
                    'type': 'ai_voice_response',
                    'audio_url': audio_url,
                    'text': ai_response,
                    'character': character['name'],
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"语音合成失败: {e}")
                # 即使语音合成失败，也要发送文字回复
            
        except Exception as e:
            logger.error(f"处理用户语音失败: {e}")
            await self.send_error(websocket, f"处理语音失败: {str(e)}")
    
    async def handle_text_message(self, connection_id: str, websocket, data: Dict):
        """处理文字消息"""
        try:
            if connection_id not in self.sessions:
                await self.send_error(websocket, "没有活跃的会话")
                return
            
            session = self.sessions[connection_id]
            character = session['character']
            message = data.get('message', '').strip()
            
            if not message:
                await self.send_error(websocket, "消息不能为空")
                return
            
            # 生成AI回复
            ai_response = self.ai_service.generate_response(
                character, 
                message, 
                session['session_id']
            )
            
            # 发送回复
            await self.send_message(websocket, {
                'type': 'ai_text_response',
                'text': ai_response,
                'character': character['name'],
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"处理文字消息失败: {e}")
            await self.send_error(websocket, f"处理文字消息失败: {str(e)}")
    
    async def handle_stop_voice_session(self, connection_id: str, websocket, data: Dict):
        """处理停止语音会话"""
        try:
            if connection_id in self.sessions:
                session = self.sessions[connection_id]
                session_id = session['session_id']
                
                # 停止语音会话
                self.voice_service.stop_realtime_voice_session(session_id)
                
                # 删除会话
                del self.sessions[connection_id]
                
                await self.send_message(websocket, {
                    'type': 'voice_session_stopped',
                    'session_id': session_id,
                    'timestamp': datetime.now().isoformat()
                })
                
                print(f"🛑 语音会话已停止: {session_id}")
            else:
                await self.send_error(websocket, "没有活跃的语音会话")
                
        except Exception as e:
            logger.error(f"停止语音会话失败: {e}")
            await self.send_error(websocket, f"停止语音会话失败: {str(e)}")
    
    async def handle_ping(self, connection_id: str, websocket, data: Dict):
        """处理ping消息"""
        await self.send_message(websocket, {
            'type': 'pong',
            'timestamp': datetime.now().isoformat()
        })
    
    async def send_message(self, websocket, message: Dict):
        """发送消息到WebSocket"""
        try:
            await websocket.send(json.dumps(message, ensure_ascii=False))
        except Exception as e:
            logger.error(f"发送WebSocket消息失败: {e}")
    
    async def send_error(self, websocket, error_message: str):
        """发送错误消息"""
        await self.send_message(websocket, {
            'type': 'error',
            'message': error_message,
            'timestamp': datetime.now().isoformat()
        })
    
    def create_message_callback(self, connection_id: str, websocket):
        """创建消息回调函数"""
        async def callback(message_type: str, data: Dict):
            await self.send_message(websocket, {
                'type': message_type,
                'data': data,
                'timestamp': datetime.now().isoformat()
            })
        return callback
    
    async def cleanup_connection(self, connection_id: str):
        """清理连接"""
        try:
            # 删除连接
            if connection_id in self.connections:
                del self.connections[connection_id]
            
            # 停止相关会话
            if connection_id in self.sessions:
                session = self.sessions[connection_id]
                session_id = session['session_id']
                self.voice_service.stop_realtime_voice_session(session_id)
                del self.sessions[connection_id]
                print(f"🧹 清理连接和会话: {connection_id}")
                
        except Exception as e:
            logger.error(f"清理连接失败: {e}")
    
    def get_connection_stats(self) -> Dict:
        """获取连接统计信息"""
        return {
            'total_connections': len(self.connections),
            'active_sessions': len(self.sessions),
            'sessions': [
                {
                    'connection_id': conn_id,
                    'session_id': session['session_id'],
                    'character': session['character']['name'],
                    'created_at': session['created_at'].isoformat()
                }
                for conn_id, session in self.sessions.items()
            ]
        }