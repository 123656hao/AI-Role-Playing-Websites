#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI角色扮演聊天应用
支持多角色对话和语音交互
"""

import os
import sys
import json
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入服务模块
try:
    from services.ai_service import AIRoleplayService
    from utils.port_manager import PortManager
    print("✓ 所有服务模块导入成功")
except ImportError as e:
    print(f"✗ 导入服务模块失败: {e}")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'ai-roleplay-secret-2024')

# 初始化SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# 初始化服务
ai_service = None

def init_services():
    """初始化所有服务"""
    global ai_service
    
    try:
        # 初始化AI服务
        ai_service = AIRoleplayService()
        logger.info("✓ AI角色扮演服务初始化成功")
        
        return True
    except Exception as e:
        logger.error(f"✗ 服务初始化失败: {e}")
        return False

def load_characters():
    """加载角色数据"""
    try:
        with open('data/characters.json', 'r', encoding='utf-8') as f:
            characters = json.load(f)
        return characters
    except Exception as e:
        logger.error(f"加载角色数据失败: {e}")
        return []

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'ai_service': ai_service is not None
        }
    })

@app.route('/api/characters')
def get_characters():
    """获取角色列表"""
    try:
        characters = load_characters()
        return jsonify({
            'success': True,
            'characters': characters
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/characters/<character_id>')
def get_character(character_id):
    """获取特定角色信息"""
    try:
        characters = load_characters()
        character = next((c for c in characters if c['id'] == character_id), None)
        
        if character:
            return jsonify({
                'success': True,
                'character': character
            })
        else:
            return jsonify({
                'success': False,
                'error': '角色不存在'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/characters/<character_id>/welcome')
def get_welcome_message(character_id):
    """获取角色欢迎消息"""
    try:
        characters = load_characters()
        character = next((c for c in characters if c['id'] == character_id), None)
        
        if not character:
            return jsonify({
                'success': False,
                'error': '角色不存在'
            })
        
        welcome_message = ai_service.generate_welcome_message(character)
        
        return jsonify({
            'success': True,
            'message': welcome_message,
            'character': character
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@socketio.on('connect')
def handle_connect():
    """客户端连接"""
    logger.info(f"客户端已连接: {request.sid}")
    emit('status', {'message': '连接成功', 'type': 'success'})

@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开连接"""
    logger.info(f"客户端已断开: {request.sid}")

@socketio.on('select_character')
def handle_select_character(data):
    """处理角色选择"""
    try:
        character_id = data.get('character_id')
        if not character_id:
            emit('error', {'message': '请选择一个角色'})
            return
        
        characters = load_characters()
        character = next((c for c in characters if c['id'] == character_id), None)
        
        if not character:
            emit('error', {'message': '角色不存在'})
            return
        
        # 生成欢迎消息
        welcome_message = ai_service.generate_welcome_message(character)
        
        emit('character_selected', {
            'character': character,
            'welcome_message': welcome_message
        })
        
        logger.info(f"角色已选择: {character['name']} (ID: {character_id})")
        
    except Exception as e:
        logger.error(f"处理角色选择时出错: {e}")
        emit('error', {'message': f'选择角色失败: {str(e)}'})

@socketio.on('chat_message')
def handle_chat_message(data):
    """处理聊天消息"""
    try:
        message = data.get('message', '').strip()
        character_id = data.get('character_id')
        
        if not message:
            emit('error', {'message': '消息内容不能为空'})
            return
        
        if not character_id:
            emit('error', {'message': '请先选择一个角色'})
            return
        
        characters = load_characters()
        character = next((c for c in characters if c['id'] == character_id), None)
        
        if not character:
            emit('error', {'message': '角色不存在'})
            return
        
        logger.info(f"收到消息: {message}, 角色: {character['name']}")
        
        # 生成AI回复
        emit('status', {'message': f'{character["name"]}正在思考...', 'type': 'info'})
        
        ai_response = ai_service.generate_response(character, message, request.sid)
        
        if ai_response:
            emit('chat_response', {
                'message': ai_response,
                'character': character,
                'timestamp': datetime.now().isoformat()
            })
            
            emit('status', {'message': '回复完成', 'type': 'success'})
            logger.info(f"AI回复: {ai_response}")
        else:
            emit('error', {'message': 'AI服务暂时不可用'})
        
    except Exception as e:
        logger.error(f"处理聊天消息时出错: {e}")
        emit('error', {'message': f'处理失败: {str(e)}'})

