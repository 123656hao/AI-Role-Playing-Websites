# AI角色扮演聊天网站 - 项目环境备份

## 项目概述

这是一个基于Flask和AI的角色扮演聊天网站，支持与历史名人和虚拟角色进行智能对话，集成了完整的实时语音交互功能。

**备份时间**: 2025年9月23日 (星期二)
**版本**: v2.0 - 实时语音交互版

## 🏗️ 项目结构

```
AI-Role-Playing-Websites/
├── app.py                      # Flask主应用 (✅ 已配置WebSocket支持)
├── requirements.txt            # Python依赖 (✅ 已添加websockets)
├── .env.example               # 环境变量示例 (✅ 已配置)
├── .env                       # 实际环境变量 (✅ 已配置豆包API)
├── .gitignore                 # Git忽略文件
├── LICENSE                    # MIT许可证
├── README.md                  # 项目说明文档
├── REALTIME_VOICE_FEATURES.md # 实时语音功能说明 (🆕 新增)
├── GIT_SETUP_GUIDE.md         # Git设置指南
├── QUICK_START_GUIDE.md       # 快速启动指南
├── setup_git.bat              # Windows Git设置脚本
├── setup_git.ps1              # PowerShell Git设置脚本
├── restore_environment.bat    # 环境恢复脚本
├── restore_environment.ps1    # PowerShell环境恢复脚本
├── check_config.py            # 配置检查脚本
├── test_api.py                # API测试脚本
├── debug_api.py               # API调试脚本
├── config/
│   └── voice_settings.json   # 语音配置 (✅ 已配置字节跳动API)
├── services/
│   ├── ai_service.py         # AI对话服务 (✅ 已配置豆包API)
│   ├── voice_service.py      # 基础语音处理服务
│   ├── enhanced_voice_service.py # 增强语音服务 (🆕 新增)
│   ├── websocket_handler.py  # WebSocket处理器 (🆕 新增)
│   ├── voice_config_service.py # 语音配置服务
│   ├── voice_chat_client.py  # 语音聊天客户端
│   └── character_service.py  # 角色管理服务
├── templates/
│   ├── index.html            # 主页模板 (✅ 已完善)
│   └── realtime_demo.html    # 实时语音演示页面 (🆕 新增)
├── static/
│   ├── js/
│   │   └── app.js           # 前端JavaScript (✅ 已添加实时语音功能)
│   ├── css/                 # 样式文件
│   ├── images/              # 图片资源
│   └── audio/               # 音频文件
├── data/
│   └── characters.json      # 角色数据 (✅ 6个角色已配置)
├── examples/                # 使用示例
├── logs/                    # 日志文件目录
└── __pycache__/            # Python缓存
```

## 🔧 当前环境配置

### Python环境
- **Python版本**: 3.8+
- **虚拟环境**: `.venv/` (已创建)
- **包管理**: pip

### 核心依赖包
```
Flask==2.3.3
Flask-CORS==4.0.0
openai==1.108.2              # ✅ 已升级到最新版本
python-dotenv==1.0.0
SpeechRecognition==3.10.0
pyttsx3==2.90
# pyaudio==0.2.11           # ⚠️ 暂时跳过，需要C++编译工具
pydub==0.25.1
requests==2.31.0
websockets==15.0.1           # 🆕 新增WebSocket支持
python-decouple==3.8
```

### API配置状态

#### AI服务配置 (.env)
```env
# Flask应用配置
SECRET_KEY=ai-roleplay-secret-2024
FLASK_ENV=development

# OpenAI API配置（豆包）
ARK_API_KEY=44ae44d0-4db0-461f-be8b-b1989ecd3e8a     # ✅ 已配置真实密钥
OPENAI_API_KEY=44ae44d0-4db0-461f-be8b-b1989ecd3e8a   # ✅ 已配置真实密钥
OPENAI_API_BASE=https://ark.cn-beijing.volces.com/api/v3
OPENAI_MODEL=doubao-seed-1-6-250615
```

#### 语音服务配置 (config/voice_settings.json)
```json
{
  "api_config": {
    "base_url": "wss://openspeech.bytedance.com/api/v3/realtime/dialogue",
    "app_id": "2440934313",
    "access_key": "snJDH6bnvjspmGT-zSyGUceWVs7O9xNK",
    "resource_id": "volc.speech.dialog",
    "app_key": "PlgvMymc7f3tQnJ6"
  }
}
```
**状态**: ✅ 已配置字节跳动语音API密钥

## 🎭 已配置角色

当前系统包含6个AI角色：

1. **苏格拉底** (socrates) - 哲学家
   - 技能: 知识问答、情感支持、教学指导
   - 语音: 男声，深刻富有哲理

