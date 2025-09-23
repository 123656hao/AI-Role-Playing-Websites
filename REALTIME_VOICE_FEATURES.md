# 🎙️ 实时语音交互功能说明

## 功能概述

AI角色扮演聊天网站现已支持完整的实时语音交互功能，用户可以通过语音与AI角色进行自然对话。

## 🌟 新增功能

### 1. 增强语音服务 (EnhancedVoiceService)
- **多重语音识别**: 支持字节跳动ASR API、Google语音识别、Sphinx离线识别
- **智能语音合成**: 优先使用字节跳动TTS API，备用本地pyttsx3
- **实时语音会话**: 支持WebSocket实时语音通信
- **角色个性化语音**: 根据角色特点选择合适的语音类型

### 2. WebSocket实时通信
- **双向通信**: 支持音频数据和文字消息的实时传输
- **会话管理**: 自动管理语音会话的生命周期
- **错误处理**: 完善的错误处理和重连机制
- **状态同步**: 实时同步客户端和服务器状态

### 3. 前端语音交互
- **一键录音**: 点击按钮即可开始/停止录音
- **实时反馈**: 录音状态的视觉反馈
- **自动播放**: AI回复的语音自动播放
- **混合输入**: 支持语音和文字混合输入

## 🚀 使用方式

### 基础语音对话
1. 在主页面选择角色并开始对话
2. 点击麦克风按钮进行语音输入
3. 系统自动识别语音并转换为文字
4. AI生成回复并自动播放语音

### 实时语音对话
1. 访问 `/demo` 页面进入演示模式
2. 选择角色并连接WebSocket
3. 启动语音会话
4. 进行实时语音对话

## 🔧 技术架构

### 后端架构
```
Flask应用 (app.py)
├── AI服务 (AIRoleplayService)
├── 基础语音服务 (VoiceService)
├── 增强语音服务 (EnhancedVoiceService)
├── WebSocket处理器 (WebSocketHandler)
└── 角色服务 (CharacterService)
```

### 前端架构
```
主应用 (static/js/app.js)
├── 基础语音录制
├── WebSocket通信
├── 实时语音处理
└── UI状态管理

演示页面 (templates/realtime_demo.html)
├── 完整功能演示
├── 状态监控
├── 日志系统
└── 调试工具
```

## 📋 API接口

### 实时语音相关
- `POST /api/realtime/start` - 启动实时语音会话
- `GET /api/realtime/status` - 获取实时语音服务状态
- `POST /api/voice/enhanced/synthesize` - 增强语音合成
- `POST /api/voice/enhanced/recognize` - 增强语音识别

### WebSocket消息类型
- `start_voice_session` - 开始语音会话
- `audio_data` - 音频数据传输
- `text_message` - 文字消息
- `stop_voice_session` - 停止语音会话
- `ping/pong` - 心跳检测

## 🎯 功能特点

### 智能语音处理
- **多级降级**: API失败时自动切换到备用方案
- **格式兼容**: 支持多种音频格式的处理
- **质量优化**: 自动选择最佳的语音识别和合成方案

### 角色个性化
- **语音匹配**: 根据角色性别和特点选择合适语音
- **说话风格**: 结合角色背景调整语音合成参数
- **情感表达**: 支持不同情感色彩的语音输出

### 用户体验
- **低延迟**: WebSocket确保实时通信
- **容错性**: 网络异常时的自动重连
- **可视化**: 丰富的状态指示和反馈

## 🛠️ 配置说明

### 环境变量配置
```env
# 豆包AI API
ARK_API_KEY=your_api_key
OPENAI_API_BASE=https://ark.cn-beijing.volces.com/api/v3
OPENAI_MODEL=doubao-seed-1-6-250615
```

### 语音API配置 (config/voice_settings.json)
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

## 📦 依赖要求

### Python包
```
websockets==12.0      # WebSocket支持
speech_recognition    # 语音识别
pyttsx3              # 本地语音合成
pyaudio              # 音频处理（可选）
```

### 浏览器要求
- 支持WebRTC的现代浏览器
- 麦克风访问权限
- WebSocket支持

## 🔍 故障排除

### 常见问题

1. **语音识别不工作**
   - 检查麦克风权限
   - 确认浏览器支持WebRTC
   - 检查网络连接

2. **WebSocket连接失败**
   - 确认WebSocket服务器已启动
   - 检查防火墙设置
   - 验证端口8765是否可用

3. **语音合成无声音**
   - 检查音频设备
   - 确认浏览器音频权限
   - 验证API配置

### 调试工具
- 访问 `/demo` 页面查看详细状态
- 查看浏览器控制台日志
- 检查服务器日志输出

## 🚀 未来规划

### 短期目标
- [ ] 完善字节跳动语音API集成
- [ ] 添加更多语音效果和音色
- [ ] 优化语音识别准确率
- [ ] 支持多语言语音交互

### 长期目标
- [ ] 语音情感识别
- [ ] 实时语音翻译
- [ ] 群组语音聊天
- [ ] 语音克隆技术

## 📞 技术支持

如有问题或建议，请：
1. 查看项目文档
2. 检查日志输出
3. 使用演示页面调试
4. 提交Issue反馈

---

**🎉 现在就开始体验全新的实时语音交互功能吧！**