#!/usr/bin/env python3
"""
AI角色扮演聊天网站 - 主应用
支持语音对话、角色搜索、多种AI技能
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
import json
import uuid
from datetime import datetime
import logging
import threading
import asyncio
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入自定义模块
from services.ai_service import AIRoleplayService
from services.voice_service import VoiceService
from services.enhanced_voice_service import EnhancedVoiceService
from services.character_service import CharacterService
from services.websocket_handler import WebSocketHandler

# WebSocket相关导入
try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    print("⚠️ websockets未安装，实时语音功能将被禁用")

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'ai-roleplay-secret-2024')
CORS(app)

# 初始化服务
ai_service = AIRoleplayService()
voice_service = VoiceService()
enhanced_voice_service = EnhancedVoiceService()
character_service = CharacterService()

# 初始化WebSocket处理器
websocket_handler = None
websocket_server = None

if WEBSOCKETS_AVAILABLE:
    websocket_handler = WebSocketHandler(enhanced_voice_service, ai_service)

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/demo')
def realtime_demo():
    """实时语音对话演示页面"""
    return render_template('realtime_demo.html')

@app.route('/api/characters')
def get_characters():
    """获取所有角色"""
    try:
        characters = character_service.get_all_characters()
        return jsonify({
            'success': True,
            'characters': characters
        })
    except Exception as e:
        logger.error(f"获取角色失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/characters/search')
def search_characters():
    """搜索角色"""
    query = request.args.get('q', '')
    category = request.args.get('category', 'all')
    
    try:
        characters = character_service.search_characters(query, category)
        return jsonify({
            'success': True,
            'characters': characters
        })
    except Exception as e:
        logger.error(f"搜索角色失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chat/start', methods=['POST'])
def start_chat():
    """开始与角色对话"""
    data = request.get_json()
    character_id = data.get('character_id')
    
    if not character_id:
        return jsonify({'success': False, 'error': '缺少角色ID'}), 400
    
    try:
        character = character_service.get_character_by_id(character_id)
        if not character:
            return jsonify({'success': False, 'error': '角色不存在'}), 404
        
        # 创建会话
        session_id = str(uuid.uuid4())
        session['chat_session_id'] = session_id
        session['character_id'] = character_id
        
        # 生成欢迎消息
        welcome_message = ai_service.generate_welcome_message(character)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'character': character,
            'welcome_message': welcome_message
        })
    except Exception as e:
        logger.error(f"开始对话失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chat/message', methods=['POST'])
def send_message():
    """发送消息给AI角色"""
    data = request.get_json()
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'success': False, 'error': '消息不能为空'}), 400
    
    session_id = session.get('chat_session_id')
    character_id = session.get('character_id')
    
    if not session_id or not character_id:
        return jsonify({'success': False, 'error': '会话无效'}), 400
    
    try:
        character = character_service.get_character_by_id(character_id)
        if not character:
            return jsonify({'success': False, 'error': '角色不存在'}), 404
        
        # 生成AI回复
        ai_response = ai_service.generate_response(character, message, session_id)
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'character_name': character['name'],
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"发送消息失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/voice/recognize', methods=['POST'])
def recognize_voice():
    """语音识别"""
    if 'audio' not in request.files:
        return jsonify({'success': False, 'error': '没有音频文件'}), 400
    
    audio_file = request.files['audio']
    
    try:
        text = voice_service.speech_to_text(audio_file)
        return jsonify({
            'success': True,
            'text': text
        })
    except Exception as e:
        logger.error(f"语音识别失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/voice/synthesize', methods=['POST'])
def synthesize_voice():
    """语音合成"""
    data = request.get_json()
    text = data.get('text', '').strip()
    character_id = data.get('character_id')
    
    if not text:
        return jsonify({'success': False, 'error': '文本不能为空'}), 400
    
    try:
        character = character_service.get_character_by_id(character_id) if character_id else None
        audio_url = voice_service.text_to_speech(text, character)
        
        return jsonify({
            'success': True,
            'audio_url': audio_url
        })
    except Exception as e:
        logger.error(f"语音合成失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/skills/<skill_name>', methods=['POST'])
def use_skill(skill_name):
    """使用AI角色技能"""
    data = request.get_json()
    character_id = session.get('character_id')
    
    if not character_id:
        return jsonify({'success': False, 'error': '会话无效'}), 400
    
    try:
        character = character_service.get_character_by_id(character_id)
        if not character:
            return jsonify({'success': False, 'error': '角色不存在'}), 404
        
        result = ai_service.execute_skill(character, skill_name, data)
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        logger.error(f"执行技能失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/voice/config/<character_id>')
def get_voice_config(character_id):
    """获取角色的语音配置"""
    try:
        from services.voice_config_service import VoiceConfigService
        voice_config_service = VoiceConfigService()
        
        # 检查角色是否存在
        character = character_service.get_character_by_id(character_id)
        if not character:
            return jsonify({'success': False, 'error': '角色不存在'}), 404
        
        # 获取语音类型参数
        voice_type = request.args.get('voice_type', 'female')
        
        # 生成语音配置
        config = voice_config_service.create_character_voice_config(character_id, voice_type)
        
        return jsonify({
            'success': True,
            'config': {
                'character_info': config['character_info'],
                'voice_speaker': config['session_config']['tts']['speaker'],
                'speaking_style': config['session_config']['dialog']['speaking_style'],
                'available_voices': voice_config_service.get_available_voices()
            }
        })
    except Exception as e:
        logger.error(f"获取语音配置失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/voice/realtime/start', methods=['POST'])
def start_realtime_voice():
    """开始实时语音对话"""
    data = request.get_json()
    character_id = data.get('character_id')
    voice_type = data.get('voice_type', 'female')
    
    if not character_id:
        return jsonify({'success': False, 'error': '缺少角色ID'}), 400
    
    try:
        from services.voice_config_service import VoiceConfigService
        voice_config_service = VoiceConfigService()
        
        # 检查角色是否存在
        character = character_service.get_character_by_id(character_id)
        if not character:
            return jsonify({'success': False, 'error': '角色不存在'}), 404
        
        # 生成完整的语音配置
        config = voice_config_service.create_character_voice_config(character_id, voice_type)
        
        # 创建会话ID
        voice_session_id = str(uuid.uuid4())
        session['voice_session_id'] = voice_session_id
        
        return jsonify({
            'success': True,
            'session_id': voice_session_id,
            'ws_config': config['ws_config'],
            'session_config': config['session_config'],
            'character_info': config['character_info']
        })
    except Exception as e:
        logger.error(f"开始实时语音对话失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def start_websocket_server():
    """启动WebSocket服务器"""
    if not WEBSOCKETS_AVAILABLE or not websocket_handler:
        print("⚠️ WebSocket服务器无法启动：websockets库未安装或处理器未初始化")
        return
    
    async def run_server():
        global websocket_server
        try:
            websocket_server = await websockets.serve(
                websocket_handler.handle_connection,
                "localhost",
                8765
            )
            print("🌐 WebSocket服务器启动成功: ws://localhost:8765")
            await websocket_server.wait_closed()
        except Exception as e:
            logger.error(f"WebSocket服务器启动失败: {e}")
    
    # 在新线程中运行WebSocket服务器
    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_server())
    
    websocket_thread = threading.Thread(target=run_in_thread, daemon=True)
    websocket_thread.start()

@app.route('/api/realtime/start', methods=['POST'])
def start_realtime_session():
    """启动实时语音会话"""
    try:
        data = request.get_json()
        character_id = data.get('character_id')
        
        if not character_id:
            return jsonify({'success': False, 'error': '缺少角色ID'}), 400
        
        if not WEBSOCKETS_AVAILABLE:
            return jsonify({
                'success': False, 
                'error': 'WebSocket功能不可用，请安装websockets库'
            }), 503
        
        # 检查角色是否存在
        character = character_service.get_character_by_id(character_id)
        if not character:
            return jsonify({'success': False, 'error': '角色不存在'}), 404
        
        # 返回WebSocket连接信息
        return jsonify({
            'success': True,
            'websocket_url': 'ws://localhost:8765',
            'character': character,
            'instructions': {
                'connect': '连接到WebSocket服务器',
                'start_session': '发送start_voice_session消息开始会话',
                'send_audio': '发送audio_data消息传输音频',
                'send_text': '发送text_message消息发送文字'
            }
        })
        
    except Exception as e:
        logger.error(f"启动实时会话失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/realtime/status')
def get_realtime_status():
    """获取实时语音服务状态"""
    try:
        status = {
            'websockets_available': WEBSOCKETS_AVAILABLE,
            'server_running': websocket_server is not None,
            'enhanced_voice_available': enhanced_voice_service is not None
        }
        
        if websocket_handler:
            status.update(websocket_handler.get_connection_stats())
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"获取实时状态失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/voice/enhanced/synthesize', methods=['POST'])
def enhanced_voice_synthesize():
    """增强语音合成"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        character_id = data.get('character_id')
        
        if not text:
            return jsonify({'success': False, 'error': '文本不能为空'}), 400
        
        character = None
        if character_id:
            character = character_service.get_character_by_id(character_id)
        
        # 使用增强语音服务
        audio_url = enhanced_voice_service.text_to_speech(text, character)
        
        return jsonify({
            'success': True,
            'audio_url': audio_url,
            'character': character['name'] if character else None
        })
        
    except Exception as e:
        logger.error(f"增强语音合成失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/voice/enhanced/recognize', methods=['POST'])
def enhanced_voice_recognize():
    """增强语音识别"""
    try:
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': '没有音频文件'}), 400
        
        audio_file = request.files['audio']
        
        # 使用增强语音服务
        text = enhanced_voice_service.speech_to_text(audio_file)
        
        return jsonify({
            'success': True,
            'text': text
        })
        
    except Exception as e:
        logger.error(f"增强语音识别失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # 创建必要目录
    os.makedirs('static/audio', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # 启动WebSocket服务器
    start_websocket_server()
    
    # 启动Flask应用
    print("🚀 启动Flask应用...")
    app.run(debug=True, host='0.0.0.0', port=5000)