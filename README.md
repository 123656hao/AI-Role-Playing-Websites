# AI语音聊天应用

一个基于Flask和百度语音识别的AI角色扮演聊天应用，支持语音识别、语音合成和实时对话。

## 🌟 主要特性

- 🎤 **语音识别**: 基于百度语音识别API，支持实时语音转文字
- 🔊 **语音合成**: 基于百度语音合成API，AI回复可转换为语音
- 🤖 **AI角色扮演**: 支持多个预设AI角色，包括苏格拉底、爱因斯坦、哈利·波特等
- 💬 **实时通信**: 基于WebSocket的实时聊天体验
- ⚡ **实时语音对话**: 全新的连续语音交互模式，支持自然对话流程
- 🎯 **智能静音检测**: 自动识别语音停顿，无需手动控制
- 🎨 **现代界面**: 响应式设计，支持移动端和桌面端
- 🔄 **音频格式转换**: 自动处理不同音频格式，确保兼容性
- 🎵 **音频可视化**: 实时显示语音输入的音频波形

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
# 方式1: 启动实时语音对话（推荐）
python start_realtime_voice.py

# 方式2: 直接启动主应用
python voice_app.py

# 方式3: 测试实时语音功能
python test_realtime_voice.py
```

### 5. 访问应用

- **实时语音对话**: http://localhost:5000/realtime （新功能）
- **标准语音聊天**: http://localhost:5000/

## 📱 使用说明

### 🎤 实时语音对话（新功能）
1. 访问 http://localhost:5000/realtime
2. 选择一个AI角色
3. 点击麦克风按钮开始对话
4. 清晰地说出您的问题
5. 系统自动检测语音结束并识别
6. 获得AI的文字和语音回复
7. 开启连续模式进行自然对话

### 语音聊天（标准模式）
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

## 👥 项目分工

### 🔧 后端 & 工作流负责人
**主要职责：**
- **核心服务开发**
  - AI对话服务 (`services/ai_service.py`)
  - 语音识别服务 (`services/baidu_voice_service.py`)
  - 语音合成服务 (`services/baidu_tts_service.py`)
  - 角色管理服务 (`services/character_service.py`)
  - WebSocket处理器 (`services/websocket_handler.py`)

- **后端架构设计**
  - Flask应用架构 (`voice_app.py`, `app.py`)
  - API接口设计和实现
  - 数据库设计和数据管理
  - 实时语音处理逻辑 (`services/realtime_voice_handler.py`)

- **工作流管理**
  - 项目构建和部署流程
  - 环境配置管理 (`.env`, `requirements.txt`)
  - 代码质量控制和测试
  - 文档维护 (`README.md`, `USAGE_GUIDE.md`)

- **系统集成**
  - 第三方API集成（百度语音、AI模型）
  - 音频处理工具 (`utils/audio_converter.py`)
  - 端口管理和服务监控 (`utils/port_manager.py`)

### 🎨 前端负责人
**主要职责：**
- **用户界面开发**
  - 主页面设计 (`templates/index.html`)
  - 语音聊天界面 (`templates/voice_chat.html`)
  - 角色扮演界面 (`templates/simple_roleplay.html`)
  - 实时语音对话界面 (`templates/realtime_voice_chat.html`)

- **交互逻辑实现**
  - 核心应用逻辑 (`static/js/app.js`)
  - 语音聊天功能 (`static/js/voice_chat.js`)
  - 实时语音处理 (`static/js/realtime_voice_chat.js`)
  - 音频转换器 (`static/js/audio_converter.js`)

- **用户体验优化**
  - 响应式设计和移动端适配
  - 音频可视化和实时反馈
  - 语音录制和播放控制
  - 错误处理和用户提示

- **前端技术实现**
  - Web Audio API集成
  - WebSocket客户端通信
  - 音频格式处理和转换
  - 浏览器兼容性处理

### 🤝 协作方式
- **代码审查**: 交叉审查对方的代码提交
- **接口协调**: 共同定义前后端API接口规范
- **测试配合**: 联合进行功能测试和集成测试
- **问题解决**: 协作解决跨端技术问题

### 📋 开发工具
- **版本控制**: Git + GitHub
- **项目管理**: GitHub Issues + Projects
- **代码规范**: Python PEP8 + JavaScript ES6+
- **测试工具**: pytest (后端) + Jest (前端)

## 🤝 贡献


### 贡献指南
1. Fork 项目到你的GitHub账户
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

### 代码规范
- **后端**: 遵循PEP8规范，使用类型提示
- **前端**: 使用ES6+语法，保持代码简洁
- **注释**: 关键功能必须有详细注释
- **测试**: 新功能需要包含相应测试用例
---

#
# 👥 详细项目分工

### 🔧 后端 & 工作流开发者
**负责人：郝仁**

#### 核心职责
- **后端架构设计与实现**
  - Flask应用框架搭建 (`voice_app.py`, `app.py`)
  - RESTful API设计和实现
  - WebSocket实时通信架构
  - 数据库设计和ORM配置

- **AI服务集成**
  - AI对话服务开发 (`services/ai_service.py`)
  - 角色管理系统 (`services/character_service.py`)
  - 智能对话逻辑和上下文管理
  - 多角色扮演功能实现

- **语音服务开发**
  - 百度语音识别集成 (`services/baidu_voice_service.py`)
  - 百度语音合成服务 (`services/baidu_tts_service.py`)
  - 实时语音处理器 (`services/realtime_voice_handler.py`)
  - 音频格式转换和优化 (`utils/audio_converter.py`)

- **工作流和DevOps**
  - 项目构建和部署脚本
  - 环境配置管理 (`.env`, `requirements.txt`)
  - 代码质量控制和自动化测试
  - 文档维护和API文档生成

- **系统监控和优化**
  - 性能监控和日志管理
  - 端口管理和服务监控 (`utils/port_manager.py`)
  - 错误处理和异常监控
  - 系统安全和数据保护

#### 技术栈
- **后端框架**: Flask, Flask-SocketIO
- **AI服务**: OpenAI API, 豆包API
- **语音服务**: 百度语音API
- **数据处理**: pandas, numpy
- **音频处理**: pydub, wave
- **部署工具**: Docker, nginx

---

### 🎨 前端开发者
**负责人：赵伟龙**

#### 核心职责
- **用户界面设计与开发**
  - 响应式网页设计 (`templates/*.html`)
  - 现代化UI/UX界面实现
  - 移动端适配和跨浏览器兼容
  - CSS动画和交互效果

- **前端交互逻辑**
  - 核心应用逻辑 (`static/js/app.js`)
  - 语音聊天功能 (`static/js/voice_chat.js`)
  - 实时语音对话 (`static/js/realtime_voice_chat.js`)
  - 角色选择和管理界面

- **音频处理前端实现**
  - Web Audio API集成
  - 音频录制和播放控制
  - 音频格式转换 (`static/js/audio_converter.js`)
  - 音频可视化和波形显示

- **实时通信客户端**
  - WebSocket客户端实现
  - 实时消息处理和显示
  - 连接状态管理和重连机制
  - 数据传输优化

- **用户体验优化**
  - 加载状态和进度提示
  - 错误处理和用户反馈
  - 无障碍访问支持
  - 性能优化和代码分割

#### 技术栈
- **前端框架**: 原生JavaScript (ES6+)
- **样式技术**: CSS3, Flexbox, Grid
- **音频技术**: Web Audio API, MediaRecorder API
- **实时通信**: Socket.IO Client
- **构建工具**: Webpack, Babel
- **测试工具**: Jest, Cypress


### 🧪 测试 & DevOps 开发者
**负责人：陈子昂**

#### 核心职责
**测试策略与执行**
 -制定整体测试计划（单元测试、集成测试、E2E测试）
 -负责集成测试和系统功能测试
 -维护测试用例和测试报告
 -负责性能测试和压力测试

**DevOps与部署**
-项目构建和部署流程（CI/CD）的搭建和维护
-Docker容器化配置和管理
-生产环境的配置、管理和发布
-持续集成和持续部署流水线 (GitHub Actions)
-系统监控与环境管理
-性能监控和日志系统（如Prometheus/Grafana）的集成

#### 技术栈
- **测试工具: pytest, Jest, Cypress**
- **DevOps: Docker, nginx, GitHub Actions**

### 🤝 协作流程

#### 开发协作
1. **需求分析**: 共同分析功能需求，确定前后端接口
2. **接口设计**: 协商API接口规范和数据格式
3. **并行开发**: 各自负责模块的独立开发
4. **集成测试**: 定期进行前后端集成测试
5. **代码审查**: 交叉审查代码质量和规范

#### 沟通机制
- **每日站会**: 同步开发进度和问题
- **技术讨论**: 解决技术难点和架构问题
- **文档协作**: 共同维护技术文档和用户手册
- **问题跟踪**: 使用GitHub Issues跟踪bug和功能请求

#### 质量保证
- **代码规范**: 统一的代码风格和命名规范
- **测试覆盖**: 单元测试和集成测试
- **性能监控**: 前后端性能指标监控
- **安全审查**: 代码安全性和数据保护审查

---

### 📊 工作量分配

| 模块 | 后端开发者 | 前端开发者 | 协作程度 |
|------|------------|------------|----------|
| API设计 | 70% | 30% | 高 |
| 语音服务 | 90% | 10% | 中 |
| 用户界面 | 10% | 90% | 低 |
| 实时通信 | 60% | 40% | 高 |
| 音频处理 | 50% | 50% | 高 |
| 测试部署 | 80% | 20% | 中 |
| 文档维护 | 60% | 40% | 中 |

### 🎯 里程碑计划

#### 第一阶段：基础功能 
- **后端**: 完成基础API和语音服务集成
- **前端**: 实现基础UI和语音录制功能

#### 第二阶段：核心功能 
- **后端**: 完成AI对话和角色管理
- **前端**: 实现完整的用户交互流程

#### 第三阶段：优化完善 
- **后端**: 性能优化和错误处理
- **前端**: UI优化和用户体验提升

#### 第四阶段：测试部署 
- **测试**: 集成测试和生产环境部署