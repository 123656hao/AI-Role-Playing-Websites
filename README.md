# AI角色扮演聊天网站

一个基于Flask和AI的角色扮演聊天网站，支持与历史名人和虚拟角色进行智能对话，集成了语音识别和语音合成功能。

## 🌟 主要特性

- 🎭 **多角色对话**: 与苏格拉底、爱因斯坦、居里夫人、莎士比亚等历史名人对话
- 🎤 **语音交互**: 支持语音输入和语音输出，提供沉浸式对话体验
- 🧠 **AI技能系统**: 知识问答、情感陪伴、教学指导、创作协助、语言练习等多种技能
- 🔊 **实时语音**: 集成字节跳动语音API，支持实时语音对话
- 📱 **响应式设计**: 适配桌面和移动设备
- 🎨 **美观界面**: 现代化的UI设计，流畅的用户体验

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Flask 2.3+
- 现代浏览器（支持WebRTC）

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/123656hao/AI-Role-Playing-Websites.git
   cd AI-Role-Playing-Websites
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**
   
   复制 `.env.example` 到 `.env` 并填入你的API密钥：
   ```bash
   cp .env.example .env
   ```
   
   编辑 `.env` 文件：
   ```env
   # AI API配置
   OPENAI_API_KEY=your_api_key_here
   OPENAI_API_BASE=https://ark.cn-beijing.volces.com/api/v3
   OPENAI_MODEL=doubao-seed-1-6-250615
   ```

4. **配置语音API**
   
   编辑 `config/voice_settings.json`，填入字节跳动语音API配置：
   ```json
   {
     "api_config": {
       "app_id": "your_app_id",
       "access_key": "your_access_key",
       "app_key": "your_app_key"
     }
   }
   ```

5. **运行应用**
   ```bash
   python app.py
   ```

6. **访问网站**
   
   打开浏览器访问 `http://localhost:5000`

## 📁 项目结构

```
AI-Role-Playing-Websites/
├── app.py                      # Flask主应用
├── requirements.txt            # Python依赖
├── .env.example               # 环境变量示例
├── config/
│   └── voice_settings.json   # 语音配置
├── services/
│   ├── ai_service.py         # AI对话服务
│   ├── voice_service.py      # 语音处理服务
│   ├── voice_config_service.py # 语音配置服务
│   ├── voice_chat_client.py  # 语音聊天客户端
│   └── character_service.py  # 角色管理服务
├── templates/
│   └── index.html            # 主页模板
├── static/
│   ├── js/
│   │   └── app.js           # 前端JavaScript
│   └── css/
├── data/
│   └── characters.json      # 角色数据
├── examples/                # 使用示例
├── logs/                   # 日志文件
└── docs/                   # 文档
```

## 🎭 支持的角色

| 角色 | 分类 | 特色 |
|------|------|------|
| 苏格拉底 | 哲学家 | 善于提问，引导思考 |
| 爱因斯坦 | 科学家 | 物理学专家，富有想象力 |
| 居里夫人 | 科学家 | 化学物理学家，坚韧不拔 |
| 莎士比亚 | 文学家 | 戏剧诗歌大师，语言优美 |
| 孔子 | 哲学家 | 儒家思想，教育智慧 |
| 哈利·波特 | 虚拟角色 | 魔法世界，年轻活力 |

## 🛠️ 技术栈

### 后端
- **Flask**: Web框架
- **OpenAI API**: AI对话生成
- **字节跳动语音API**: 语音识别和合成
- **SpeechRecognition**: 本地语音识别
- **pyttsx3**: 本地语音合成

### 前端
- **HTML5/CSS3**: 现代Web标准
- **JavaScript ES6+**: 前端交互
- **Bootstrap 5**: UI框架
- **WebRTC**: 语音录制
- **WebSocket**: 实时通信

## 🎤 语音功能

### 语音识别
- 支持中文和英文语音识别
- 优先使用字节跳动ASR API
- 本地SpeechRecognition作为备用

### 语音合成
- 字节跳动TTS API提供高质量语音
- 支持多种音色（男声/女声）
- 角色个性化语音配置

### 实时语音对话
- WebSocket实时通信
- 低延迟语音交互
- 自动语音播放控制

## 🔧 配置说明

### AI配置
在 `.env` 文件中配置AI服务：
```env
OPENAI_API_KEY=your_doubao_api_key
OPENAI_API_BASE=https://ark.cn-beijing.volces.com/api/v3
OPENAI_MODEL=doubao-seed-1-6-250615
```

### 语音配置
在 `config/voice_settings.json` 中配置语音服务：
```json
{
  "api_config": {
    "base_url": "wss://openspeech.bytedance.com/api/v3/realtime/dialogue",
    "app_id": "your_app_id",
    "access_key": "your_access_key",
    "app_key": "your_app_key"
  },
  "voice_speakers": {
    "male": "zh_male_yunzhou_jupiter_bigtts",
    "female": "zh_female_aojiaonvyou_tob"
  }
}
```

## 📚 使用指南

### 基础对话
1. 选择想要对话的角色
2. 点击"开始对话"
3. 输入文字或使用语音输入
4. 享受与AI角色的智能对话

### 语音功能
1. 点击麦克风图标开始录音
2. 说话后点击停止录音
3. 系统自动识别语音并转为文字
4. AI回复可自动播放语音

### 技能系统
- **知识问答**: 向角色提问专业问题
- **情感陪伴**: 获得情感支持和安慰
- **教学指导**: 学习特定主题知识
- **创作协助**: 协助文学创作
- **语言练习**: 多语言学习练习

## 🔍 故障排除

### 常见问题

1. **语音功能不可用**
   - 检查浏览器麦克风权限
   - 确认语音API配置正确
   - 尝试使用HTTPS访问

2. **AI回复异常**
   - 检查API密钥配置
   - 确认网络连接正常
   - 查看控制台错误信息

3. **角色加载失败**
   - 检查 `data/characters.json` 文件
   - 确认文件格式正确
   - 重启应用服务

### 日志查看
应用日志保存在 `logs/` 目录下，可以查看详细的错误信息。

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [OpenAI](https://openai.com/) - AI对话技术
- [字节跳动](https://www.volcengine.com/) - 语音技术支持
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [Bootstrap](https://getbootstrap.com/) - UI框架

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- GitHub Issues: [提交问题](https://github.com/123656hao/AI-Role-Playing-Websites/issues)
- 项目主页: [AI角色扮演聊天网站](https://github.com/123656hao/AI-Role-Playing-Websites)

---

⭐ 如果这个项目对你有帮助，请给它一个星标！