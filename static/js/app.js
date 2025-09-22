/**
 * AI角色扮演聊天应用 - 前端JavaScript
 */

class AIRoleplayApp {
    constructor() {
        this.characters = [];
        this.currentCharacter = null;
        this.currentSessionId = null;
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        
        // 语音配置相关
        this.voiceConfig = null;
        this.websocket = null;
        this.voiceSessionId = null;
        this.realtimeVoiceEnabled = false;
        
        this.init();
    }

    async init() {
        this.bindEvents();
        await this.loadCharacters();
        this.setupVoiceRecording();
    }

    bindEvents() {
        // 搜索功能
        document.getElementById('searchInput').addEventListener('input', (e) => {
            this.searchCharacters(e.target.value);
        });

        // 分类筛选
        document.querySelectorAll('.category-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.filterByCategory(e.target.dataset.category);
                this.updateCategoryButtons(e.target);
            });
        });

        // 发送消息
        document.getElementById('sendBtn').addEventListener('click', () => {
            this.sendMessage();
        });

        // 回车发送
        document.getElementById('messageInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // 语音按钮
        document.getElementById('voiceBtn').addEventListener('click', () => {
            this.toggleVoiceRecording();
        });

        // 技能按钮
        document.querySelectorAll('.skill-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.openSkillModal(e.target.dataset.skill);
            });
        });

        // 执行技能
        document.getElementById('executeSkillBtn').addEventListener('click', () => {
            this.executeSkill();
        });

        // 聊天模态框关闭时清理
        document.getElementById('chatModal').addEventListener('hidden.bs.modal', () => {
            this.currentCharacter = null;
            this.currentSessionId = null;
            document.getElementById('messagesContainer').innerHTML = '';
        });
    }

    async loadCharacters() {
        try {
            this.showLoading(true);
            const response = await fetch('/api/characters');
            const data = await response.json();
            
            if (data.success) {
                this.characters = data.characters;
                this.renderCharacters(this.characters);
            } else {
                this.showError('加载角色失败: ' + data.error);
            }
        } catch (error) {
            this.showError('网络错误: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    renderCharacters(characters) {
        const grid = document.getElementById('charactersGrid');
        grid.innerHTML = '';

        characters.forEach(character => {
            const card = this.createCharacterCard(character);
            grid.appendChild(card);
        });
    }

    createCharacterCard(character) {
        const card = document.createElement('div');
        card.className = 'character-card';
        card.innerHTML = `
            <div class="character-avatar">${this.getCharacterEmoji(character.category)}</div>
            <div class="character-name">${character.name}</div>
            <div class="character-category">${this.getCategoryName(character.category)}</div>
            <div class="character-description">${character.background.substring(0, 100)}...</div>
            <div class="character-tags">
                ${character.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
            </div>
            <button class="chat-btn" onclick="app.startChat('${character.id}')">
                <i class="fas fa-comments me-2"></i>开始对话
            </button>
        `;
        return card;
    }

    getCharacterEmoji(category) {
        const emojis = {
            'philosophy': '🧠',
            'science': '🔬',
            'literature': '📚',
            'fiction': '🎭',
            'history': '📜'
        };
        return emojis[category] || '👤';
    }

    getCategoryName(category) {
        const names = {
            'philosophy': '哲学家',
            'science': '科学家',
            'literature': '文学家',
            'fiction': '虚拟角色',
            'history': '历史人物'
        };
        return names[category] || '其他';
    }

    searchCharacters(query) {
        if (!query.trim()) {
            this.renderCharacters(this.characters);
            return;
        }

        const filtered = this.characters.filter(character => 
            character.name.toLowerCase().includes(query.toLowerCase()) ||
            character.background.toLowerCase().includes(query.toLowerCase()) ||
            character.tags.some(tag => tag.toLowerCase().includes(query.toLowerCase()))
        );

        this.renderCharacters(filtered);
    }

    filterByCategory(category) {
        if (category === 'all') {
            this.renderCharacters(this.characters);
        } else {
            const filtered = this.characters.filter(character => character.category === category);
            this.renderCharacters(filtered);
        }
    }

    updateCategoryButtons(activeBtn) {
        document.querySelectorAll('.category-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        activeBtn.classList.add('active');
    }

    async startChat(characterId) {
        try {
            const response = await fetch('/api/chat/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ character_id: characterId })
            });

            const data = await response.json();
            
            if (data.success) {
                this.currentCharacter = data.character;
                this.currentSessionId = data.session_id;
                
                // 加载语音配置
                await this.loadVoiceConfig(characterId);
                
                // 更新聊天界面
                this.updateChatHeader(data.character);
                this.clearMessages();
                
                // 显示欢迎消息
                if (data.welcome_message) {
                    this.addMessage(data.welcome_message, 'ai');
                    
                    // 自动播放欢迎消息语音
                    if (this.voiceConfig && this.shouldAutoPlayVoice()) {
                        this.playVoice(data.welcome_message);
                    }
                }
                
                // 显示聊天模态框
                const chatModal = new bootstrap.Modal(document.getElementById('chatModal'));
                chatModal.show();
            } else {
                this.showError('开始对话失败: ' + data.error);
            }
        } catch (error) {
            this.showError('网络错误: ' + error.message);
        }
    }

    updateChatHeader(character) {
        document.getElementById('chatAvatar').textContent = this.getCharacterEmoji(character.category);
        document.getElementById('chatCharacterName').textContent = character.name;
        document.getElementById('chatCharacterCategory').textContent = this.getCategoryName(character.category);
    }

    async sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();
        
        if (!message || !this.currentSessionId) return;

        // 添加用户消息到界面
        this.addMessage(message, 'user');
        input.value = '';

        // 显示AI正在输入
        const typingId = this.showTyping();

        try {
            const response = await fetch('/api/chat/message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();
            
            // 移除正在输入提示
            this.removeTyping(typingId);
            
            if (data.success) {
                this.addMessage(data.response, 'ai');
                
                // 自动语音播放（可选）
                if (this.shouldAutoPlayVoice()) {
                    this.playVoice(data.response);
                }
            } else {
                this.addMessage('抱歉，我现在无法回复。请稍后再试。', 'ai');
            }
        } catch (error) {
            this.removeTyping(typingId);
            this.addMessage('网络连接出现问题，请检查网络后重试。', 'ai');
        }
    }

    addMessage(content, type) {
        const container = document.getElementById('messagesContainer');
        const message = document.createElement('div');
        message.className = `message ${type}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = type === 'user' ? '👤' : this.getCharacterEmoji(this.currentCharacter?.category);
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = this.formatMessage(content);
        
        message.appendChild(avatar);
        message.appendChild(messageContent);
        container.appendChild(message);
        
        // 滚动到底部
        container.scrollTop = container.scrollHeight;
    }

    formatMessage(content) {
        // 简单的文本格式化
        return content
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }

    showTyping() {
        const typingId = 'typing-' + Date.now();
        const container = document.getElementById('messagesContainer');
        const typing = document.createElement('div');
        typing.id = typingId;
        typing.className = 'message ai';
        typing.innerHTML = `
            <div class="message-avatar">${this.getCharacterEmoji(this.currentCharacter?.category)}</div>
            <div class="message-content">
                <div class="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        
        container.appendChild(typing);
        container.scrollTop = container.scrollHeight;
        
        return typingId;
    }

    removeTyping(typingId) {
        const typing = document.getElementById(typingId);
        if (typing) {
            typing.remove();
        }
    }

    clearMessages() {
        document.getElementById('messagesContainer').innerHTML = '';
    }

    setupVoiceRecording() {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ 
                audio: {
                    sampleRate: 16000,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true
                }
            })
                .then(stream => {
                    this.audioStream = stream;
                    this.setupAudioContext(stream);
                    
                    // 同时设置MediaRecorder作为备用方案
                    const options = { mimeType: 'audio/webm;codecs=opus' };
                    
                    if (MediaRecorder.isTypeSupported('audio/wav')) {
                        options.mimeType = 'audio/wav';
                    } else if (MediaRecorder.isTypeSupported('audio/webm')) {
                        options.mimeType = 'audio/webm';
                    }
                    
                    this.mediaRecorder = new MediaRecorder(stream, options);
                    
                    this.mediaRecorder.ondataavailable = (event) => {
                        if (event.data.size > 0) {
                            this.audioChunks.push(event.data);
                        }
                    };
                    
                    this.mediaRecorder.onstop = () => {
                        this.processRecording();
                    };
                    
                    console.log('语音录制初始化成功');
                })
                .catch(error => {
                    console.warn('语音功能不可用:', error);
                    this.showError('无法访问麦克风，请检查浏览器权限设置');
                });
        } else {
            console.warn('浏览器不支持语音录制功能');
        }
    }

    setupAudioContext(stream) {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
                sampleRate: 16000
            });
            this.source = this.audioContext.createMediaStreamSource(stream);
            
            // 创建ScriptProcessor用于录制
            this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);
            this.recordingData = [];
            
            this.processor.onaudioprocess = (event) => {
                if (this.isRecording) {
                    const inputData = event.inputBuffer.getChannelData(0);
                    // 复制数据到录制缓冲区
                    this.recordingData.push(new Float32Array(inputData));
                }
            };
            
            console.log('Web Audio API 初始化成功');
        } catch (error) {
            console.warn('Web Audio API 初始化失败:', error);
        }
    }

    toggleVoiceRecording() {
        const voiceBtn = document.getElementById('voiceBtn');
        
        if (!this.mediaRecorder && !this.audioContext) {
            this.showError('语音功能不可用，请检查麦克风权限');
            return;
        }

        if (!this.isRecording) {
            // 开始录音
            this.audioChunks = [];
            this.recordingData = [];
            
            // 优先使用Web Audio API录制WAV格式
            if (this.audioContext && this.processor) {
                console.log('使用Web Audio API录制WAV格式');
                this.source.connect(this.processor);
                this.processor.connect(this.audioContext.destination);
                this.useWebAudio = true;
            } else if (this.mediaRecorder) {
                console.log('使用MediaRecorder录制');
                this.mediaRecorder.start();
                this.useWebAudio = false;
            }
            
            this.isRecording = true;
            
            voiceBtn.classList.add('recording');
            voiceBtn.innerHTML = '<i class="fas fa-stop"></i>';
            voiceBtn.title = '停止录音';
        } else {
            // 停止录音
            this.isRecording = false;
            
            if (this.useWebAudio && this.processor) {
                this.processor.disconnect();
                this.source.disconnect();
                // 直接处理Web Audio API的数据
                this.processWebAudioRecording();
            } else if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
                this.mediaRecorder.stop();
                // processRecording会在onstop事件中被调用
            }
            
            voiceBtn.classList.remove('recording');
            voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            voiceBtn.title = '语音输入';
        }
    }

    processWebAudioRecording() {
        if (this.recordingData.length === 0) {
            this.showError('录音数据为空，请重新录制');
            return;
        }

        console.log('处理Web Audio录音数据...');
        
        // 合并所有录制的数据
        let totalLength = 0;
        for (let i = 0; i < this.recordingData.length; i++) {
            totalLength += this.recordingData[i].length;
        }
        
        const mergedData = new Float32Array(totalLength);
        let offset = 0;
        for (let i = 0; i < this.recordingData.length; i++) {
            mergedData.set(this.recordingData[i], offset);
            offset += this.recordingData[i].length;
        }
        
        // 转换为WAV格式
        const wavBlob = this.floatArrayToWav(mergedData, 16000);
        this.sendAudioToServer(wavBlob, 'recording.wav');
    }

    floatArrayToWav(floatArray, sampleRate) {
        const length = floatArray.length;
        const buffer = new ArrayBuffer(44 + length * 2);
        const view = new DataView(buffer);
        
        // WAV文件头
        const writeString = (offset, string) => {
            for (let i = 0; i < string.length; i++) {
                view.setUint8(offset + i, string.charCodeAt(i));
            }
        };
        
        writeString(0, 'RIFF');
        view.setUint32(4, 36 + length * 2, true);
        writeString(8, 'WAVE');
        writeString(12, 'fmt ');
        view.setUint32(16, 16, true);
        view.setUint16(20, 1, true);
        view.setUint16(22, 1, true);
        view.setUint32(24, sampleRate, true);
        view.setUint32(28, sampleRate * 2, true);
        view.setUint16(32, 2, true);
        view.setUint16(34, 16, true);
        writeString(36, 'data');
        view.setUint32(40, length * 2, true);
        
        // 转换浮点数据为16位PCM
        let offset = 44;
        for (let i = 0; i < length; i++) {
            const sample = Math.max(-1, Math.min(1, floatArray[i]));
            view.setInt16(offset, sample * 0x7FFF, true);
            offset += 2;
        }
        
        return new Blob([buffer], { type: 'audio/wav' });
    }

    async processRecording() {
        if (this.audioChunks.length === 0) {
            this.showError('录音数据为空，请重新录制');
            return;
        }

        // 确定音频格式
        let mimeType = 'audio/webm';
        let filename = 'recording.webm';
        
        if (this.mediaRecorder && this.mediaRecorder.mimeType) {
            mimeType = this.mediaRecorder.mimeType;
            if (mimeType.includes('wav')) {
                filename = 'recording.wav';
            } else if (mimeType.includes('webm')) {
                filename = 'recording.webm';
            }
        }

        const audioBlob = new Blob(this.audioChunks, { type: mimeType });
        
        // 检查音频大小
        if (audioBlob.size < 1000) {
            this.showError('录音时间太短，请重新录制');
            return;
        }
        
        console.log('处理MediaRecorder录音:', {
            size: audioBlob.size,
            type: mimeType,
            chunks: this.audioChunks.length
        });

        this.sendAudioToServer(audioBlob, filename);
    }

    async sendAudioToServer(audioBlob, filename) {
        const formData = new FormData();
        formData.append('audio', audioBlob, filename);

        // 显示处理中状态
        const messageInput = document.getElementById('messageInput');
        const originalPlaceholder = messageInput.placeholder;
        messageInput.placeholder = '正在识别语音...';
        messageInput.disabled = true;

        try {
            const response = await fetch('/api/voice/recognize', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (data.success && data.text) {
                messageInput.value = data.text;
                console.log('语音识别成功:', data.text);
            } else {
                this.showError(data.error || '语音识别失败，请重试');
                console.error('语音识别失败:', data);
            }
        } catch (error) {
            this.showError('语音识别出错: ' + error.message);
            console.error('语音识别网络错误:', error);
        } finally {
            // 恢复输入框状态
            messageInput.placeholder = originalPlaceholder;
            messageInput.disabled = false;
            
            // 清空录音数据
            this.audioChunks = [];
            this.recordingData = [];
        }
    }

    async playVoice(text) {
        try {
            const response = await fetch('/api/voice/synthesize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    text: text,
                    character_id: this.currentCharacter?.id 
                })
            });

            const data = await response.json();
            
            if (data.success && data.audio_url) {
                const audio = new Audio(data.audio_url);
                audio.play().catch(error => {
                    console.warn('音频播放失败:', error);
                });
            }
        } catch (error) {
            console.warn('语音合成失败:', error);
        }
    }

    shouldAutoPlayVoice() {
        // 可以添加用户设置来控制是否自动播放语音
        return false;
    }

    openSkillModal(skillName) {
        const modal = document.getElementById('skillModal');
        const title = document.getElementById('skillModalTitle');
        const body = document.getElementById('skillModalBody');
        
        title.textContent = this.getSkillTitle(skillName);
        body.innerHTML = this.getSkillForm(skillName);
        
        // 为语言练习添加事件监听器
        if (skillName === 'language_practice') {
            setTimeout(() => {
                const topicSelect = document.getElementById('skillTopic');
                const customTopicDiv = document.getElementById('customTopicDiv');
                
                if (topicSelect && customTopicDiv) {
                    topicSelect.addEventListener('change', (e) => {
                        if (e.target.value === '自定义') {
                            customTopicDiv.style.display = 'block';
                        } else {
                            customTopicDiv.style.display = 'none';
                        }
                    });
                }
            }, 100);
        }
        
        const skillModal = new bootstrap.Modal(modal);
        skillModal.show();
        
        // 保存当前技能
        modal.dataset.currentSkill = skillName;
    }

    getSkillTitle(skillName) {
        const titles = {
            'knowledge_qa': '知识问答',
            'emotional_support': '情感陪伴',
            'teaching_guidance': '教学指导',
            'creative_writing': '创作协助',
            'language_practice': '语言练习'
        };
        return titles[skillName] || '技能';
    }

    getSkillForm(skillName) {
        const forms = {
            'knowledge_qa': `
                <div class="mb-3">
                    <label class="form-label">请输入你的问题：</label>
                    <textarea class="form-control" id="skillQuestion" rows="3" placeholder="例如：请解释相对论的基本原理"></textarea>
                </div>
            `,
            'emotional_support': `
                <div class="mb-3">
                    <label class="form-label">当前情绪状态：</label>
                    <select class="form-select" id="skillEmotion">
                        <option value="sad">难过</option>
                        <option value="anxious">焦虑</option>
                        <option value="confused">困惑</option>
                        <option value="lonely">孤独</option>
                        <option value="stressed">压力大</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label">想要分享的内容：</label>
                    <textarea class="form-control" id="skillMessage" rows="3" placeholder="告诉我你的感受..."></textarea>
                </div>
            `,
            'teaching_guidance': `
                <div class="mb-3">
                    <label class="form-label">学习主题：</label>
                    <input type="text" class="form-control" id="skillTopic" placeholder="例如：量子物理、哲学思辨、文学创作">
                </div>
                <div class="mb-3">
                    <label class="form-label">学习水平：</label>
                    <select class="form-select" id="skillLevel">
                        <option value="beginner">初学者</option>
                        <option value="intermediate">中级</option>
                        <option value="advanced">高级</option>
                    </select>
                </div>
            `,
            'creative_writing': `
                <div class="mb-3">
                    <label class="form-label">创作类型：</label>
                    <select class="form-select" id="skillType">
                        <option value="story">故事</option>
                        <option value="poem">诗歌</option>
                        <option value="essay">散文</option>
                        <option value="dialogue">对话</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label">主题：</label>
                    <input type="text" class="form-control" id="skillTheme" placeholder="例如：友谊、成长、科幻">
                </div>
                <div class="mb-3">
                    <label class="form-label">风格要求：</label>
                    <input type="text" class="form-control" id="skillStyle" placeholder="例如：温馨、悬疑、幽默">
                </div>
            `,
            'language_practice': `
                <div class="mb-3">
                    <label class="form-label">目标语言：</label>
                    <select class="form-select" id="skillLanguage">
                        <option value="Chinese">中文</option>
                        <option value="English">英语</option>
                        <option value="French">法语</option>
                        <option value="German">德语</option>
                        <option value="Spanish">西班牙语</option>
                        <option value="Japanese">日语</option>
                        <option value="Korean">韩语</option>
                        <option value="Russian">俄语</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label">练习类型：</label>
                    <select class="form-select" id="skillPracticeType">
                        <option value="conversation">对话练习</option>
                        <option value="grammar">语法练习</option>
                        <option value="vocabulary">词汇练习</option>
                        <option value="pronunciation">发音练习</option>
                        <option value="writing">写作练习</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label">话题：</label>
                    <select class="form-select" id="skillTopic">
                        <option value="日常生活">日常生活</option>
                        <option value="工作职场">工作职场</option>
                        <option value="旅行出游">旅行出游</option>
                        <option value="文化交流">文化交流</option>
                        <option value="中华传统文化">中华传统文化</option>
                        <option value="现代科技">现代科技</option>
                        <option value="美食文化">美食文化</option>
                        <option value="节日庆典">节日庆典</option>
                        <option value="学习教育">学习教育</option>
                        <option value="家庭生活">家庭生活</option>
                        <option value="自定义">自定义话题</option>
                    </select>
                </div>
                <div class="mb-3" id="customTopicDiv" style="display: none;">
                    <label class="form-label">自定义话题：</label>
                    <input type="text" class="form-control" id="customTopic" placeholder="请输入您想练习的话题">
                </div>
            `
        };
        return forms[skillName] || '<p>技能表单加载中...</p>';
    }

    async executeSkill() {
        const modal = document.getElementById('skillModal');
        const skillName = modal.dataset.currentSkill;
        
        if (!skillName || !this.currentCharacter) return;

        const skillData = this.getSkillData(skillName);
        
        try {
            const response = await fetch(`/api/skills/${skillName}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(skillData)
            });

            const data = await response.json();
            
            if (data.success) {
                // 关闭技能模态框
                bootstrap.Modal.getInstance(modal).hide();
                
                // 在聊天中显示技能结果
                this.addMessage(`使用了${this.getSkillTitle(skillName)}技能`, 'user');
                this.addMessage(data.result.answer || data.result.lesson || data.result.creation || data.result.support_message || data.result.practice_content, 'ai');
            } else {
                this.showError('技能执行失败: ' + data.error);
            }
        } catch (error) {
            this.showError('网络错误: ' + error.message);
        }
    }

    getSkillData(skillName) {
        const data = {};
        
        switch (skillName) {
            case 'knowledge_qa':
                data.question = document.getElementById('skillQuestion')?.value || '';
                break;
            case 'emotional_support':
                data.emotion = document.getElementById('skillEmotion')?.value || '';
                data.message = document.getElementById('skillMessage')?.value || '';
                break;
            case 'teaching_guidance':
                data.topic = document.getElementById('skillTopic')?.value || '';
                data.level = document.getElementById('skillLevel')?.value || 'beginner';
                break;
            case 'creative_writing':
                data.type = document.getElementById('skillType')?.value || 'story';
                data.theme = document.getElementById('skillTheme')?.value || '';
                data.style = document.getElementById('skillStyle')?.value || '';
                break;
            case 'language_practice':
                data.language = document.getElementById('skillLanguage')?.value || 'Chinese';
                data.type = document.getElementById('skillPracticeType')?.value || 'conversation';
                const topicSelect = document.getElementById('skillTopic')?.value || '日常生活';
                if (topicSelect === '自定义') {
                    data.topic = document.getElementById('customTopic')?.value || '日常生活';
                } else {
                    data.topic = topicSelect;
                }
                break;
        }
        
        return data;
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        const grid = document.getElementById('charactersGrid');
        
        if (show) {
            loading.style.display = 'block';
            grid.style.display = 'none';
        } else {
            loading.style.display = 'none';
            grid.style.display = 'grid';
        }
    }

    showError(message) {
        // 简单的错误提示，可以替换为更好的UI组件
        alert(message);
    }
}

// 初始化应用
const app = new AIRoleplayApp();

// 添加CSS动画样式
const style = document.createElement('style');
style.textContent = `
    .typing-indicator {
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    .typing-indicator span {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #999;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
    .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes typing {
        0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
        40% { transform: scale(1); opacity: 1; }
    }
`;
document.head.appendChild(style);    // 语音配置
相关方法
    async loadVoiceConfig(characterId) {
        try {
            console.log('加载角色语音配置:', characterId);
            
            const response = await fetch(`/api/voice/config/${characterId}?voice_type=auto`);
            const data = await response.json();
            
            if (data.success) {
                this.voiceConfig = data.config;
                console.log('语音配置加载成功:', this.voiceConfig);
                
                // 添加语音控制按钮到聊天界面
                this.addVoiceControls();
            } else {
                console.warn('语音配置加载失败:', data.error);
            }
        } catch (error) {
            console.warn('语音配置加载错误:', error);
        }
    }

    addVoiceControls() {
        const skillsSection = document.getElementById('skillsSection');
        
        // 检查是否已经添加了语音控制
        if (document.getElementById('voiceControls')) {
            return;
        }
        
        const voiceControls = document.createElement('div');
        voiceControls.id = 'voiceControls';
        voiceControls.className = 'voice-controls mt-2';
        voiceControls.innerHTML = `
            <small class="text-muted">语音功能：</small>
            <div class="mt-2">
                <button class="skill-btn" id="toggleAutoVoice" onclick="app.toggleAutoVoice()">
                    <i class="fas fa-volume-up"></i> 自动语音播放
                </button>
                <button class="skill-btn" id="startRealtimeVoice" onclick="app.startRealtimeVoice()">
                    <i class="fas fa-phone"></i> 实时语音对话
                </button>
                <button class="skill-btn" onclick="app.testVoice()">
                    <i class="fas fa-play"></i> 测试语音
                </button>
            </div>
        `;
        
        skillsSection.appendChild(voiceControls);
    }

    toggleAutoVoice() {
        this.autoVoiceEnabled = !this.autoVoiceEnabled;
        const btn = document.getElementById('toggleAutoVoice');
        
        if (this.autoVoiceEnabled) {
            btn.classList.add('active');
            btn.innerHTML = '<i class="fas fa-volume-up"></i> 自动语音播放 (开)';
            this.showInfo('自动语音播放已开启');
        } else {
            btn.classList.remove('active');
            btn.innerHTML = '<i class="fas fa-volume-up"></i> 自动语音播放 (关)';
            this.showInfo('自动语音播放已关闭');
        }
    }

    async startRealtimeVoice() {
        if (this.realtimeVoiceEnabled) {
            this.stopRealtimeVoice();
            return;
        }

        try {
            console.log('启动实时语音对话...');
            
            // 获取实时语音配置
            const response = await fetch('/api/voice/realtime/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    character_id: this.currentCharacter.id,
                    voice_type: 'auto'
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.voiceSessionId = data.session_id;
                
                // 连接WebSocket
                await this.connectVoiceWebSocket(data.ws_config, data.session_config);
                
                this.realtimeVoiceEnabled = true;
                this.updateRealtimeVoiceButton(true);
                this.showInfo('实时语音对话已启动');
            } else {
                this.showError('启动实时语音失败: ' + data.error);
            }
        } catch (error) {
            this.showError('实时语音启动错误: ' + error.message);
        }
    }

    async connectVoiceWebSocket(wsConfig, sessionConfig) {
        try {
            const url = wsConfig.base_url;
            
            // 创建WebSocket连接
            this.websocket = new WebSocket(url);
            
            // 设置请求头（注意：WebSocket不能直接设置自定义头，需要通过URL参数或其他方式）
            // 这里我们需要修改连接方式
            
            this.websocket.onopen = () => {
                console.log('WebSocket连接成功');
                
                // 发送会话开始请求
                const startMessage = {
                    type: 'start_session',
                    data: sessionConfig
                };
                
                this.websocket.send(JSON.stringify(startMessage));
            };
            
            this.websocket.onmessage = (event) => {
                this.handleVoiceMessage(event.data);
            };
            
            this.websocket.onclose = () => {
                console.log('WebSocket连接关闭');
                this.realtimeVoiceEnabled = false;
                this.updateRealtimeVoiceButton(false);
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket错误:', error);
                this.showError('语音连接错误');
            };
            
        } catch (error) {
            console.error('WebSocket连接失败:', error);
            throw error;
        }
    }

    handleVoiceMessage(messageData) {
        try {
            const data = JSON.parse(messageData);
            
            switch (data.type) {
                case 'session_started':
                    console.log('语音会话已开始');
                    break;
                    
                case 'audio':
                    // 处理接收到的音频数据
                    this.playReceivedAudio(data.data);
                    break;
                    
                case 'text':
                    // 处理接收到的文本消息
                    if (data.data && data.data.text) {
                        this.addMessage(data.data.text, 'ai');
                    }
                    break;
                    
                case 'error':
                    console.error('语音服务错误:', data.message);
                    this.showError('语音服务错误: ' + data.message);
                    break;
                    
                default:
                    console.log('未知消息类型:', data.type);
            }
        } catch (error) {
            console.error('处理语音消息错误:', error);
        }
    }

    playReceivedAudio(audioData) {
        try {
            // 将十六进制字符串转换为音频数据并播放
            const audioBytes = this.hexToBytes(audioData);
            const audioBlob = new Blob([audioBytes], { type: 'audio/wav' });
            const audioUrl = URL.createObjectURL(audioBlob);
            
            const audio = new Audio(audioUrl);
            audio.play().catch(error => {
                console.warn('音频播放失败:', error);
            });
            
            // 清理URL对象
            audio.onended = () => {
                URL.revokeObjectURL(audioUrl);
            };
        } catch (error) {
            console.error('播放接收音频错误:', error);
        }
    }

    hexToBytes(hex) {
        const bytes = new Uint8Array(hex.length / 2);
        for (let i = 0; i < hex.length; i += 2) {
            bytes[i / 2] = parseInt(hex.substr(i, 2), 16);
        }
        return bytes;
    }

    stopRealtimeVoice() {
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        
        this.realtimeVoiceEnabled = false;
        this.voiceSessionId = null;
        this.updateRealtimeVoiceButton(false);
        this.showInfo('实时语音对话已停止');
    }

    updateRealtimeVoiceButton(enabled) {
        const btn = document.getElementById('startRealtimeVoice');
        if (btn) {
            if (enabled) {
                btn.classList.add('active');
                btn.innerHTML = '<i class="fas fa-phone-slash"></i> 停止语音对话';
            } else {
                btn.classList.remove('active');
                btn.innerHTML = '<i class="fas fa-phone"></i> 实时语音对话';
            }
        }
    }

    async testVoice() {
        if (!this.voiceConfig) {
            this.showError('语音配置未加载');
            return;
        }
        
        const testText = `你好，我是${this.currentCharacter.name}，很高兴与你对话！`;
        await this.playVoice(testText);
    }

    shouldAutoPlayVoice() {
        return this.autoVoiceEnabled || false;
    }

    showInfo(message) {
        // 简单的信息提示
        console.log('Info:', message);
        
        // 可以添加更好的UI提示
        const toast = document.createElement('div');
        toast.className = 'toast-message info';
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #17a2b8;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            z-index: 9999;
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    // 重写语音播放方法以支持字节跳动TTS
    async playVoice(text) {
        try {
            console.log('播放语音:', text.substring(0, 50) + '...');
            
            const response = await fetch('/api/voice/synthesize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    text: text,
                    character_id: this.currentCharacter?.id 
                })
            });

            const data = await response.json();
            
            if (data.success && data.audio_url) {
                const audio = new Audio(data.audio_url);
                
                // 添加播放状态指示
                const playingIndicator = this.showPlayingIndicator();
                
                audio.onended = () => {
                    this.hidePlayingIndicator(playingIndicator);
                };
                
                audio.onerror = () => {
                    this.hidePlayingIndicator(playingIndicator);
                    console.warn('音频播放失败');
                };
                
                await audio.play();
            } else {
                console.warn('语音合成失败:', data.error);
            }
        } catch (error) {
            console.warn('语音播放失败:', error);
        }
    }

    showPlayingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'playing-indicator';
        indicator.innerHTML = '<i class="fas fa-volume-up"></i> 正在播放...';
        indicator.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 10px 15px;
            border-radius: 20px;
            z-index: 9999;
            font-size: 14px;
        `;
        
        document.body.appendChild(indicator);
        return indicator;
    }

    hidePlayingIndicator(indicator) {
        if (indicator && indicator.parentNode) {
            indicator.parentNode.removeChild(indicator);
        }
    }
}

// 初始化应用
const app = new AIRoleplayApp();