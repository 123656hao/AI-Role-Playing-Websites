/**
 * 语音聊天应用 - 前端JavaScript
 * 支持百度语音识别的实时语音对话
 */

class VoiceChatApp {
    constructor() {
        this.socket = null;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.currentCharacter = null;
        this.conversationId = null;
        this.audioConverter = null;
        
        this.init();
    }
    
    init() {
        this.initElements();
        this.initSocketIO();
        this.loadCharacters();
        this.bindEvents();
        this.checkVoiceStatus();
        this.initAudioConverter();
    }
    
    initAudioConverter() {
        if (window.AudioConverter && AudioConverter.isSupported()) {
            this.audioConverter = new AudioConverter();
            console.log('音频转换器初始化成功');
        } else {
            console.warn('浏览器不支持音频转换功能');
        }
    }
    
    initElements() {
        // 获取DOM元素
        this.chatContainer = document.getElementById('chat-container');
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.voiceButton = document.getElementById('voice-button');
        this.characterSelect = document.getElementById('character-select');
        this.statusIndicator = document.getElementById('status-indicator');
        this.voiceStatus = document.getElementById('voice-status');
        
        // 创建音频元素
        this.audioPlayer = document.createElement('audio');
        this.audioPlayer.controls = false;
    }
    
    initSocketIO() {
        // 初始化Socket.IO连接
        this.socket = io();
        
        this.socket.on('connect', () => {
            this.updateStatus('已连接', 'success');
            console.log('Socket.IO连接成功');
        });
        
        this.socket.on('disconnect', () => {
            this.updateStatus('连接断开', 'error');
            console.log('Socket.IO连接断开');
        });
        
        this.socket.on('chat_response', (data) => {
            this.displayMessage(data.response, 'ai', data.character, '', data.audio_url);
        });
        
        this.socket.on('error', (data) => {
            this.showError(data.message);
        });
    }
    
    async loadCharacters() {
        try {
            const response = await fetch('/api/characters');
            const data = await response.json();
            
            if (data.success) {
                this.populateCharacterSelect(data.characters);
            } else {
                this.showError('加载角色失败: ' + data.error);
            }
        } catch (error) {
            this.showError('加载角色失败: ' + error.message);
        }
    }
    
    populateCharacterSelect(characters) {
        this.characterSelect.innerHTML = '<option value="">选择角色...</option>';
        
        characters.forEach(character => {
            const option = document.createElement('option');
            option.value = character.id;
            option.textContent = character.name;
            this.characterSelect.appendChild(option);
        });
    }
    
