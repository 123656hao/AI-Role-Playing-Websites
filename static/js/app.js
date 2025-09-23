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
            
            // 点击外部隐藏搜索建议
            document.addEventListener('click', (e) => {
                if (!e.target.closest('.search-box')) {
                    this.hideSearchSuggestions();
                }
            });
            
            // 键盘导航支持
            searchInput.addEventListener('keydown', (e) => {
                const suggestions = document.getElementById('searchSuggestions');
                if (!suggestions || suggestions.style.display === 'none') return;
                
                const items = suggestions.querySelectorAll('.suggestion-item');
                let activeIndex = Array.from(items).findIndex(item => item.classList.contains('active'));
                
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    items.forEach(item => item.classList.remove('active'));
                    activeIndex = activeIndex < items.length - 1 ? activeIndex + 1 : 0;
                    items[activeIndex]?.classList.add('active');
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    items.forEach(item => item.classList.remove('active'));
                    activeIndex = activeIndex > 0 ? activeIndex - 1 : items.length - 1;
                    items[activeIndex]?.classList.add('active');
                } else if (e.key === 'Enter' && activeIndex >= 0) {
                    e.preventDefault();
                    items[activeIndex]?.click();
                } else if (e.key === 'Escape') {
                    this.hideSearchSuggestions();
                }
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
                <div class="empty-state" style="grid-column: 1 / -1;">
                    <div class="empty-state-icon">🤔</div>
                    <h3>暂无匹配的角色</h3>
                    <p>请尝试调整搜索条件或切换分类筛选</p>
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
        
        // 简化描述为一行
        const shortDescription = this.getShortDescription(background);
        
        card.innerHTML = `
            <div class="character-header">
                <div class="character-avatar">${this.getCharacterEmoji(category)}</div>
                <div class="character-info">
                    <h3 style="text-align: center !important; display: flex; justify-content: center; align-items: center; margin: 0 auto;">${name}</h3>
                    <div class="character-category" style="text-align: center !important; display: flex; justify-content: center; align-items: center;">${this.getCategoryName(category)}</div>
                </div>
            </div>
            <div class="character-description" style="text-align: center !important;">${shortDescription}</div>
            <div class="character-tags" style="justify-content: center !important; display: flex; align-items: center;">
                ${tags.slice(0, 4).map(tag => `<span class="tag">${tag}</span>`).join('')}
            </div>
            <div class="character-actions">
                <button class="chat-btn" onclick="event.stopPropagation(); window.app.startChat('${id}')">
                    <i class="fas fa-comments"></i> 开始对话
                </button>
            </div>
        `;
        
        // 添加卡片点击事件来显示角色详情
        card.addEventListener('click', (e) => {
            // 如果点击的是按钮，不触发卡片事件
            if (e.target.closest('.chat-btn')) {
                return;
            }
            this.showCharacterInfo(id);
        });
        
        return card;
    }

    getShortDescription(background) {
        // 提取背景介绍的前40个字符作为简短描述
        if (!background || background.length <= 40) {
            return background || '暂无介绍';
        }
        return background.substring(0, 40) + '...';
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
        console.log('🔍 搜索角色:', query);
        
        if (!query.trim()) {
            this.renderCharacters(this.characters);
            this.hideSearchSuggestions();
            return;
        }

        const filtered = this.characters.filter(character => 
            character.name.toLowerCase().includes(query.toLowerCase()) ||
            character.background.toLowerCase().includes(query.toLowerCase()) ||
            character.tags.some(tag => tag.toLowerCase().includes(query.toLowerCase())) ||
            this.getCategoryName(character.category).includes(query)
        );

        this.renderCharacters(filtered);
        this.showSearchSuggestions(query, filtered);
    }

    showSearchSuggestions(query, filteredCharacters) {
        const suggestions = document.getElementById('searchSuggestions');
        if (!suggestions) return;
        
        // 显示前5个匹配的角色
        const topMatches = filteredCharacters.slice(0, 5);
        
        if (topMatches.length === 0) {
            suggestions.style.display = 'none';
            return;
        }
        
        suggestions.innerHTML = topMatches.map(character => `
            <div class="suggestion-item" onclick="window.app.selectSuggestion('${character.name}')">
                <span style="margin-right: 0.5rem;">${this.getCharacterEmoji(character.category)}</span>
                <strong>${character.name}</strong>
                <small style="margin-left: 0.5rem; color: var(--text-muted);">${this.getCategoryName(character.category)}</small>
            </div>
        `).join('');
        
        suggestions.style.display = 'block';
    }

    hideSearchSuggestions() {
        const suggestions = document.getElementById('searchSuggestions');
        if (suggestions) {
            suggestions.style.display = 'none';
        }
    }

    selectSuggestion(characterName) {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.value = characterName;
            this.searchCharacters(characterName);
            this.hideSearchSuggestions();
        }
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
        const currentTime = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
        
        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div>
                <div class="message-content">${content}</div>
                <div class="message-time">${currentTime}</div>
            </div>
        `;

        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(20px)';
        messagesContainer.appendChild(messageDiv);
        
        // 动画效果
        setTimeout(() => {
            messageDiv.style.transition = 'all 0.3s ease';
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
        }, 10);
        
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        const grid = document.getElementById('charactersGrid');
        
        if (loading && grid) {
            if (show) {
                loading.classList.add('show');
                grid.style.display = 'none';
            } else {
                loading.classList.remove('show');
                grid.style.display = 'grid';
            }
        }
    }

    showError(message) {
        console.error('🚨 错误:', message);
        
        // 创建更友好的错误提示
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger alert-dismissible fade show';
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(239, 68, 68, 0.2);
        `;
        
        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2"></i>
            <strong>错误：</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(errorDiv);
        
        // 5秒后自动移除
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }

    showCharacterInfo(characterId) {
        const character = this.characters.find(c => c.id === characterId);
        if (!character) return;
        
        // 显示角色详情模态框
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header" style="background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)); color: white;">
                        <h5 class="modal-title">
                            <span style="font-size: 1.5rem; margin-right: 0.5rem;">${this.getCharacterEmoji(character.category)}</span>
                            ${character.name}
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-4 text-center mb-3">
                                <div class="character-avatar" style="width: 100px; height: 100px; font-size: 3rem; margin: 0 auto;">
                                    ${this.getCharacterEmoji(character.category)}
                                </div>
                                <div class="mt-2">
                                    <span class="badge" style="background: var(--primary-color); font-size: 0.9rem;">
                                        ${this.getCategoryName(character.category)}
                                    </span>
                                </div>
                            </div>
                            <div class="col-md-8">
                                <h6 style="color: var(--primary-color); font-weight: 600;">背景介绍</h6>
                                <p style="line-height: 1.6; color: var(--text-dark);">${character.background}</p>
                                
                                <h6 style="color: var(--primary-color); font-weight: 600; margin-top: 1.5rem;">专业领域</h6>
                                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                                    ${character.tags.map(tag => `
                                        <span class="tag" style="background: var(--bg-secondary); padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.8rem;">
                                            ${tag}
                                        </span>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                        <button type="button" class="btn" style="background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)); color: white;" 
                                onclick="window.app.startChat('${character.id}'); bootstrap.Modal.getOrCreateInstance(this.closest('.modal')).hide();">
                            <i class="fas fa-comments me-2"></i>开始对话
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        // 模态框关闭后移除DOM
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
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