2. **哈利·波特** (harry_potter) - 虚拟角色
   - 技能: 情感支持、创作协助、教学指导
   - 语音: 男声，年轻热情

3. **阿尔伯特·爱因斯坦** (einstein) - 科学家
   - 技能: 知识问答、教学指导、创作协助
   - 语音: 男声，严谨幽默

4. **威廉·莎士比亚** (shakespeare) - 文学家
   - 技能: 创作协助、情感支持、语言练习
   - 语音: 男声，富有诗意

5. **孔子** (confucius) - 哲学家
   - 技能: 知识问答、教学指导、情感支持
   - 语音: 男声，温和威严

6. **玛丽·居里** (marie_curie) - 科学家
   - 技能: 知识问答、教学指导、情感支持
   - 语音: 女声，坚定温柔

## 🚀 启动方式

### Windows环境
```cmd
# 激活虚拟环境
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动应用
python app.py
```

或使用批处理文件：
```cmd
start.bat
```

### 访问地址
- 本地访问: http://localhost:5000
- 网络访问: http://0.0.0.0:5000

## 🎤 语音功能状态

### 语音识别 (ASR)
- ✅ 字节跳动ASR API (主要)
- ✅ 本地SpeechRecognition (备用)
- ✅ 支持中英文识别

### 语音合成 (TTS)
- ✅ 字节跳动TTS API (高质量)
- ✅ 本地pyttsx3 (备用)
- ✅ 角色个性化语音配置

### 实时语音对话
- ✅ WebSocket实时通信
- ✅ 低延迟语音交互
- ✅ 自动语音播放控制

## 📁 重要文件状态

### 已打开的编辑器文件
- ✅ services/voice_service.py - 语音处理服务
- ✅ README.md - 项目说明文档
- ✅ LICENSE - MIT许可证
- ✅ GIT_SETUP_GUIDE.md - Git设置指南
- ✅ setup_git.ps1 - PowerShell Git设置脚本
- ✅ .gitignore - Git忽略文件
- ✅ setup_git.bat - Windows Git设置脚本
- ✅ static/js/app.js - 前端JavaScript

### 当前活动文件
- **README.md** - 项目主要说明文档

## 🔐 安全配置

### 环境变量保护
- ✅ .env 文件已在 .gitignore 中
- ✅ 提供 .env.example 模板
- ⚠️ 需要用户配置真实的API密钥

### API密钥状态
- 🔑 字节跳动语音API: 已配置
- ⚠️ 豆包AI API: 需要用户配置

## 🛠️ 开发工具配置

### Git配置
- ✅ .gitignore 已配置
- ✅ 提供自动化Git设置脚本
- ✅ Windows和PowerShell脚本支持

### 日志系统
- ✅ 日志目录: logs/
- ✅ 应用级别日志配置
- ✅ 错误追踪和调试支持

## 🌐 Web功能

### 前端特性
- ✅ 响应式设计 (Bootstrap 5)
- ✅ 现代化UI界面
- ✅ 实时语音录制 (WebRTC)
- ✅ 角色搜索和筛选
- ✅ 语音播放控制

### 后端API
- ✅ RESTful API设计
- ✅ 会话管理
- ✅ 角色管理
- ✅ 语音处理
- ✅ AI对话生成
- ✅ 技能系统

## 📋 待办事项

### 必须配置
1. **配置豆包AI API密钥** - 在.env文件中设置OPENAI_API_KEY
2. **测试语音功能** - 验证字节跳动语音API是否正常工作
3. **创建角色头像** - 在static/images/目录添加角色头像图片

### 可选优化
1. 添加更多AI角色
2. 优化语音质量和延迟
3. 添加对话历史记录
4. 实现用户账户系统
5. 添加多语言支持

## 🔍 故障排除

### 常见问题
1. **语音功能不可用**: 检查浏览器麦克风权限和HTTPS访问
2. **AI回复异常**: 检查API密钥配置和网络连接
3. **角色加载失败**: 检查data/characters.json文件格式
4. **依赖安装失败**: 确保Python版本3.8+，考虑使用虚拟环境

### 日志查看
- 应用日志: logs/目录
- 控制台输出: 启动应用时的终端输出
- 浏览器控制台: F12开发者工具

## 📞 技术支持

### 相关文档
- README.md - 完整使用指南
- GIT_SETUP_GUIDE.md - Git配置指南
- examples/ - 代码使用示例

### API文档
- 豆包AI API: https://ark.cn-beijing.volces.com/
- 字节跳动语音API: https://openspeech.bytedance.com/

---

**备份说明**: 此文档记录了项目在2025年9月22日的完整环境状态，包括所有配置、依赖和当前功能状态。可用于项目恢复、环境迁移或新团队成员快速了解项目结构。