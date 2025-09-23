#!/usr/bin/env python3
"""
AI角色扮演聊天网站 - 配置检查脚本
检查项目环境和配置是否正确
"""

import os
import json
import sys
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    print("🐍 检查Python版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (符合要求)")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (需要3.8+)")
        return False

def check_virtual_env():
    """检查虚拟环境"""
    print("📦 检查虚拟环境...")
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("   ✅ 虚拟环境已激活")
        return True
    else:
        print("   ⚠️  未检测到虚拟环境")
        return False

def check_dependencies():
    """检查依赖包"""
    print("📚 检查依赖包...")
    required_packages = [
        'flask', 'flask_cors', 'openai', 'python_dotenv',
        'speech_recognition', 'pyttsx3', 'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (未安装)")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def check_env_file():
    """检查环境变量文件"""
    print("🔐 检查环境配置...")
    env_file = Path('.env')
    
    if not env_file.exists():
        print("   ❌ .env 文件不存在")
        return False
    
    # 读取环境变量
    env_vars = {}
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    # 检查必要的环境变量
    required_vars = ['SECRET_KEY', 'OPENAI_API_KEY', 'OPENAI_API_BASE', 'OPENAI_MODEL']
    all_configured = True
    
    for var in required_vars:
        if var in env_vars:
            if var == 'OPENAI_API_KEY' and env_vars[var] == 'your_doubao_api_key_here':
                print(f"   ⚠️  {var}: 需要配置真实的API密钥")
                all_configured = False
            else:
                print(f"   ✅ {var}: 已配置")
        else:
            print(f"   ❌ {var}: 未配置")
            all_configured = False
    
    return all_configured

def check_voice_config():
    """检查语音配置"""
    print("🎤 检查语音配置...")
    config_file = Path('config/voice_settings.json')
    
    if not config_file.exists():
        print("   ❌ config/voice_settings.json 文件不存在")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 检查API配置
        api_config = config.get('api_config', {})
        required_keys = ['base_url', 'app_id', 'access_key', 'app_key']
        
        all_configured = True
        for key in required_keys:
            if key in api_config and api_config[key]:
                print(f"   ✅ {key}: 已配置")
            else:
                print(f"   ❌ {key}: 未配置")
                all_configured = False
        
        return all_configured
        
    except json.JSONDecodeError:
        print("   ❌ 配置文件格式错误")
        return False

def check_characters_data():
    """检查角色数据"""
    print("🎭 检查角色数据...")
    characters_file = Path('data/characters.json')
    
    if not characters_file.exists():
        print("   ❌ data/characters.json 文件不存在")
        return False
    
    try:
        with open(characters_file, 'r', encoding='utf-8') as f:
            characters = json.load(f)
        
        if isinstance(characters, list) and len(characters) > 0:
            print(f"   ✅ 已配置 {len(characters)} 个角色")
            for char in characters:
                if 'id' in char and 'name' in char:
                    print(f"      - {char['name']} ({char['id']})")
            return True
        else:
            print("   ❌ 角色数据格式错误或为空")
            return False
            
    except json.JSONDecodeError:
        print("   ❌ 角色数据文件格式错误")
        return False

def check_directories():
    """检查必要目录"""
    print("📁 检查项目目录...")
    required_dirs = [
        'static/audio', 'static/css', 'static/js', 'static/images',
        'templates', 'services', 'config', 'data', 'logs'
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"   ✅ {dir_path}")
        else:
            print(f"   ❌ {dir_path} (不存在)")
            all_exist = False
    
    return all_exist

def check_main_files():
    """检查主要文件"""
    print("📄 检查主要文件...")
    required_files = [
        'app.py', 'requirements.txt', 'README.md',
        'templates/index.html', 'static/js/app.js'
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (不存在)")
            all_exist = False
    
    return all_exist

def main():
    """主检查函数"""
    print("=" * 50)
    print("🔍 AI角色扮演聊天网站 - 配置检查")
    print("=" * 50)
    print()
    
    checks = [
        ("Python版本", check_python_version),
        ("虚拟环境", check_virtual_env),
        ("依赖包", check_dependencies),
        ("环境配置", check_env_file),
        ("语音配置", check_voice_config),
        ("角色数据", check_characters_data),
        ("项目目录", check_directories),
        ("主要文件", check_main_files),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"   ❌ 检查失败: {e}")
            results.append((name, False))
        print()
    
    # 总结
    print("=" * 50)
    print("📊 检查结果总结")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:12} : {status}")
    
    print()
    print(f"总体状态: {passed}/{total} 项检查通过")
    
    if passed == total:
        print("🎉 所有检查都通过！项目已准备就绪。")
        print("💡 运行 'python app.py' 启动应用")
    else:
        print("⚠️  存在配置问题，请根据上述检查结果进行修复。")
        print("💡 参考 PROJECT_ENVIRONMENT_BACKUP.md 了解详细配置说明")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)