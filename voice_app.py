#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI语音聊天应用
支持语音识别、AI对话和语音合成
"""

import os
import sys
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import json
import base64
import tempfile
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入服务模块
try:
    from services.baidu_voice_service import BaiduVoiceService
    from services.baidu_tts_service import BaiduTTSService
    from services.ai_service import AIRoleplayService
    from services.character_service import CharacterService
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
app.config['SECRET_KEY'] = 'your-secret-key-here'

# 初始化SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# 初始化服务
voice_service = None
tts_service = None
ai_service = None
character_service = None

# 实时语音处理器
realtime_voice_handler = None

def init_services():
    """初始化所有服务"""
    global voice_service, tts_service, ai_service, character_service
    
    try:
        # 初始化百度语音识别服务
        voice_service = BaiduVoiceService()
        logger.info("✓ 百度语音识别服务初始化成功")
        
        # 初始化百度语音合成服务
        tts_service = BaiduTTSService()
        logger.info("✓ 百度语音合成服务初始化成功")
        
        # 初始化AI服务
        ai_service = AIRoleplayService()
        logger.info("✓ AI服务初始化成功")
        
        # 初始化角色服务
        character_service = CharacterService()
        logger.info("✓ 角色服务初始化成功")
        
        return True
    except Exception as e:
        logger.error(f"✗ 服务初始化失败: {e}")
        return False

def init_realtime_voice_handler():
    """初始化实时语音处理器"""
    global realtime_voice_handler
    try:
        from services.realtime_voice_handler import RealtimeVoiceHandler
        realtime_voice_handler = RealtimeVoiceHandler(voice_service, ai_service, tts_service)
        logger.info("✓ 实时语音处理器初始化成功")
        return True
    except Exception as e:
        logger.error(f"✗ 实时语音处理器初始化失败: {e}")
        return False

@app.route('/')
def index():
    """主页 - 使用简化的角色扮演界面"""
    try:
        characters = load_characters()
        logger.info(f"主页加载，角色数量: {len(characters)}")
        return render_template('simple_roleplay.html', 
                             characters=characters, 
                             character_count=len(characters))
    except Exception as e:
        logger.error(f"主页加载失败: {e}")
        return f"""
        <html>
        <head><title>调试信息</title></head>
        <body>
        <h1>应用调试信息</h1>
        <p><strong>错误:</strong> {str(e)}</p>
        <p><strong>时间:</strong> {datetime.now()}</p>
        <p><strong>工作目录:</strong> {os.getcwd()}</p>
        <p><strong>文件列表:</strong></p>
        <ul>
        {''.join([f'<li>{f}</li>' for f in os.listdir('.')])}
        </ul>
        <p><a href="/api/characters">测试角色API</a></p>
        <p><a href="/health">健康检查</a></p>
        </body>
        </html>
        """

@app.route('/original')
def original_index():
    """原始复杂界面"""
    return render_template('index.html')

@app.route('/voice')
def voice_chat():
    """语音聊天页面"""
    return render_template('voice_chat.html')

@app.route('/realtime')
def realtime_voice():
    """实时语音对话页面"""
    return render_template('realtime_voice_chat.html')

@app.route('/test')
def test_characters():
    """角色测试页面"""
    return send_from_directory('.', 'Test/test_characters.html')

@app.route('/simple')
def simple_test():
    """简单测试页面"""
    return send_from_directory('.', 'simple_test.html')

@app.route('/debug')
def debug_page():
    """调试页面"""
    return send_from_directory('.', 'debug.html')

@app.route('/mic-test')
def mic_test():
    """麦克风测试页面"""
    return send_from_directory('.', 'mic_test.html')

@app.route('/unity-test')
def unity_test():
    """Unity集成测试页面"""
    return send_from_directory('.', 'unity_test.html')

@app.route('/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'voice_recognition': voice_service is not None,
            'text_to_speech': tts_service is not None,
            'ai_service': ai_service is not None
        }
    })

def load_characters():
    """加载角色数据"""
    try:
        with open('data/characters.json', 'r', encoding='utf-8') as f:
            characters = json.load(f)
        return characters
    except Exception as e:
        logger.error(f"加载角色数据失败: {e}")
        # 返回默认角色
        return [
            {
                'id': 'assistant',
                'name': 'AI助手',
                'category': 'assistant',
                'background': '我是一个智能AI助手，专门为用户提供语音交互服务',
                'personality': '友善、耐心、乐于助人',
                'expertise': '语音识别、自然语言处理、智能对话',
                'tags': ['AI', '助手', '语音']
            }
        ]

@app.route('/api/characters')
def get_characters():
    """获取可用角色列表"""
    try:
        if character_service:
            characters = character_service.get_all_characters()
        else:
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

@app.route('/api/voice/status')
def voice_status():
    """获取语音服务状态"""
    try:
        status = {
            'configured': voice_service is not None and tts_service is not None,
            'voice_recognition': voice_service is not None,
            'text_to_speech': tts_service is not None
        }
        
        test_result = {
            'api_accessible': True  # 简化处理，实际可以测试API连通性
        }
        
        return jsonify({
            'success': True,
            'status': status,
            'test_result': test_result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/voice/upload', methods=['POST'])
def upload_voice():
    """处理语音上传和识别"""
    try:
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有音频文件'
            }), 400
        
        file = request.files['audio']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '没有选择文件'
            }), 400
        
        # 语音识别
        text = voice_service.speech_to_text(file)
        
        if not text or text.startswith('语音识别') or text.startswith('百度') or text.startswith('音频'):
            return jsonify({
                'success': False,
                'error': text or '语音识别失败'
            }), 500
        
        return jsonify({
            'success': True,
            'text': text
        })
        
    except Exception as e:
        logger.error(f"语音上传处理失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': '缺少消息内容'
            }), 400
        
        message = data['message'].strip()
        character_id = data.get('character_id', 'default')
        
        if not message:
            return jsonify({
                'success': False,
                'error': '消息不能为空'
            }), 400
        
        # 获取角色信息
        if character_service:
            character = character_service.get_character_by_id(character_id)
        else:
            # 从文件加载角色
            characters_list = load_characters()
            character = None
            for char in characters_list:
                if char['id'] == character_id:
                    character = char
                    break
        
        if not character:
            return jsonify({
                'success': False,
                'error': '角色不存在'
            }), 404
        
        # 生成AI回复
        response = ai_service.generate_response(character, message, 'web_session')
        
        # 生成语音合成
        audio_url = None
        try:
            tts_result = tts_service.text_to_speech(response, character)
            if tts_result and tts_result.get('success'):
                audio_url = tts_result.get('audio_url')
        except Exception as e:
            logger.warning(f"语音合成失败: {e}")
        
        return jsonify({
            'success': True,
            'response': response,
            'character': character,
            'audio_url': audio_url
        })
        
    except Exception as e:
        logger.error(f"聊天处理失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tts', methods=['POST'])
def unity_tts():
    """Unity TTS API - 为Unity 3D角色提供语音合成"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': '缺少文本内容'
            }), 400
        
        text = data['text'].strip()
        character_id = data.get('character_id', 'assistant')
        voice_settings = data.get('voice_settings', {})
        
        if not text:
            return jsonify({
                'success': False,
                'error': '文本不能为空'
            }), 400
        
        logger.info(f"Unity TTS请求: 角色={character_id}, 文本长度={len(text)}")
        
        # 获取角色信息
        characters_list = load_characters()
        character = None
        
        for char in characters_list:
            if char['id'] == character_id:
                character = char
                break
        
        # 如果没找到角色，使用默认设置
        if not character:
            character = {
                'id': character_id,
                'name': 'AI助手',
                'gender': 'female',  # 默认女声
                'voice_type': 'female'
            }
        
        # 根据Unity传来的语音设置调整角色参数
        if voice_settings and character:
            character = character.copy()
            character['unity_voice_settings'] = voice_settings
        
        # 语音合成
        tts_result = tts_service.text_to_speech(text, character)
        
        if tts_result:
            # 处理TTS结果的兼容性
            audio_path = None
            
            if isinstance(tts_result, dict):
                if tts_result.get('success'):
                    audio_path = tts_result.get('audio_path')
                else:
                    return jsonify({
                        'success': False,
                        'error': tts_result.get('error', '语音合成失败')
                    }), 500
            elif isinstance(tts_result, str):
                # 从URL推导出文件路径
                if tts_result.startswith('/static/audio/'):
                    filename = tts_result.replace('/static/audio/', '')
                    audio_path = os.path.join('static', 'audio', filename)
            
            # 检查是否是Unity请求
            user_agent = request.headers.get('User-Agent', '')
            is_unity_client = 'Unity' in user_agent or data.get('unity_client', False)
            
            if is_unity_client and audio_path and os.path.exists(audio_path):
                # 直接返回音频文件给Unity
                from flask import send_file
                logger.info(f"向Unity发送音频文件: {audio_path}")
                return send_file(
                    audio_path,
                    mimetype='audio/wav',
                    as_attachment=False
                )
            else:
                # 返回JSON响应给Web客户端
                return jsonify({
                    'success': True,
                    'audio_url': tts_result if isinstance(tts_result, str) else tts_result.get('audio_url'),
                    'character_id': character_id,
                    'voice_type': character.get('gender', 'female'),
                    'character_name': character.get('name', 'AI助手')
                })
        else:
            return jsonify({
                'success': False,
                'error': '语音合成失败'
            }), 500
        
    except Exception as e:
        logger.error(f"Unity TTS处理失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/characters/unity')
def get_unity_characters():
    """获取Unity角色配置"""
    try:
        # 加载角色数据
        characters = load_characters()
        
        # 转换为Unity格式，添加性别和语音类型信息
        unity_characters = []
        for char in characters:
            # 根据角色名称推断性别
            gender = 'male'
            if any(name in char.get('name', '') for name in ['玛丽', '居里', '李老师']):
                gender = 'female'
            elif char.get('name') == 'AI助手':
                gender = 'female'
            
            unity_char = {
                'id': char['id'],
                'name': char['name'],
                'gender': gender,
                'voice_type': gender,
                'category': char.get('category', 'general'),
                'background': char.get('background', ''),
                'personality': char.get('personality', ''),
                'voice_settings': {
                    'pitch': 1.1 if gender == 'female' else 0.9,
                    'speed': 1.0,
                    'voice_id': f"{gender}_default"
                }
            }
            unity_characters.append(unity_char)
        
        return jsonify({
            'success': True,
            'characters': unity_characters,
            'total_count': len(unity_characters)
        })
        
    except Exception as e:
        logger.error(f"获取Unity角色配置失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@socketio.on('connect')
def handle_connect():
    """客户端连接"""
    logger.info(f"客户端已连接: {request.sid}")
    emit('status', {'message': '连接成功', 'type': 'success'})

@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开连接"""
    logger.info(f"客户端已断开: {request.sid}")
    
    # 清理实时语音会话
    if realtime_voice_handler:
        # 查找并结束该连接的会话
        for session_id, session in realtime_voice_handler.active_sessions.items():
            if session.get('connection_id') == request.sid:
                realtime_voice_handler.end_session(session_id)
                break

@socketio.on('chat_message')
def handle_chat_message(data):
    """处理聊天消息"""
    try:
        message = data.get('message', '').strip()
        character_id = data.get('character_id', 'assistant')
        
        if not message:
            emit('error', {'message': '消息内容不能为空'})
            return
        
        logger.info(f"收到聊天消息: {message}, 角色: {character_id}")
        
        # 获取角色信息
        if character_service:
            character = character_service.get_character_by_id(character_id)
        else:
            # 从文件加载角色信息
            characters_list = load_characters()
            character = None
            
            # 查找对应的角色
            for char in characters_list:
                if char['id'] == character_id:
                    character = char
                    break
        
        # 如果没找到，使用默认角色
        if not character:
            character = {
                'name': 'AI助手',
                'description': '智能语音助手',
                'background': '我是一个智能AI助手，专门为用户提供语音交互服务',
                'personality': '友善、耐心、乐于助人',
                'expertise': '语音识别、自然语言处理、智能对话'
            }
        
        # AI对话
        emit('status', {'message': f'{character["name"]}正在思考...', 'type': 'info'})
        
        try:
            ai_response = ai_service.generate_response(character, message, request.sid)
            
            if not ai_response:
                emit('error', {'message': 'AI服务响应失败'})
                return
            
            logger.info(f"AI回复: {ai_response}")
            
            # 语音合成
            audio_url = None
            try:
                emit('status', {'message': '正在生成语音...', 'type': 'info'})
                tts_result = tts_service.text_to_speech(ai_response, character)
                
                # 处理TTS结果的兼容性
                if tts_result:
                    audio_path = None
                    
                    # 如果返回的是字典格式
                    if isinstance(tts_result, dict):
                        if tts_result.get('success'):
                            audio_url = tts_result.get('audio_url')
                        else:
                            logger.warning(f"语音合成失败: {tts_result.get('error', '未知错误')}")
                    
                    # 如果返回的是字符串格式（旧版本兼容）
                    elif isinstance(tts_result, str):
                        audio_url = tts_result
                        logger.info("语音合成成功")
                else:
                    logger.warning("语音合成失败")
            except Exception as tts_error:
                logger.error(f"语音合成错误: {tts_error}")
            
            # 发送回复
            emit('chat_response', {
                'response': ai_response,
                'character': character,
                'audio_url': audio_url,
                'timestamp': datetime.now().isoformat()
            })
            
            emit('status', {'message': '处理完成', 'type': 'success'})
            
        except Exception as ai_error:
            logger.error(f"AI服务错误: {ai_error}")
            emit('error', {'message': f'AI服务错误: {str(ai_error)}'})
        
    except Exception as e:
        logger.error(f"处理聊天消息时出错: {e}")
        emit('error', {'message': f'处理失败: {str(e)}'})

@socketio.on('voice_message')
def handle_voice_message(data):
    """处理语音消息"""
    try:
        logger.info(f"收到语音消息，数据类型: {type(data)}, 内容: {str(data)[:100]}...")
        
        # 确保data是字典类型
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except:
                emit('error', {'message': '语音数据格式错误'})
                return
        
        # 获取音频数据
        audio_data = data.get('audio')
        if not audio_data:
            emit('error', {'message': '没有收到音频数据'})
            return
        
        # 解码base64音频数据
        try:
            audio_bytes = base64.b64decode(audio_data.split(',')[1] if ',' in audio_data else audio_data)
        except Exception as e:
            logger.error(f"音频数据解码失败: {e}")
            emit('error', {'message': '音频数据格式错误'})
            return
        
        # 保存临时音频文件
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_audio_path = temp_file.name
        
        try:
            # 语音识别
            emit('status', {'message': '正在识别语音...', 'type': 'info'})
            
            # 使用werkzeug的FileStorage来正确模拟文件对象
            from werkzeug.datastructures import FileStorage
            from io import BytesIO
            
            # 读取临时文件内容
            with open(temp_audio_path, 'rb') as f:
                file_content = f.read()
            
            # 创建FileStorage对象
            temp_file_obj = FileStorage(
                stream=BytesIO(file_content),
                filename='recording.wav',
                content_type='audio/wav'
            )
            
            recognition_text = voice_service.speech_to_text(temp_file_obj)
            
            if not recognition_text or recognition_text.startswith('语音识别') or recognition_text.startswith('百度'):
                emit('error', {'message': recognition_text or '语音识别失败'})
                return
            
            user_text = recognition_text.strip()
            if not user_text:
                emit('error', {'message': '未识别到语音内容'})
                return
            
            logger.info(f"语音识别结果: {user_text}")
            emit('recognition_result', {'text': user_text})
            
            # AI对话 - 使用默认角色
            emit('status', {'message': 'AI正在思考...', 'type': 'info'})
            default_character = {
                'name': 'AI助手',
                'description': '智能语音助手',
                'background': '我是一个智能AI助手，专门为用户提供语音交互服务',
                'personality': '友善、耐心、乐于助人',
                'expertise': '语音识别、自然语言处理、智能对话'
            }
            ai_response = ai_service.generate_response(default_character, user_text, request.sid)
            
            if not ai_response:
                emit('error', {'message': 'AI服务响应失败'})
                return
            
            logger.info(f"AI回复: {ai_response}")
            emit('ai_response', {'text': ai_response})
            
            # 语音合成
            emit('status', {'message': '正在生成语音...', 'type': 'info'})
            tts_result = tts_service.text_to_speech(ai_response)
            
            # 处理TTS结果的兼容性 - 支持字符串和字典两种格式
            if tts_result:
                audio_path = None
                
                # 如果返回的是字典格式
                if isinstance(tts_result, dict):
                    if tts_result.get('success'):
                        audio_path = tts_result.get('audio_path')
                    else:
                        emit('error', {'message': f'语音合成失败: {tts_result.get("error", "未知错误")}'})
                        emit('status', {'message': '处理完成', 'type': 'success'})
                        return
                
                # 如果返回的是字符串格式（旧版本兼容）
                elif isinstance(tts_result, str):
                    # 从URL推导出文件路径
                    if tts_result.startswith('/static/audio/'):
                        filename = tts_result.replace('/static/audio/', '')
                        audio_path = os.path.join('static', 'audio', filename)
                
                # 处理音频文件
                if audio_path and os.path.exists(audio_path):
                    with open(audio_path, 'rb') as f:
                        audio_base64 = base64.b64encode(f.read()).decode('utf-8')
                    
                    emit('tts_result', {
                        'audio': f"data:audio/wav;base64,{audio_base64}",
                        'text': ai_response
                    })
                    
                    # 清理临时文件
                    try:
                        os.unlink(audio_path)
                    except:
                        pass
                else:
                    emit('error', {'message': '语音合成文件生成失败'})
            else:
                emit('error', {'message': '语音合成失败'})
            
            emit('status', {'message': '处理完成', 'type': 'success'})
            
        finally:
            # 清理临时音频文件
            try:
                os.unlink(temp_audio_path)
            except:
                pass
                
    except Exception as e:
        logger.error(f"处理语音消息时出错: {e}")
        emit('error', {'message': f'处理失败: {str(e)}'})

@socketio.on('text_message')
def handle_text_message(data):
    """处理文本消息"""
    try:
        user_text = data.get('text', '').strip()
        if not user_text:
            emit('error', {'message': '文本内容不能为空'})
            return
        
        logger.info(f"收到文本消息: {user_text}")
        
        # AI对话 - 使用默认角色
        emit('status', {'message': 'AI正在思考...', 'type': 'info'})
        default_character = {
            'name': 'AI助手',
            'description': '智能语音助手',
            'background': '我是一个智能AI助手，专门为用户提供语音交互服务',
            'personality': '友善、耐心、乐于助人',
            'expertise': '语音识别、自然语言处理、智能对话'
        }
        ai_response = ai_service.generate_response(default_character, user_text, request.sid)
        
        if not ai_response:
            emit('error', {'message': 'AI服务响应失败'})
            return
        
        logger.info(f"AI回复: {ai_response}")
        emit('ai_response', {'text': ai_response})
        
        # 语音合成
        emit('status', {'message': '正在生成语音...', 'type': 'info'})
        tts_result = tts_service.text_to_speech(ai_response)
        
        # 处理TTS结果的兼容性
        if tts_result:
            audio_path = None
            
            # 如果返回的是字典格式
            if isinstance(tts_result, dict):
                if tts_result.get('success'):
                    audio_path = tts_result.get('audio_path')
                else:
                    emit('error', {'message': f'语音合成失败: {tts_result.get("error", "未知错误")}'})
                    emit('status', {'message': '处理完成', 'type': 'success'})
                    return
            
            # 如果返回的是字符串格式（旧版本兼容）
            elif isinstance(tts_result, str):
                # 从URL推导出文件路径
                if tts_result.startswith('/static/audio/'):
                    filename = tts_result.replace('/static/audio/', '')
                    audio_path = os.path.join('static', 'audio', filename)
            
            # 处理音频文件
            if audio_path and os.path.exists(audio_path):
                with open(audio_path, 'rb') as f:
                    audio_base64 = base64.b64encode(f.read()).decode('utf-8')
                
                emit('tts_result', {
                    'audio': f"data:audio/wav;base64,{audio_base64}",
                    'text': ai_response
                })
                
                # 清理临时文件
                try:
                    os.unlink(audio_path)
                except:
                    pass
            else:
                emit('error', {'message': '语音合成文件生成失败'})
        else:
            emit('error', {'message': '语音合成失败'})
        
        emit('status', {'message': '处理完成', 'type': 'success'})
        
    except Exception as e:
        logger.error(f"处理文本消息时出错: {e}")
        emit('error', {'message': f'处理失败: {str(e)}'})

# 实时语音WebSocket事件
@socketio.on('start_realtime_voice')
def handle_start_realtime_voice(data):
    """开始实时语音会话"""
    try:
        if not realtime_voice_handler:
            emit('error', {'message': '实时语音服务未启用'})
            return
        
        character_id = data.get('character_id')
        if not character_id:
            emit('error', {'message': '缺少角色ID'})
            return
        
        # 获取角色信息
        if character_service:
            character = character_service.get_character_by_id(character_id)
        else:
            # 从文件加载角色
            characters_list = load_characters()
            character = None
            for char in characters_list:
                if char['id'] == character_id:
                    character = char
                    break
        
        if not character:
            emit('error', {'message': '角色不存在'})
            return
        
        # 创建回调函数
        def voice_callback(result):
            emit('realtime_voice_result', result)
        
        # 创建实时语音会话
        session_id = realtime_voice_handler.create_session(character_id, character, voice_callback)
        
        # 记录连接ID
        if session_id in realtime_voice_handler.active_sessions:
            realtime_voice_handler.active_sessions[session_id]['connection_id'] = request.sid
        
        emit('realtime_voice_started', {
            'session_id': session_id,
            'character': character,
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"开始实时语音会话: {session_id} for {character['name']}")
        
    except Exception as e:
        logger.error(f"开始实时语音会话失败: {e}")
        emit('error', {'message': str(e)})

@socketio.on('realtime_audio_data')
def handle_realtime_audio_data(data):
    """处理实时音频数据"""
    try:
        if not realtime_voice_handler:
            emit('error', {'message': '实时语音服务未启用'})
            return
        
        session_id = data.get('session_id')
        audio_base64 = data.get('audio_data')
        
        if not session_id or not audio_base64:
            emit('error', {'message': '缺少会话ID或音频数据'})
            return
        
        # 解码音频数据
        import base64
        audio_data = base64.b64decode(audio_base64)
        
        # 创建回调函数
        def audio_callback(result):
            emit('realtime_voice_result', result)
        
        # 处理音频流
        realtime_voice_handler.process_audio_stream(session_id, audio_data, audio_callback)
        
    except Exception as e:
        logger.error(f"处理实时音频数据失败: {e}")
        emit('error', {'message': str(e)})

@socketio.on('stop_realtime_voice')
def handle_stop_realtime_voice(data):
    """停止实时语音会话"""
    try:
        if not realtime_voice_handler:
            emit('error', {'message': '实时语音服务未启用'})
            return
        
        session_id = data.get('session_id')
        if not session_id:
            emit('error', {'message': '缺少会话ID'})
            return
        
        # 结束会话
        realtime_voice_handler.end_session(session_id)
        
        emit('realtime_voice_stopped', {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"停止实时语音会话: {session_id}")
        
    except Exception as e:
        logger.error(f"停止实时语音会话失败: {e}")
        emit('error', {'message': str(e)})

@socketio.on('update_voice_config')
def handle_update_voice_config(data):
    """更新语音配置"""
    try:
        if not realtime_voice_handler:
            emit('error', {'message': '实时语音服务未启用'})
            return
        
        session_id = data.get('session_id')
        config = data.get('config', {})
        
        if not session_id:
            emit('error', {'message': '缺少会话ID'})
            return
        
        # 更新会话配置
        realtime_voice_handler.update_session_config(session_id, config)
        
        emit('voice_config_updated', {
            'session_id': session_id,
            'config': config,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"更新语音配置失败: {e}")
        emit('error', {'message': str(e)})

def main():
    """主函数"""
    print("=" * 50)
    print("🎤 AI语音聊天应用启动中...")
    print("=" * 50)
    
    # 检查环境变量
    required_env_vars = [
        'BAIDU_API_KEY',
        'BAIDU_SECRET_KEY',
        'OPENAI_API_KEY'
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"✗ 缺少必要的环境变量: {', '.join(missing_vars)}")
        print("请在.env文件中配置这些变量")
        return
    
    print("✓ 环境变量检查通过")
    
    # 初始化服务
    if not init_services():
        print("✗ 服务初始化失败，程序退出")
        return
    
    # 初始化实时语音处理器
    print("🔍 初始化实时语音处理器...")
    if init_realtime_voice_handler():
        print("✓ 实时语音处理器已启用")
    else:
        print("⚠️ 实时语音处理器启用失败，但不影响基本功能")
    
    # 获取可用端口
    port_manager = PortManager()
    port = port_manager.find_available_port('localhost', 5000) or 5000
    
    print(f"✓ 使用端口: {port}")
    print("=" * 50)
    print(f"🚀 应用已启动!")
    print(f"📱 标准语音聊天: http://localhost:{port}")
    print(f"⚡ 实时语音对话: http://localhost:{port}/realtime")
    print(f"🔒 HTTPS访问地址: https://localhost:{port + 1}")
    print(f"🎯 功能: 语音识别 + AI对话 + 语音合成 + 实时语音流")
    print("=" * 50)
    print("💡 麦克风权限提示:")
    print("   • 如果麦克风无法使用，请尝试HTTPS地址")
    print("   • 点击地址栏左侧图标允许麦克风权限")
    print("   • 首次访问可能需要手动信任证书")
    print("=" * 50)
    
    # 启动应用
    try:
        # 创建SSL上下文（自签名证书，仅用于开发）
        import ssl
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        
        # 尝试使用临时证书
        try:
            # 生成临时自签名证书
            import tempfile
            import subprocess
            
            # 创建临时证书文件
            cert_file = tempfile.NamedTemporaryFile(suffix='.crt', delete=False)
            key_file = tempfile.NamedTemporaryFile(suffix='.key', delete=False)
            cert_file.close()
            key_file.close()
            
            # 生成自签名证书（需要openssl）
            try:
                subprocess.run([
                    'openssl', 'req', '-x509', '-newkey', 'rsa:4096', 
                    '-keyout', key_file.name, '-out', cert_file.name,
                    '-days', '365', '-nodes', '-subj', '/CN=localhost'
                ], check=True, capture_output=True)
                
                context.load_cert_chain(cert_file.name, key_file.name)
                
                # 启动HTTPS服务器
                import threading
                
                def run_https():
                    socketio.run(
                        app,
                        host='0.0.0.0',
                        port=port + 1,
                        debug=False,
                        ssl_context=context,
                        allow_unsafe_werkzeug=True
                    )
                
                https_thread = threading.Thread(target=run_https, daemon=True)
                https_thread.start()
                
                print("✓ HTTPS服务器已启动")
                
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("⚠️ 无法生成SSL证书，仅启动HTTP服务器")
            
        except Exception as ssl_error:
            print(f"⚠️ SSL设置失败: {ssl_error}")
        
        # 启动HTTP服务器
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