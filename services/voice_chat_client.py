"""
语音聊天客户端 - 与字节跳动语音API交互
"""

import asyncio
import websockets
import json
import threading
import queue
from typing import Optional, Callable
from .voice_config_service import VoiceConfigService

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("警告: pyaudio未安装，音频功能将不可用")


class VoiceChatClient:
    def __init__(self, character_id: str, voice_type: str = "female"):
        self.voice_service = VoiceConfigService()
        self.character_id = character_id
        self.voice_type = voice_type
        
        # 获取配置
        self.config = self.voice_service.create_character_voice_config(
            character_id, voice_type
        )
        
        # WebSocket连接
        self.websocket = None
        self.is_connected = False
        
        # 音频相关
        self.audio = pyaudio.PyAudio() if PYAUDIO_AVAILABLE else None
        self.input_stream = None
        self.output_stream = None
        self.audio_queue = queue.Queue()
        
        # 回调函数
        self.on_message_received: Optional[Callable] = None
        self.on_audio_received: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
    async def connect(self):
        """连接到语音服务"""
        try:
            ws_config = self.config["ws_config"]
            
            # 构建WebSocket URL和headers
            url = ws_config["base_url"]
            headers = ws_config["headers"]
            
            print(f"正在连接到 {url}")
            print(f"使用角色: {self.config['character_info']['name']}")
            
            # 连接WebSocket
            self.websocket = await websockets.connect(
                url,
                additional_headers=headers,
                ping_interval=30,
                ping_timeout=10
            )
            
            self.is_connected = True
            print("WebSocket连接成功")
            
            # 发送会话开始请求
            await self._start_session()
            
            # 启动消息监听
            asyncio.create_task(self._listen_messages())
            
        except Exception as e:
            print(f"连接失败: {e}")
            if self.on_error:
                self.on_error(f"连接失败: {e}")
            raise
    
    async def _start_session(self):
        """开始会话"""
        session_config = self.config["session_config"]
        
        start_message = {
            "type": "start_session",
            "data": session_config
        }
        
        await self.websocket.send(json.dumps(start_message))
        print("会话开始请求已发送")
    
    async def _listen_messages(self):
        """监听WebSocket消息"""
        try:
            async for message in self.websocket:
                await self._handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket连接已关闭")
            self.is_connected = False
        except Exception as e:
            print(f"消息监听错误: {e}")
            if self.on_error:
                self.on_error(f"消息监听错误: {e}")
    
    async def _handle_message(self, message: str):
        """处理接收到的消息"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "audio":
                # 处理音频数据
                audio_data = data.get("data")
                if audio_data and self.on_audio_received:
                    self.on_audio_received(audio_data)
                    
            elif message_type == "text":
                # 处理文本消息
                text_data = data.get("data")
                if text_data and self.on_message_received:
                    self.on_message_received(text_data)
                    
            elif message_type == "session_started":
                print("会话已开始")
                
            elif message_type == "error":
                error_msg = data.get("message", "未知错误")
                print(f"服务器错误: {error_msg}")
                if self.on_error:
                    self.on_error(error_msg)
                    
        except json.JSONDecodeError as e:
            print(f"消息解析错误: {e}")
        except Exception as e:
            print(f"消息处理错误: {e}")
    
    def start_audio_input(self):
        """开始音频输入"""
        if not PYAUDIO_AVAILABLE:
            print("pyaudio未安装，无法启动音频输入")
            return
            
        input_config = self.config["input_audio_config"]
        
        self.input_stream = self.audio.open(
            format=input_config["bit_size"],
            channels=input_config["channels"],
            rate=input_config["sample_rate"],
            input=True,
            frames_per_buffer=input_config["chunk"]
        )
        
        # 启动音频输入线程
        self.input_thread = threading.Thread(target=self._audio_input_loop)
        self.input_thread.daemon = True
        self.input_thread.start()
        
        print("音频输入已开始")
    
    def _audio_input_loop(self):
        """音频输入循环"""
        input_config = self.config["input_audio_config"]
        
        while self.is_connected and self.input_stream:
            try:
                # 读取音频数据
                audio_data = self.input_stream.read(
                    input_config["chunk"],
                    exception_on_overflow=False
                )
                
                # 发送音频数据到服务器
                if self.websocket and not self.websocket.closed:
                    asyncio.run_coroutine_threadsafe(
                        self._send_audio(audio_data),
                        asyncio.get_event_loop()
                    )
                    
            except Exception as e:
                print(f"音频输入错误: {e}")
                break
    
    async def _send_audio(self, audio_data: bytes):
        """发送音频数据"""
        try:
            # 这里需要根据实际API格式调整
            audio_message = {
                "type": "audio",
                "data": audio_data.hex()  # 转换为十六进制字符串
            }
            
            await self.websocket.send(json.dumps(audio_message))
            
        except Exception as e:
            print(f"发送音频错误: {e}")
    
    def start_audio_output(self):
        """开始音频输出"""
        if not PYAUDIO_AVAILABLE:
            print("pyaudio未安装，无法启动音频输出")
            return
            
        output_config = self.config["output_audio_config"]
        
        self.output_stream = self.audio.open(
            format=output_config["bit_size"],
            channels=output_config["channels"],
            rate=output_config["sample_rate"],
            output=True,
            frames_per_buffer=output_config["chunk"]
        )
        
        print("音频输出已开始")
    
    def play_audio(self, audio_data: bytes):
        """播放音频数据"""
        if self.output_stream:
            try:
                self.output_stream.write(audio_data)
            except Exception as e:
                print(f"音频播放错误: {e}")
    
    async def send_text(self, text: str):
        """发送文本消息"""
        if not self.is_connected or not self.websocket:
            raise RuntimeError("未连接到服务器")
        
        text_message = {
            "type": "text",
            "data": {
                "text": text
            }
        }
        
        await self.websocket.send(json.dumps(text_message))
        print(f"已发送文本: {text}")
    
    async def disconnect(self):
        """断开连接"""
        self.is_connected = False
        
        # 停止音频流
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
            self.input_stream = None
            
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
            self.output_stream = None
        
        # 关闭WebSocket
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        
        # 关闭PyAudio
        if self.audio:
            self.audio.terminate()
        
        print("已断开连接")
    
    def set_callbacks(self, 
                     on_message_received: Optional[Callable] = None,
                     on_audio_received: Optional[Callable] = None,
                     on_error: Optional[Callable] = None):
        """设置回调函数"""
        self.on_message_received = on_message_received
        self.on_audio_received = on_audio_received
        self.on_error = on_error