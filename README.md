# AI语音聊天应用

一个基于Flask和百度语音识别的AI角色扮演聊天应用，支持语音识别、语音合成和实时对话。

## 🌟 主要特性

- 🎤 **语音识别**: 基于百度语音识别API，支持实时语音转文字
- 🔊 **语音合成**: 基于百度语音合成API，AI回复可转换为语音
- 🤖 **AI角色扮演**: 支持多个预设AI角色，包括苏格拉底、爱因斯坦、哈利·波特等
- 💬 **实时通信**: 基于WebSocket的实时聊天体验
- 🎨 **现代界面**: 响应式设计，支持移动端和桌面端
- 🔄 **音频格式转换**: 自动处理不同音频格式，确保兼容性

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd ai-voice-chat

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API密钥

复制 `.env.example` 为 `.env` 并填入你的API密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# Flask应用配置
SECRET_KEY=your-secret-key-here

# AI服务配置（豆包/OpenAI）
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://ark.cn-beijing.volces.com/api/v3
OPENAI_MODEL=doubao-seed-1-6-250615

# 百度语音API配置
BAIDU_API_KEY=your_baidu_api_key_here
BAIDU_SECRET_KEY=your_baidu_secret_key_here
```

### 3. 获取API密钥

#### 百度语音识别API
1. 访问 [百度AI开放平台](https://ai.baidu.com/)
2. 注册账号并创建应用
3. 获取 API Key 和 Secret Key

#### AI服务API（豆包）
1. 访问 [火山引擎](https://www.volcengine.com/)
2. 开通豆包大模型服务
3. 获取 API Key

### 4. 启动应用

```bash
# 方式1: 使用启动脚本（推荐）
python start_voice_chat.py

# 方式2: 直接启动
python voice_app.py

# 方式3: 使用简洁版本
python app_clean.py
```

### 5. 访问应用

打开浏览器访问: http://localhost:5000

## 📱 使用说明

### 语音聊天
1. 选择一个AI角色
2. 点击并按住"🎤 按住说话"按钮
3. 说话完毕后松开按钮
4. 系统会自动识别语音并生成AI回复

### 文字聊天
1. 选择一个AI角色
2. 在输入框中输入消息
3. 点击"发送"按钮或按回车键

### 支持的音频格式
- WAV (推荐)
- MP3
- OGG
- WebM (自动转换)
- M4A
- FLAC
- AMR

## 🛠️ 技术架构

### 后端技术
- **Flask**: Web框架
- **Flask-SocketIO**: WebSocket实时通信
- **百度语音识别API**: 语音转文字
- **百度语音合成API**: 文字转语音
- **OpenAI API**: AI对话生成

### 前端技术
- **HTML5**: 现代Web标准
- **CSS3**: 响应式设计和动画
- **JavaScript**: 交互逻辑和音频处理
- **WebRTC**: 浏览器音频录制
- **Socket.IO**: 实时通信

### 音频处理
- **pydub**: Python音频处理
- **Web Audio API**: 浏览器端音频转换
- **自定义音频转换器**: 格式兼容性处理

## 📁 项目结构

```
ai-voice-chat/
├── services/              # 服务层
│   ├── ai_service.py     # AI对话服务
│   ├── baidu_voice_service.py  # 百度语音识别
│   ├── baidu_tts_service.py    # 百度语音合成
│   └── character_service.py    # 角色管理
├── templates/            # HTML模板
│   └── voice_chat.html  # 主界面
├── static/              # 静态资源
│   ├── js/             # JavaScript文件
│   └── audio/          # 音频文件存储
├── utils/              # 工具类
│   └── audio_converter.py  # 音频转换工具
├── data/               # 数据文件
│   └── characters.json # 角色数据
├── voice_app.py        # 主应用（完整版）
├── app_clean.py        # 简洁版应用
├── start_voice_chat.py # 启动脚本
└── requirements.txt    # 依赖包
```

## 🎭 预设角色

- **苏格拉底**: 古希腊哲学家，擅长哲学思辨
- **爱因斯坦**: 物理学家，科学思维和创新
- **哈利·波特**: 魔法世界的冒险者
- **莎士比亚**: 文学大师，诗歌和戏剧
- **孔子**: 儒家思想家，教育和道德
- **玛丽·居里**: 科学家，坚持和突破
- **李老师**: 中文教师，语言学习

## 🔧 故障排除

### 语音识别不工作
1. 检查百度API密钥配置
2. 确认麦克风权限已授权
3. 检查网络连接
4. 查看浏览器控制台错误信息

### 音频格式问题
1. 推荐使用WAV格式录音
2. 确保采样率为16kHz
3. 检查音频文件大小（<4MB）

### AI回复异常
1. 检查OpenAI API密钥配置
2. 确认API额度充足
3. 检查网络连接

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件
- 🌐 **实时通信**: WebSocket支持实时语音交流

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 网络连接（用于AI API调用）

### 安装运行

1. **克隆项目**
```bash
git clone <repository-url>
cd ai_roleplay_project
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境**
```bash
# 复制环境配置文件
cp .env.example .env
# 编辑 .env 文件，填入你的API密钥
```

