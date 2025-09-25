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

        // 技能执行按钮
        const executeSkillBtn = document.getElementById('executeSkillBtn');
        if (executeSkillBtn) {
            executeSkillBtn.addEventListener('click', () => {
                this.executeSkill();
            });
        }

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
        
        // 获取角色头像
        const avatarUrl = this.getCharacterAvatar(character);
        
        card.innerHTML = `
            <div class="character-header">
                <div class="character-avatar">
                    ${avatarUrl ? `<img src="${avatarUrl}" alt="${name}" style="width: 100%; height: 100%; object-fit: cover; border-radius: inherit;" onload="this.nextElementSibling.style.display='none';" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">` : ''}
                    <div style="${avatarUrl ? 'display: none;' : 'display: flex;'} width: 100%; height: 100%; align-items: center; justify-content: center; font-size: 2.2rem;">${this.getCharacterEmoji(category)}</div>
                </div>
                <div class="character-info">
                    <h3 style="text-align: center !important; display: flex; justify-content: center; align-items: center; margin: 0 auto;">${name}</h3>
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

    getCharacterAvatar(character) {
        // 角色头像映射，使用高质量稳定的头像图片
        const avatarMap = {
            'socrates': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Socrates_Louvre.jpg/300px-Socrates_Louvre.jpg',
            'harry_potter': 'https://upload.wikimedia.org/wikipedia/en/thumb/d/d7/Harry_Potter_character_poster.jpg/220px-Harry_Potter_character_poster.jpg',
            'einstein': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Einstein_1921_by_F_Schmutzer_-_restoration.jpg/300px-Einstein_1921_by_F_Schmutzer_-_restoration.jpg',
            'shakespeare': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Shakespeare.jpg/300px-Shakespeare.jpg',
            'confucius': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Confucius_02.png/256px-Confucius_02.png',
            'marie_curie': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Marie_Curie_c._1920s.jpg/256px-Marie_Curie_c._1920s.jpg'
        };
        
        // 如果没有在映射中找到，尝试使用角色数据中的avatar字段
        const primaryUrl = avatarMap[character.id];
        const fallbackUrl = character.avatar;
        
        return primaryUrl || fallbackUrl || null;
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
        
        suggestions.innerHTML = topMatches.map(character => {
            const avatarUrl = this.getCharacterAvatar(character);
            const avatarDisplay = avatarUrl ? 
                `<img src="${avatarUrl}" alt="${character.name}" style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover; margin-right: 0.5rem;" onerror="this.outerHTML='<span style=\'margin-right: 0.5rem; font-size: 16px;\'>${this.getCharacterEmoji(character.category)}</span>'">` :
                `<span style="margin-right: 0.5rem; font-size: 16px;">${this.getCharacterEmoji(character.category)}</span>`;
            
            return `
                <div class="suggestion-item" onclick="window.app.selectSuggestion('${character.name}')">
                    ${avatarDisplay}
                    <strong>${character.name}</strong>
                </div>
            `;
        }).join('');
        
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
        
        // 设置头像
        const chatAvatar = document.getElementById('chatAvatar');
        const avatarUrl = this.getCharacterAvatar(character);
        
        if (avatarUrl) {
            chatAvatar.innerHTML = `<img src="${avatarUrl}" alt="${character.name}" style="width: 100%; height: 100%; object-fit: cover; border-radius: inherit;" onload="this.nextElementSibling.style.display='none';" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                                    <div style="display: none; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 2.2rem;">${this.getCharacterEmoji(character.category)}</div>`;
        } else {
            chatAvatar.innerHTML = `<div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 2.2rem;">${this.getCharacterEmoji(character.category)}</div>`;
        }

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

        // 获取头像
        let avatar;
        if (sender === 'user') {
            avatar = '👤';
        } else {
            const avatarUrl = this.currentCharacter ? this.getCharacterAvatar(this.currentCharacter) : null;
            if (avatarUrl) {
                avatar = `<img src="${avatarUrl}" alt="${this.currentCharacter.name}" style="width: 32px; height: 32px; border-radius: 50%; object-fit: cover;" onerror="this.outerHTML='${this.getCharacterEmoji(this.currentCharacter?.category)}'">`;
            } else {
                avatar = this.getCharacterEmoji(this.currentCharacter?.category);
            }
        }
        
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
                                    ${(() => {
                                        const avatarUrl = this.getCharacterAvatar(character);
                                        if (avatarUrl) {
                                            return `<img src="${avatarUrl}" alt="${character.name}" style="width: 100%; height: 100%; object-fit: cover; border-radius: inherit;" onload="this.nextElementSibling.style.display='none';" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                                                    <div style="display: none; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 3rem;">${this.getCharacterEmoji(character.category)}</div>`;
                                        } else {
                                            return `<div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 3rem;">${this.getCharacterEmoji(character.category)}</div>`;
                                        }
                                    })()}
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

    // 语音相关功能
    setupVoiceRecording() {
        console.log('🎤 设置语音录制功能...');
        
        // 检查浏览器支持
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            console.warn('⚠️ 浏览器不支持语音录制');
            return;
        }
        
        // 初始化语音录制相关变量
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.websocket = null;
        this.realtimeMode = false;
        
        console.log('✅ 语音录制功能初始化完成');
    }

    async toggleVoiceRecording() {
        console.log('🎤 切换语音录制状态');
        
        if (!this.isRecording) {
            await this.startRecording();
        } else {
            await this.stopRecording();
        }
    }

    async startRecording() {
        try {
            console.log('🎤 开始录音...');
            
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    sampleRate: 16000,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true
                } 
            });
            
            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });
            
            this.audioChunks = [];
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            this.mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                await this.processRecordedAudio(audioBlob);
            };
            
            this.mediaRecorder.start();
            this.isRecording = true;
            
            // 更新UI
            const voiceBtn = document.getElementById('voiceBtn');
            if (voiceBtn) {
                voiceBtn.classList.add('recording');
                voiceBtn.innerHTML = '<i class="fas fa-stop"></i>';
            }
            
            console.log('✅ 录音已开始');
            
        } catch (error) {
            console.error('❌ 开始录音失败:', error);
            this.showError('无法访问麦克风，请检查权限设置');
        }
    }

    async stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            console.log('🛑 停止录音...');
            
            this.mediaRecorder.stop();
            this.isRecording = false;
            
            // 停止所有音频轨道
            if (this.mediaRecorder.stream) {
                this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            }
            
            // 更新UI
            const voiceBtn = document.getElementById('voiceBtn');
            if (voiceBtn) {
                voiceBtn.classList.remove('recording');
                voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            }
            
            console.log('✅ 录音已停止');
        }
    }

    async processRecordedAudio(audioBlob) {
        try {
            console.log('🎵 处理录音数据...');
            
            // 创建FormData
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');
            
            // 发送到服务器进行语音识别
            const response = await fetch('/api/voice/enhanced/recognize', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success && data.text) {
                // 将识别的文字填入输入框
                const messageInput = document.getElementById('messageInput');
                if (messageInput) {
                    messageInput.value = data.text;
                    console.log('✅ 语音识别成功:', data.text);
                }
            } else {
                this.showError(data.error || '语音识别失败');
            }
            
        } catch (error) {
            console.error('❌ 处理录音失败:', error);
            this.showError('语音处理失败: ' + error.message);
        }
    }

    async loadVoiceConfig(characterId) {
        console.log('🔊 加载语音配置:', characterId);
        
        try {
            const response = await fetch(`/api/voice/config/${characterId}?voice_type=auto`);
            const data = await response.json();
            
            if (data.success) {
                this.voiceConfig = data.config;
                console.log('✅ 语音配置加载成功');
                
                // 添加实时语音按钮
                this.addRealtimeVoiceButton();
            }
            
        } catch (error) {
            console.error('❌ 加载语音配置失败:', error);
        }
    }

    addRealtimeVoiceButton() {
        const skillsSection = document.getElementById('skillsSection');
        if (skillsSection && !document.getElementById('realtimeVoiceBtn')) {
            const realtimeBtn = document.createElement('button');
            realtimeBtn.id = 'realtimeVoiceBtn';
            realtimeBtn.className = 'skill-btn';
            realtimeBtn.innerHTML = '🎙️ 实时语音对话';
            realtimeBtn.onclick = () => this.toggleRealtimeVoice();
            
            skillsSection.appendChild(realtimeBtn);
        }
    }

    async toggleRealtimeVoice() {
        if (!this.realtimeMode) {
            await this.startRealtimeVoice();
        } else {
            await this.stopRealtimeVoice();
        }
    }

    async startRealtimeVoice() {
        try {
            console.log('🌐 启动实时语音对话...');
            
            if (!this.currentCharacter) {
                this.showError('请先选择一个角色');
                return;
            }
            
            // 获取实时语音配置
            const response = await fetch('/api/realtime/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    character_id: this.currentCharacter.id
                })
            });
            
            const data = await response.json();
            
            if (!data.success) {
                this.showError(data.error || '启动实时语音失败');
                return;
            }
            
            // 连接WebSocket
            await this.connectWebSocket(data.websocket_url);
            
            this.realtimeMode = true;
            this.updateRealtimeVoiceButton(true);
            
            console.log('✅ 实时语音对话已启动');
            
        } catch (error) {
            console.error('❌ 启动实时语音失败:', error);
            this.showError('启动实时语音失败: ' + error.message);
        }
    }

    async connectWebSocket(url) {
        return new Promise((resolve, reject) => {
            try {
                this.websocket = new WebSocket(url);
                
                this.websocket.onopen = () => {
                    console.log('🔌 WebSocket连接成功');
                    
                    // 发送开始会话消息
                    this.websocket.send(JSON.stringify({
                        type: 'start_voice_session',
                        character_id: this.currentCharacter.id,
                        config: this.voiceConfig || {}
                    }));
                    
                    resolve();
                };
                
                this.websocket.onmessage = (event) => {
                    this.handleWebSocketMessage(JSON.parse(event.data));
                };
                
                this.websocket.onclose = () => {
                    console.log('🔌 WebSocket连接关闭');
                    this.realtimeMode = false;
                    this.updateRealtimeVoiceButton(false);
                };
                
                this.websocket.onerror = (error) => {
                    console.error('❌ WebSocket错误:', error);
                    reject(error);
                };
                
            } catch (error) {
                reject(error);
            }
        });
    }

    handleWebSocketMessage(message) {
        console.log('📨 收到WebSocket消息:', message.type);
        
        switch (message.type) {
            case 'voice_session_started':
                console.log('✅ 语音会话已开始');
                break;
                
            case 'ai_text_response':
                this.addMessage(message.text, 'assistant');
                break;
                
            case 'ai_voice_response':
                this.addMessage(message.text, 'assistant');
                if (message.audio_url) {
                    this.playAudioUrl(message.audio_url);
                }
                break;
                
            case 'error':
                console.error('❌ WebSocket错误:', message.message);
                this.showError('语音服务错误: ' + message.message);
                break;
                
            default:
                console.log('ℹ️ 未处理的消息类型:', message.type);
        }
    }

    async stopRealtimeVoice() {
        try {
            console.log('🛑 停止实时语音对话...');
            
            if (this.websocket) {
                this.websocket.send(JSON.stringify({
                    type: 'stop_voice_session'
                }));
                
                this.websocket.close();
                this.websocket = null;
            }
            
            this.realtimeMode = false;
            this.updateRealtimeVoiceButton(false);
            
            console.log('✅ 实时语音对话已停止');
            
        } catch (error) {
            console.error('❌ 停止实时语音失败:', error);
        }
    }

    updateRealtimeVoiceButton(active) {
        const btn = document.getElementById('realtimeVoiceBtn');
        if (btn) {
            if (active) {
                btn.innerHTML = '🛑 停止实时对话';
                btn.style.backgroundColor = '#e53e3e';
            } else {
                btn.innerHTML = '🎙️ 实时语音对话';
                btn.style.backgroundColor = '';
            }
        }
    }

    async playVoice(text) {
        console.log('🔊 播放语音:', text.substring(0, 50) + '...');
        
        try {
            const response = await fetch('/api/voice/enhanced/synthesize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: text,
                    character_id: this.currentCharacter?.id
                })
            });
            
            const data = await response.json();
            
            if (data.success && data.audio_url) {
                this.playAudioUrl(data.audio_url);
            }
            
        } catch (error) {
            console.error('❌ 语音播放失败:', error);
        }
    }

    playAudioUrl(audioUrl) {
        try {
            const audio = new Audio(audioUrl);
            audio.play().catch(error => {
                console.error('❌ 音频播放失败:', error);
            });
        } catch (error) {
            console.error('❌ 创建音频对象失败:', error);
        }
    }

    showSkillModal(skillName) {
        console.log('🛠️ 显示技能模态框:', skillName);
        
        if (!this.currentCharacter) {
            this.showError('请先选择一个角色');
            return;
        }
        
        const skillModal = document.getElementById('skillModal');
        const skillModalTitle = document.getElementById('skillModalTitle');
        const skillModalBody = document.getElementById('skillModalBody');
        
        // 设置技能标题和内容
        const skillInfo = this.getSkillInfo(skillName);
        skillModalTitle.textContent = skillInfo.title;
        skillModalBody.innerHTML = skillInfo.content;
        
        // 显示模态框
        const modal = new bootstrap.Modal(skillModal);
        modal.show();
        
        // 保存当前技能
        this.currentSkill = skillName;
    }

    getSkillInfo(skillName) {
        const skillMap = {
            'knowledge_qa': {
                title: '知识问答',
                content: `
                    <div class="mb-3">
                        <label class="form-label">请输入您的问题：</label>
                        <textarea class="form-control" id="skillQuestion" rows="3" placeholder="例如：什么是相对论？"></textarea>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">问题类型：</label>
                        <select class="form-select" id="skillQuestionType">
                            <option value="general">一般问题</option>
                            <option value="academic">学术问题</option>
                            <option value="practical">实用问题</option>
                            <option value="philosophical">哲学问题</option>
                        </select>
                    </div>
                `
            },
            'emotional_support': {
                title: '情感陪伴',
                content: `
                    <div class="mb-3">
                        <label class="form-label">您当前的情绪状态：</label>
                        <select class="form-select" id="skillEmotion">
                            <option value="happy">开心</option>
                            <option value="sad">难过</option>
                            <option value="anxious">焦虑</option>
                            <option value="confused">困惑</option>
                            <option value="angry">愤怒</option>
                            <option value="lonely">孤独</option>
                            <option value="stressed">压力大</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">请描述您的情况：</label>
                        <textarea class="form-control" id="skillEmotionMessage" rows="4" placeholder="告诉我发生了什么，我会陪伴您..."></textarea>
                    </div>
                `
            },
            'teaching_guidance': {
                title: '教学指导',
                content: `
                    <div class="mb-3">
                        <label class="form-label">学习主题：</label>
                        <input type="text" class="form-control" id="skillTopic" placeholder="例如：量子物理、古典文学、编程基础">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">您的水平：</label>
                        <select class="form-select" id="skillLevel">
                            <option value="beginner">初学者</option>
                            <option value="intermediate">中级</option>
                            <option value="advanced">高级</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">学习目标：</label>
                        <textarea class="form-control" id="skillGoal" rows="2" placeholder="您希望通过学习达到什么目标？"></textarea>
                    </div>
                `
            },
            'creative_writing': {
                title: '创作协助',
                content: `
                    <div class="mb-3">
                        <label class="form-label">创作类型：</label>
                        <select class="form-select" id="skillWritingType">
                            <option value="story">故事</option>
                            <option value="poem">诗歌</option>
                            <option value="essay">散文</option>
                            <option value="dialogue">对话</option>
                            <option value="script">剧本</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">创作主题：</label>
                        <input type="text" class="form-control" id="skillTheme" placeholder="例如：友谊、冒险、爱情、科幻">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">风格要求：</label>
                        <input type="text" class="form-control" id="skillStyle" placeholder="例如：幽默、悲伤、神秘、浪漫">
                    </div>
                `
            },
            'language_practice': {
                title: '语言练习',
                content: `
                    <div class="mb-3">
                        <label class="form-label">目标语言：</label>
                        <select class="form-select" id="skillLanguage">
                            <option value="Chinese">中文</option>
                            <option value="English">英语</option>
                            <option value="Japanese">日语</option>
                            <option value="Korean">韩语</option>
                            <option value="French">法语</option>
                            <option value="German">德语</option>
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
                        <label class="form-label">练习话题：</label>
                        <input type="text" class="form-control" id="skillPracticeTopic" placeholder="例如：日常生活、工作、旅行、学习">
                    </div>
                `
            }
        };
        
        return skillMap[skillName] || {
            title: '未知技能',
            content: '<p>技能信息不存在</p>'
        };
    }

    async executeSkill() {
        if (!this.currentSkill || !this.currentCharacter) {
            this.showError('技能执行失败：缺少必要信息');
            return;
        }
        
        try {
            // 收集技能参数
            const skillData = this.collectSkillData(this.currentSkill);
            
            if (!skillData) {
                this.showError('请填写完整的技能参数');
                return;
            }
            
            // 发送技能执行请求
            const response = await fetch(`/api/skills/${this.currentSkill}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(skillData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                // 关闭技能模态框
                const skillModal = bootstrap.Modal.getInstance(document.getElementById('skillModal'));
                skillModal.hide();
                
                // 显示技能执行结果
                this.displaySkillResult(data.result);
            } else {
                this.showError('技能执行失败: ' + data.error);
            }
            
        } catch (error) {
            console.error('❌ 技能执行失败:', error);
            this.showError('技能执行失败: ' + error.message);
        }
    }

    collectSkillData(skillName) {
        const skillDataMap = {
            'knowledge_qa': () => {
                const question = document.getElementById('skillQuestion')?.value?.trim();
                const questionType = document.getElementById('skillQuestionType')?.value;
                
                if (!question) return null;
                
                return {
                    question: question,
                    type: questionType
                };
            },
            'emotional_support': () => {
                const emotion = document.getElementById('skillEmotion')?.value;
                const message = document.getElementById('skillEmotionMessage')?.value?.trim();
                
                if (!message) return null;
                
                return {
                    emotion: emotion,
                    message: message
                };
            },
            'teaching_guidance': () => {
                const topic = document.getElementById('skillTopic')?.value?.trim();
                const level = document.getElementById('skillLevel')?.value;
                const goal = document.getElementById('skillGoal')?.value?.trim();
                
                if (!topic) return null;
                
                return {
                    topic: topic,
                    level: level,
                    goal: goal
                };
            },
            'creative_writing': () => {
                const type = document.getElementById('skillWritingType')?.value;
                const theme = document.getElementById('skillTheme')?.value?.trim();
                const style = document.getElementById('skillStyle')?.value?.trim();
                
                if (!theme) return null;
                
                return {
                    type: type,
                    theme: theme,
                    style: style
                };
            },
            'language_practice': () => {
                const language = document.getElementById('skillLanguage')?.value;
                const practiceType = document.getElementById('skillPracticeType')?.value;
                const topic = document.getElementById('skillPracticeTopic')?.value?.trim();
                
                if (!topic) return null;
                
                return {
                    language: language,
                    type: practiceType,
                    topic: topic
                };
            }
        };
        
        const collector = skillDataMap[skillName];
        return collector ? collector() : null;
    }

    displaySkillResult(result) {
        // 根据技能类型显示不同的结果
        let message = '';
        
        switch (result.skill) {
            case 'knowledge_qa':
                message = `📚 ${result.character}的回答：\n\n${result.answer}`;
                break;
            case 'emotional_support':
                message = `💝 ${result.character}的安慰：\n\n${result.support_message}`;
                break;
            case 'teaching_guidance':
                message = `👨‍🏫 ${result.character}的教学：\n\n${result.lesson}`;
                break;
            case 'creative_writing':
                message = `✍️ ${result.character}的创作：\n\n${result.creation}`;
                break;
            case 'language_practice':
                message = `🗣️ ${result.character}的语言指导：\n\n${result.practice_content}`;
                break;
            default:
                message = `🤖 ${result.character || '助手'}：\n\n${JSON.stringify(result, null, 2)}`;
        }
        
        // 添加到聊天界面
        this.addMessage(message, 'assistant');
        
        // 自动播放语音（如果有语音配置）
        if (this.voiceConfig) {
            this.playVoice(message);
        }
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