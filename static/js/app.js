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
        
        console.log('🎯 AIRoleplayApp 构造函数执行完成');
        this.init();
    }

    async init() {
        console.log('🚀 开始初始化应用...');
        try {
            this.bindEvents();
            await this.loadCharacters();
            this.setupVoiceRecording();
            console.log('✅ 应用初始化完成');
        } catch (error) {
            console.error('❌ 应用初始化失败:', error);
        }
    }

    bindEvents() {
        console.log('🔗 绑定事件监听器...');
        
        // 搜索功能
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchCharacters(e.target.value);
            });
        }

        // 分类筛选
        document.querySelectorAll('.category-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.filterByCategory(e.target.dataset.category);
                this.updateCategoryButtons(e.target);
            });
        });

        // 发送消息
        const sendBtn = document.getElementById('sendBtn');
        if (sendBtn) {
            sendBtn.addEventListener('click', () => {
                this.sendMessage();
            });
        }

        // 回车发送
        const messageInput = document.getElementById('messageInput');
        if (messageInput) {
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }

        // 语音按钮
        const voiceBtn = document.getElementById('voiceBtn');
        if (voiceBtn) {
            voiceBtn.addEventListener('click', () => {
                this.toggleVoiceRecording();
            });
        }

        // 技能按钮
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('skill-btn')) {
                this.showSkillModal(e.target.dataset.skill);
            }
        });

        console.log('✅ 事件监听器绑定完成');
    }

    async loadCharacters() {
        console.log('📥 开始加载角色数据...');
        try {
            this.showLoading(true);
            
            const response = await fetch('/api/characters');
            console.log('🌐 API响应状态:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('📊 接收到的数据:', data);
            
            if (data.success && data.characters) {
                this.characters = data.characters;
                console.log('👥 成功加载角色数量:', this.characters.length);
                this.renderCharacters(this.characters);
            } else {
                throw new Error(data.error || '未知错误');
            }
        } catch (error) {
            console.error('❌ 加载角色失败:', error);
            this.showError('加载角色失败: ' + error.message);
            
            // 显示错误信息到页面
            const grid = document.getElementById('charactersGrid');
            if (grid) {
                grid.innerHTML = `
                    <div style="grid-column: 1 / -1; text-align: center; padding: 2rem; color: #e53e3e;">
                        <h3>😔 角色加载失败</h3>
                        <p>错误信息: ${error.message}</p>
                        <button onclick="window.app.loadCharacters()" style="padding: 0.5rem 1rem; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer;">
                            🔄 重新加载
                        </button>
                    </div>
                `;
            }
        } finally {
            this.showLoading(false);
        }
    }

    renderCharacters(characters) {
        console.log('🎨 开始渲染角色卡片...');
        const grid = document.getElementById('charactersGrid');
        
        if (!grid) {
            console.error('❌ 找不到角色网格容器 #charactersGrid');
            return;
        }
        
        console.log('🧹 清空网格容器');
        grid.innerHTML = '';

        if (!characters || characters.length === 0) {
            grid.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 2rem; color: #718096;">
                    <h3>🤔 没有找到角色</h3>
                    <p>请检查搜索条件或稍后重试</p>
                </div>
            `;
            return;
        }

        characters.forEach((character, index) => {
            console.log(`🎭 渲染角色 ${index + 1}: ${character.name}`);
            try {
                const card = this.createCharacterCard(character);
                grid.appendChild(card);
            } catch (error) {
                console.error(`❌ 渲染角色 ${character.name} 失败:`, error);
            }
        });
        
        console.log('✅ 角色卡片渲染完成');
    }

    createCharacterCard(character) {
        const card = document.createElement('div');
        card.className = 'character-card';
        
        // 安全地获取角色属性
        const name = character.name || '未知角色';
        const background = character.background || '暂无背景介绍';
        const category = character.category || 'unknown';
        const tags = character.tags || [];
        const id = character.id || 'unknown';
        
        card.innerHTML = `
            <div class="character-avatar">${this.getCharacterEmoji(category)}</div>
            <div class="character-name">${name}</div>
            <div class="character-category">${this.getCategoryName(category)}</div>
            <div class="character-description">${background.substring(0, 100)}...</div>
            <div class="character-tags">
                ${tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
            </div>
            <button class="chat-btn" onclick="window.app.startChat('${id}')">
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
            character.name.includes(query) ||
            character.background.includes(query) ||
            character.tags.some(tag => tag.includes(query))
        );

        this.renderCharacters(filtered);
    }

    filterByCategory(category) {
        if (category === 'all') {
            this.renderCharacters(this.characters);
        } else {
            const filtered = this.characters.filter(character => 
                character.category === category
            );
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
        console.log('💬 开始与角色对话:', characterId);
        
        try {
            const response = await fetch('/api/chat/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ character_id: characterId })
            });

            const data = await response.json();

            if (data.success) {
                this.currentCharacter = data.character;
                this.currentSessionId = data.session_id;
                
                this.showChatModal(data.character, data.welcome_message);
                await this.loadVoiceConfig(characterId);
            } else {
                this.showError('开始对话失败: ' + data.error);
            }
        } catch (error) {
            console.error('❌ 开始对话失败:', error);
            this.showError('网络错误: ' + error.message);
        }
    }

    showChatModal(character, welcomeMessage) {
        // 设置角色信息
        document.getElementById('chatCharacterName').textContent = character.name;
        document.getElementById('chatCharacterCategory').textContent = this.getCategoryName(character.category);
        document.getElementById('chatAvatar').textContent = this.getCharacterEmoji(character.category);

        // 清空消息容器
        const messagesContainer = document.getElementById('messagesContainer');
        messagesContainer.innerHTML = '';

        // 添加欢迎消息
        if (welcomeMessage) {
            this.addMessage(welcomeMessage, 'assistant');
        }

        // 显示模态框
        const modal = new bootstrap.Modal(document.getElementById('chatModal'));
        modal.show();
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();

        if (!message) return;

        // 添加用户消息到界面
        this.addMessage(message, 'user');
        messageInput.value = '';

        try {
            const response = await fetch('/api/chat/message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();

            if (data.success) {
                this.addMessage(data.response, 'assistant');
                
                // 自动播放语音回复
                if (this.voiceConfig) {
                    this.playVoice(data.response);
                }
            } else {
                this.showError('发送消息失败: ' + data.error);
            }
        } catch (error) {
            console.error('❌ 发送消息失败:', error);
            this.showError('网络错误: ' + error.message);
        }
    }

    addMessage(content, sender) {
        const messagesContainer = document.getElementById('messagesContainer');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        const avatar = sender === 'user' ? '👤' : this.getCharacterEmoji(this.currentCharacter?.category);
        
        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">${content}</div>
        `;

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        const grid = document.getElementById('charactersGrid');
        
        if (loading && grid) {
            if (show) {
                loading.style.display = 'block';
                grid.style.display = 'none';
            } else {
                loading.style.display = 'none';
                grid.style.display = 'grid';
            }
        }
    }

    showError(message) {
        console.error('🚨 错误:', message);
        alert(message);
    }

    // 语音相关功能（简化版）
    setupVoiceRecording() {
        console.log('🎤 设置语音录制功能...');
        // 简化的语音功能，避免复杂的错误
    }

    toggleVoiceRecording() {
        console.log('🎤 切换语音录制状态');
        this.showError('语音功能暂时不可用，请使用文字输入');
    }

    async loadVoiceConfig(characterId) {
        console.log('🔊 加载语音配置:', characterId);
        // 简化的语音配置加载
    }

    async playVoice(text) {
        console.log('🔊 播放语音:', text.substring(0, 50) + '...');
        // 简化的语音播放
    }

    showSkillModal(skillName) {
        console.log('🛠️ 显示技能模态框:', skillName);
        this.showError('技能功能开发中，敬请期待');
    }
}

// 确保DOM完全加载后再初始化应用
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        console.log('📄 DOM加载完成，初始化应用...');
        window.app = new AIRoleplayApp();
    });
} else {
    console.log('📄 DOM已就绪，立即初始化应用...');
    window.app = new AIRoleplayApp();
}

console.log('📜 JavaScript文件加载完成');