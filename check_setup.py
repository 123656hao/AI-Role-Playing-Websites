#!/usr/bin/env python3
"""
检查应用设置和依赖
确保所有组件都能正常工作
"""

import os
import sys
import importlib
import logging
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def check_python_version():
    """检查Python版本"""
    logger.info("🐍 检查Python版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        logger.error(f"❌ Python版本过低: {version.major}.{version.minor}")
        logger.error("需要Python 3.8或更高版本")
        return False
    
    logger.info(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """检查依赖包"""
    logger.info("📦 检查依赖包...")
    
    required_packages = {
        'flask': 'Flask',
        'flask_socketio': 'Flask-SocketIO',
        'requests': 'requests',
        'dotenv': 'python-dotenv',
        'openai': 'openai',
        'pydub': 'pydub (可选，用于音频处理)'
    }
    
    missing_packages = []
    
    for package, description in required_packages.items():
        try:
            importlib.import_module(package)
            logger.info(f"✅ {description}")
        except ImportError:
            logger.error(f"❌ {description} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        logger.error("请运行以下命令安装缺失的包:")
        logger.error(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_environment_variables():
    """检查环境变量"""
    logger.info("🔑 检查环境变量...")
    
    # 必需的环境变量
    required_vars = {
        'OPENAI_API_KEY': 'AI服务API密钥',
        'BAIDU_API_KEY': '百度语音识别API密钥',
        'BAIDU_SECRET_KEY': '百度语音识别Secret密钥'
    }
    
    # 可选的环境变量
    optional_vars = {
        'SECRET_KEY': 'Flask应用密钥',
        'OPENAI_API_BASE': 'AI服务API基础URL',
        'OPENAI_MODEL': 'AI模型名称'
    }
    
    missing_required = []
    
    # 检查必需变量
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            logger.info(f"✅ {description} - 已设置")
        else:
            logger.error(f"❌ {description} - 未设置 ({var})")
            missing_required.append(var)
    
    # 检查可选变量
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            logger.info(f"✅ {description} - 已设置")
        else:
            logger.warning(f"⚠️ {description} - 未设置 ({var})")
    
    if missing_required:
        logger.error("请在.env文件中设置以下必需的环境变量:")
        for var in missing_required:
            logger.error(f"  {var}=your_value_here")
        return False
    
    return True

def check_directories():
    """检查目录结构"""
    logger.info("📁 检查目录结构...")
    
    required_dirs = [
        'static/audio',
        'templates',
        'services',
        'utils',
        'data'
    ]
    
    for directory in required_dirs:
        if os.path.exists(directory):
            logger.info(f"✅ {directory}")
        else:
            logger.warning(f"⚠️ {directory} - 不存在，将自动创建")
            os.makedirs(directory, exist_ok=True)
    
    return True

def check_files():
    """检查关键文件"""
    logger.info("📄 检查关键文件...")
    
    required_files = [
        'voice_app.py',
        'services/ai_service.py',
        'services/character_service.py',
        'services/baidu_voice_service.py',
        'services/baidu_tts_service.py',
        'templates/voice_chat.html',
        'static/js/voice_chat.js',
        'static/js/audio_converter.js',
        'utils/audio_converter.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            logger.info(f"✅ {file_path}")
        else:
            logger.error(f"❌ {file_path} - 文件不存在")
            missing_files.append(file_path)
    
    if missing_files:
        logger.error("缺少关键文件，应用可能无法正常运行")
        return False
    
    return True

def test_services():
    """测试服务初始化"""
    logger.info("🧪 测试服务初始化...")
    
    try:
        # 测试AI服务
        from services.ai_service import AIRoleplayService
        ai_service = AIRoleplayService()
        logger.info("✅ AI服务初始化成功")
    except Exception as e:
        logger.error(f"❌ AI服务初始化失败: {e}")
        return False
    
    try:
        # 测试角色服务
        from services.character_service import CharacterService
        character_service = CharacterService()
        characters = character_service.get_all_characters()
        logger.info(f"✅ 角色服务初始化成功，加载了{len(characters)}个角色")
    except Exception as e:
        logger.error(f"❌ 角色服务初始化失败: {e}")
        return False
    
    try:
        # 测试语音服务
        from services.baidu_voice_service import BaiduVoiceService
        voice_service = BaiduVoiceService()
        status = voice_service.get_service_status()
        if status['configured']:
            logger.info("✅ 百度语音识别服务配置正确")
        else:
            logger.warning("⚠️ 百度语音识别服务未配置")
    except Exception as e:
        logger.error(f"❌ 语音服务初始化失败: {e}")
        return False
    
    try:
        # 测试TTS服务
        from services.baidu_tts_service import BaiduTTSService
        tts_service = BaiduTTSService()
        status = tts_service.get_service_status()
        if status['configured']:
            logger.info("✅ 百度语音合成服务配置正确")
        else:
            logger.warning("⚠️ 百度语音合成服务未配置")
    except Exception as e:
        logger.error(f"❌ TTS服务初始化失败: {e}")
        return False
    
    return True

def main():
    """主检查函数"""
    logger.info("🔍 开始检查应用设置...")
    logger.info("=" * 50)
    
    checks = [
        ("Python版本", check_python_version),
        ("依赖包", check_dependencies),
        ("环境变量", check_environment_variables),
        ("目录结构", check_directories),
        ("关键文件", check_files),
        ("服务初始化", test_services)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        logger.info(f"\n📋 {check_name}检查:")
        if not check_func():
            all_passed = False
    
    logger.info("\n" + "=" * 50)
    
    if all_passed:
        logger.info("🎉 所有检查通过！应用已准备就绪")
        logger.info("🚀 可以运行以下命令启动应用:")
        logger.info("   python voice_app.py")
        logger.info("   或")
        logger.info("   python start_voice_chat.py")
        return True
    else:
        logger.error("❌ 部分检查未通过，请修复上述问题后重试")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)