@socketio.on('execute_skill')
def handle_execute_skill(data):
    """处理技能执行"""
    try:
        character_id = data.get('character_id')
        skill_name = data.get('skill_name')
        skill_data = data.get('data', {})
        
        if not character_id or not skill_name:
            emit('error', {'message': '缺少必要参数'})
            return
        
        characters = load_characters()
        character = next((c for c in characters if c['id'] == character_id), None)
        
        if not character:
            emit('error', {'message': '角色不存在'})
            return
        
        if skill_name not in character.get('skills', []):
            emit('error', {'message': '该角色不支持此技能'})
            return
        
        logger.info(f"执行技能: {skill_name}, 角色: {character['name']}")
        
        # 执行技能
        emit('status', {'message': f'正在执行{skill_name}技能...', 'type': 'info'})
        
        result = ai_service.execute_skill(character, skill_name, skill_data)
        
        if 'error' not in result:
            emit('skill_result', {
                'skill': skill_name,
                'result': result,
                'character': character
            })
            
            emit('status', {'message': '技能执行完成', 'type': 'success'})
        else:
            emit('error', {'message': result['error']})
        
    except Exception as e:
        logger.error(f"执行技能时出错: {e}")
        emit('error', {'message': f'技能执行失败: {str(e)}'})

@socketio.on('clear_conversation')
def handle_clear_conversation(data):
    """清除对话历史"""
    try:
        conversation_id = data.get('conversation_id', request.sid)
        ai_service.clear_conversation(conversation_id)
        
        emit('conversation_cleared', {'message': '对话历史已清除'})
        logger.info(f"对话历史已清除: {conversation_id}")
        
    except Exception as e:
        logger.error(f"清除对话历史时出错: {e}")
        emit('error', {'message': f'清除失败: {str(e)}'})

def main():
    """主函数"""
    print("=" * 60)
    print("🎭 AI角色扮演聊天应用启动中...")
    print("=" * 60)
    
    # 检查环境变量
    required_env_vars = ['OPENAI_API_KEY']
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var) and not os.getenv('ARK_API_KEY'):
            missing_vars.append(var)
    
    if missing_vars and not os.getenv('ARK_API_KEY'):
        print(f"✗ 缺少必要的环境变量: {', '.join(missing_vars)}")
        print("请在.env文件中配置OPENAI_API_KEY或ARK_API_KEY")
        return
    
    print("✓ 环境变量检查通过")
    
    # 检查角色数据文件
    if not os.path.exists('data/characters.json'):
        print("✗ 角色数据文件不存在: data/characters.json")
        return
    
    characters = load_characters()
    print(f"✓ 已加载 {len(characters)} 个角色")
    
    # 初始化服务
    if not init_services():
        print("✗ 服务初始化失败，程序退出")
        return
    
    # 获取可用端口
    port_manager = PortManager()
    port = port_manager.find_available_port('localhost', 5000) or 5000
    
    print(f"✓ 使用端口: {port}")
    print("=" * 60)
    print(f"🚀 应用已启动!")
    print(f"📱 访问地址: http://localhost:{port}")
    print(f"🎭 功能: AI角色扮演聊天")
    print(f"👥 可用角色: {len(characters)} 个")
    print("=" * 60)
    
    # 启动应用
    try:
        socketio.run(
            app,
            host='0.0.0.0',
            port=port,
            debug=False,
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"✗ 应用启动失败: {e}")

if __name__ == '__main__':
    main()