    bindEvents() {
        // 发送按钮事件
        this.sendButton.addEventListener('click', () => {
            this.sendTextMessage();
        });
        
        // 输入框回车事件
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendTextMessage();
            }
        });
        
        // 语音按钮事件
        this.voiceButton.addEventListener('mousedown', () => {
            this.startRecording();
        });
        
        this.voiceButton.addEventListener('mouseup', () => {
            this.stopRecording();
        });
        
        this.voiceButton.addEventListener('mouseleave', () => {
            if (this.isRecording) {
                this.stopRecording();
            }
        });
        
        // 角色选择事件
        this.characterSelect.addEventListener('change', () => {
            this.selectCharacter();
        });
    }
    
    async checkVoiceStatus() {
        try {
            const response = await fetch('/api/voice/status');
            const data = await response.json();
            
            if (data.success) {
                const status = data.status;
                const testResult = data.test_result;
                
                let statusText = '语音服务状态: ';
                let statusClass = 'success';
                
                if (status.configured && testResult.api_accessible) {
                    statusText += '✅ 百度语音识别已配置并可用';
                } else if (status.configured && !testResult.api_accessible) {
                    statusText += '⚠️ 百度语音识别已配置但API不可访问';
                    statusClass = 'warning';
                } else {
                    statusText += '❌ 百度语音识别未配置';
                    statusClass = 'error';
                }
                
                this.updateVoiceStatus(statusText, statusClass);
            }
        } catch (error) {
            this.updateVoiceStatus('❌ 无法获取语音服务状态', 'error');
        }
    }
    
    selectCharacter() {
        const characterId = this.characterSelect.value;
        if (characterId) {
            // 这里可以获取角色详细信息
            this.currentCharacter = characterId;
            this.updateStatus(`已选择角色: ${this.characterSelect.selectedOptions[0].text}`, 'success');
        }
    }
    
    sendTextMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        if (!this.currentCharacter) {
            this.showError('请先选择一个角色');
            return;
        }
        
        // 显示用户消息
        this.displayMessage(message, 'user');
        
        // 发送消息到服务器
        this.socket.emit('chat_message', {
            message: message,
            character_id: this.currentCharacter
        });
        
        // 清空输入框
        this.messageInput.value = '';
    }
    
    async startRecording() {
        if (!this.currentCharacter) {
            this.showError('请先选择一个角色');
            return;
        }
        
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                    sampleRate: 16000
                }
            });
            
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];
            
            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };
            
            this.mediaRecorder.onstop = () => {
                this.processRecording();
            };
            
            this.mediaRecorder.start();
            this.isRecording = true;
            
            // 更新UI
            this.voiceButton.classList.add('recording');
            this.voiceButton.textContent = '🔴 录音中...';
            
            // 添加录音指导提示
            this.updateStatus('🎤 正在录音... 请清晰地说话', 'recording');
            
            // 录音时间提示
            let recordingTime = 0;
            this.recordingTimer = setInterval(() => {
                if (this.isRecording) {
                    recordingTime++;
                    if (recordingTime === 1) {
                        this.updateStatus('🎤 录音中... 请说出您的问题（建议3-8秒）', 'recording');
                    } else if (recordingTime === 3) {
                        this.updateStatus('🎤 继续录音... 说话要清晰响亮', 'recording');
                    } else if (recordingTime === 8) {
                        this.updateStatus('🎤 录音时间较长，可以松开按钮结束', 'recording');
                    } else if (recordingTime >= 15) {
                        this.updateStatus('⏰ 录音时间过长，建议重新录制', 'warning');
                    }
                } else {
                    clearInterval(this.recordingTimer);
                }
            }, 1000);
            
        } catch (error) {
            let errorMsg = '无法访问麦克风';
            if (error.name === 'NotAllowedError') {
                errorMsg = '麦克风权限被拒绝，请在浏览器设置中允许麦克风访问';
            } else if (error.name === 'NotFoundError') {
                errorMsg = '未找到麦克风设备，请检查设备连接';
            }
            this.showError(errorMsg + ': ' + error.message);
        }
    }
    
    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            
            // 清除录音计时器
            if (this.recordingTimer) {
                clearInterval(this.recordingTimer);
                this.recordingTimer = null;
            }
            
            // 停止所有音频轨道
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            
            // 更新UI
            this.voiceButton.classList.remove('recording');
            this.voiceButton.textContent = '🎤 按住说话';
            this.updateStatus('🔄 处理语音中，请稍候...', 'processing');
        }
    }
    
    async processRecording() {
        try {
            let audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
            let filename = 'recording.webm';
            
            // 检查是否需要格式转换
            if (audioBlob.type.includes('webm') && this.audioConverter) {
                this.updateStatus('转换音频格式...', 'processing');
                
                try {
                    // 转换WebM到WAV
                    audioBlob = await this.audioConverter.convertWebMToWAV(audioBlob);
                    filename = 'recording.wav';
                    
                    console.log('音频格式转换成功: WebM -> WAV');
                    this.updateStatus('音频转换完成，开始识别...', 'processing');
                    
                } catch (convertError) {
                    console.error('音频转换失败:', convertError);
                    this.showError('音频格式转换失败，请尝试使用其他录音方式');
                    return;
                }
            }
            
            // 创建FormData
            const formData = new FormData();
            formData.append('audio', audioBlob, filename);
            
            // 发送到服务器进行语音识别
            const response = await fetch('/api/voice/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                const recognizedText = data.text;
                
                // 显示识别的文字
                this.displayMessage(recognizedText, 'user', null, '🎤 ');
                
                // 发送给AI
                this.socket.emit('chat_message', {
                    message: recognizedText,
                    character_id: this.currentCharacter
                });
                
                this.updateStatus('语音识别成功', 'success');
            } else {
                this.showError('语音识别失败: ' + data.error);
            }
            
        } catch (error) {
            this.showError('处理录音失败: ' + error.message);
        }
    }
    
    displayMessage(message, sender, character = null, prefix = '', audioUrl = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const timestamp = new Date().toLocaleTimeString();
        
        let senderName = '';
        if (sender === 'user') {
            senderName = '你';
        } else if (sender === 'ai' && character) {
            senderName = character.name || '助手';
        } else {
            senderName = '助手';
        }
        
        // 创建消息内容
        let messageContent = `
            <div class="message-header">
                <span class="sender">${senderName}</span>
                <span class="timestamp">${timestamp}</span>
            </div>
            <div class="message-content">${prefix}${message}`;
        
        // 如果是AI消息且有音频URL，添加播放按钮
        if (sender === 'ai' && audioUrl) {
            messageContent += `
                <div class="audio-controls">
                    <button class="play-audio-btn" onclick="voiceChatApp.playAudio('${audioUrl}')">
                        🔊 播放语音
                    </button>
                </div>`;
        }
        
        messageContent += `</div>`;
        messageDiv.innerHTML = messageContent;
        
        this.chatContainer.appendChild(messageDiv);
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
        
        // 如果是AI消息且有音频，自动播放
        if (sender === 'ai' && audioUrl) {
            setTimeout(() => {
                this.playAudio(audioUrl);
            }, 500); // 延迟500ms播放，让用户看到消息
        }
    }
    
    updateStatus(message, type = 'info') {
        if (this.statusIndicator) {
            this.statusIndicator.textContent = message;
            this.statusIndicator.className = `status ${type}`;
        }
    }
    
    updateVoiceStatus(message, type = 'info') {
        if (this.voiceStatus) {
            this.voiceStatus.textContent = message;
            this.voiceStatus.className = `voice-status ${type}`;
        }
    }
    
    showError(message) {
        console.error(message);
        this.updateStatus('错误: ' + message, 'error');
        
        // 也可以显示在聊天区域
        this.displayMessage('❌ ' + message, 'system');
    }
    
    playAudio(audioUrl) {
        // 播放音频
        try {
            // 停止当前播放的音频
            if (this.audioPlayer && !this.audioPlayer.paused) {
                this.audioPlayer.pause();
                this.audioPlayer.currentTime = 0;
            }
            
            // 设置新的音频源
            this.audioPlayer.src = audioUrl;
            
            // 播放音频
            const playPromise = this.audioPlayer.play();
            
            if (playPromise !== undefined) {
                playPromise.then(() => {
                    console.log('音频播放开始');
                    this.updateStatus('正在播放语音...', 'success');
                    this.updateAudioStatus('正在播放...');
                }).catch(error => {
                    console.error('音频播放失败:', error);
                    this.updateStatus('音频播放失败', 'error');
                    this.updateAudioStatus('播放失败');
                });
            }
            
            // 监听播放结束事件
            this.audioPlayer.onended = () => {
                console.log('音频播放结束');
                this.updateStatus('准备就绪', 'success');
                this.updateAudioStatus('音频就绪');
            };
            
            // 监听播放错误事件
            this.audioPlayer.onerror = (error) => {
                console.error('音频播放错误:', error);
                this.updateStatus('音频播放错误', 'error');
                this.updateAudioStatus('播放错误');
            };
            
        } catch (error) {
            console.error('播放音频时出错:', error);
            this.updateStatus('播放音频失败: ' + error.message, 'error');
        }
    }
    
    stopAudio() {
        // 停止音频播放
        if (this.audioPlayer && !this.audioPlayer.paused) {
            this.audioPlayer.pause();
            this.audioPlayer.currentTime = 0;
            this.updateStatus('音频播放已停止', 'warning');
            this.updateAudioStatus('播放已停止');
        }
    }
    
    updateAudioStatus(message) {
        const audioStatus = document.getElementById('audio-status');
        if (audioStatus) {
            audioStatus.textContent = message;
        }
    }
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.voiceChatApp = new VoiceChatApp();
});