4. **运行应用**
```bash
# 标准启动
python app.py

# 或使用启动脚本
python run.py

# 测试Web实时语音识别
python start_web_realtime_test.py
```

5. **访问应用**
- 主应用: `http://localhost:5000`
- Web实时语音演示: `http://localhost:5000/web_realtime_demo.html`

## ⚙️ 环境配置

在 `.env` 文件中配置：

```env
# AI服务配置
DOUBAO_API_KEY=your_doubao_api_key
DOUBAO_API_BASE=https://ark.cn-beijing.volces.com/api/v3

# 应用配置
SECRET_KEY=your_secret_key
DEBUG=False
PORT=5000
```

## 📁 项目结构

```
ai_roleplay_project/
├── app.py                          # 主应用文件
├── requirements.txt                # 依赖包
├── .env                           # 环境配置
├── services/                      # 核心服务
│   ├── ai_service.py             # AI对话服务
│   ├── enhanced_voice_service.py  # 增强语音服务
│   ├── chinese_voice_service.py   # 中文语音识别
│   ├── character_service.py       # 角色管理
│   └── websocket_handler.py       # WebSocket处理
├── templates/                     # 页面模板
│   ├── index.html                # 主页面
│   └── realtime_demo.html        # 实时语音演示
├── static/                       # 静态资源
│   ├── css/
│   ├── js/
│   └── audio/
└── data/                         # 数据文件
    └── characters.json           # 角色数据
```

## 🎯 使用说明

### 基本对话
1. 选择AI角色
2. 开始文字或语音对话
3. 享受智能交流体验

### 语音功能
- **语音输入**: 点击麦克风按钮，说中文即可识别
- **语音输出**: AI回复自动播放语音
- **实时对话**: 支持连续语音交流

### 角色特色
- **哲学家**: 深度思考，人生哲理
- **科学家**: 科学知识，技术解答  
- **文学家**: 文学创作，诗词鉴赏
- **历史学家**: 历史文化，古今传承

## 🔧 核心API

### 对话接口
- `POST /api/chat/message` - 文字消息
- `POST /api/chat/voice_message` - 语音消息

### 语音接口  
- `POST /api/voice/enhanced/recognize` - 中文语音识别
- `POST /api/voice/enhanced/synthesize` - 语音合成

### 角色接口
- `GET /api/characters` - 获取角色列表
- `POST /api/chat/start` - 开始对话

## 🛠️ 技术特点

### 语音识别优化
- 支持多种音频格式（WebM、OGG、MP3、WAV等）
- 自动音频格式转换和RIFF头修复
- 优先使用Google中文识别API
- 音频预处理和噪音过滤

### 中文语音处理
- 针对中文语音特点优化
- 音量标准化和动态范围压缩
- 静音检测和自然停顿保留
- 多引擎识别结果对比

### 实时语音识别
- **Web Audio API + WebSocket方案**: 基于浏览器端音频流的实时识别
- **连续语音流处理**: 支持长时间连续语音输入
- **低延迟识别**: 实时音频数据传输和处理
- **多格式兼容**: 自动处理不同浏览器的音频格式

## 🐛 故障排除

### 语音识别问题
```bash
# 检查音频格式
# 确认麦克风权限
# 验证网络连接
```

### RIFF格式错误
- 项目已自动修复音频格式问题
- 支持多种输入格式自动转换
- 生成标准WAV文件

### 依赖安装
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## 📝 更新日志

### v2.1 (当前版本)
- 🆕 **全新Web实时语音识别方案**
- 🎤 基于Web Audio API + WebSocket的实时语音流处理
- ⚡ 低延迟音频传输和识别
- 🔄 支持连续语音输入和实时结果反馈
- 🌐 兼容现代浏览器的音频处理

### v2.0
- ✅ 修复RIFF格式错误
- ✅ 优化中文语音识别准确性
- ✅ 简化项目结构，删除冗余文件
- ✅ 改进音频处理流程
- ✅ 增强错误处理机制

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！