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
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入自定义模块
from services.ai_service import AIRoleplayService
from services.voice_service import VoiceService
from services.character_service import CharacterService

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'ai-roleplay-secret-2024')
CORS(app)

# 初始化服务
ai_service = AIRoleplayService()
voice_service = VoiceService()
character_service = CharacterService()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

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

if __name__ == '__main__':
    os.makedirs('static/audio', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)