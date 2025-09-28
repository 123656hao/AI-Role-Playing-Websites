# Unity 3D角色集成指南

## 概述

这个集成方案为你的AI语音聊天应用添加了Unity 3D角色支持，包括：
- 6位虚拟角色的3D模型展示
- 基于性别的语音合成（男性角色使用男声，女性角色使用女声）
- 实时语音动画和表情控制
- 与后端语音服务的无缝集成

## 角色配置

### 男性角色（使用男声）
1. **苏格拉底** - 古希腊哲学家
2. **哈利·波特** - 魔法世界的年轻巫师
3. **爱因斯坦** - 著名物理学家
4. **莎士比亚** - 英国文学大师
5. **孔子** - 中国古代思想家

### 女性角色（使用女声）
1. **玛丽·居里** - 诺贝尔奖获得者
2. **李老师** - 中文教师

## Unity项目设置

### 1. 导入脚本文件

将以下脚本文件复制到Unity项目的 `Assets/Scripts/` 目录：

```
unity_integration/
├── CharacterManager.cs          # 角色管理器
├── CharacterController3D.cs     # 3D角色控制器
├── VoiceManager.cs             # 语音管理器
└── character_config.json       # 角色配置文件
```

### 2. 创建角色管理器

1. 在场景中创建一个空的GameObject，命名为 "CharacterManager"
2. 添加 `CharacterManager` 组件
3. 设置以下属性：
   - **Character Config File**: 拖入 `character_config.json` 文件
   - **Character Spawn Point**: 创建一个空GameObject作为角色生成点
   - **Character Camera**: 设置用于观察角色的摄像机
   - **Voice Audio Source**: 添加AudioSource组件用于播放语音

### 3. 准备角色模型

在 `Assets/Resources/Models/Characters/` 目录下放置角色模型：

```
Resources/
└── Models/
    └── Characters/
        ├── Socrates/           # 苏格拉底模型
        ├── HarryPotter/        # 哈利·波特模型
        ├── Einstein/           # 爱因斯坦模型
        ├── Shakespeare/        # 莎士比亚模型
        ├── Confucius/          # 孔子模型
        ├── MarieCurie/         # 玛丽·居里模型
        └── ChineseTeacher/     # 李老师模型
```

### 4. 设置动画控制器

为每个角色创建Animator Controller：

```
Assets/
└── Controllers/
    ├── MaleCharacterController.controller    # 男性角色动画控制器
    └── FemaleCharacterController.controller  # 女性角色动画控制器
```

#### 动画状态包括：
- **Idle** - 待机动画
- **Speaking** - 说话动画
- **MaleSpeaking** - 男性说话动画
- **FemaleSpeaking** - 女性说话动画
- **Idle_Blink** - 眨眼动画
- **Idle_LookAround** - 环顾动画

### 5. 配置语音管理器

1. 在CharacterManager上添加 `VoiceManager` 组件
2. 设置语音参数：
   - **Male Base Pitch**: 0.8 (男声基础音调)
   - **Female Base Pitch**: 1.2 (女声基础音调)
   - **Male Base Speed**: 0.9 (男声基础语速)
   - **Female Base Speed**: 1.0 (女声基础语速)

## API集成

### 后端配置

确保你的 `voice_app.py` 正在运行，并且包含以下API端点：

- `GET /api/characters/unity` - 获取Unity角色配置
- `POST /api/tts` - 语音合成API

### Unity网络请求

VoiceManager会自动向后端发送TTS请求：

```csharp
// 示例请求数据
{
    "text": "你好，我是苏格拉底",
    "character_id": "socrates",
    "unity_client": true,
    "voice_settings": {
        "pitch": 0.8,
        "speed": 0.9,
        "voice_id": "male_wise"
    }
}
```

## 使用方法

### 切换角色

```csharp
CharacterManager characterManager = FindObjectOfType<CharacterManager>();
characterManager.SwitchToCharacter("socrates");
```

### 播放语音

```csharp
VoiceManager voiceManager = FindObjectOfType<VoiceManager>();
voiceManager.PlayVoiceForCharacter("socrates", "你好，我是苏格拉底。");
```

### 播放动画

```csharp
CharacterManager characterManager = FindObjectOfType<CharacterManager>();
characterManager.PlayCharacterAnimation("Speaking");
```

## 测试

### Web测试页面

访问 `http://localhost:5000/unity-test` 来测试Unity集成：

1. 测试API连接
2. 加载角色列表
3. 测试每个角色的语音合成
4. 验证男女声音的区别

### Unity测试

在Unity编辑器中：

1. 运行场景
2. 调用 `CharacterManager.SwitchToCharacter()` 切换角色
3. 调用 `VoiceManager.PlayVoiceForCharacter()` 播放语音
4. 观察角色动画和语音同步

## 故障排除

### 常见问题

1. **角色模型不显示**
   - 检查模型路径是否正确
   - 确保模型在Resources文件夹中

2. **语音不播放**
   - 检查网络连接到后端API
   - 验证百度TTS服务配置
   - 查看Unity Console的错误信息

3. **动画不播放**
   - 检查Animator Controller设置
   - 确保动画状态名称正确

4. **性别语音错误**
   - 检查角色配置中的gender字段
   - 验证后端TTS服务的语音参数

### 调试技巧

1. 启用Unity Console查看日志
2. 使用Web测试页面验证后端API
3. 检查CharacterManager的事件回调
4. 监控VoiceManager的网络请求

## 扩展功能

### 添加新角色

1. 在 `character_config.json` 中添加角色配置
2. 准备角色3D模型
3. 设置相应的动画控制器
4. 更新后端角色数据

### 自定义语音效果

1. 修改 `VoiceSettings` 参数
2. 添加新的语音预设
3. 实现语音情感控制

### 高级动画

1. 添加更多动画状态
2. 实现面部表情控制
3. 添加手势动画

## 性能优化

1. **模型优化**
   - 使用LOD系统
   - 优化贴图分辨率
   - 减少多边形数量

2. **音频优化**
   - 压缩音频文件
   - 使用音频缓存
   - 异步加载音频

3. **网络优化**
   - 实现请求队列
   - 添加重试机制
   - 使用连接池

## 许可证

本项目遵循MIT许可证。详见LICENSE文件。