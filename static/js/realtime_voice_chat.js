/**
 * 实时语音对话应用
 * 支持连续语音识别和自然对话流程
 */

class RealtimeVoiceApp {
    constructor() {
        this.socket = null;
        this.mediaRecorder = null;
        this.audioStream = null;
        this.isListening = false;
        this.isProcessing = false;
        this.continuousMode = false;
        this.currentCharacter = null;
        this.conversationId = null;
        this.audioChunks = [];
        this.audioContext = null;
        this.analyser = null;
        this.audioPlayer = null;
        
        // 语音检测参数
        this.silenceThreshold = 0.01;
        this.silenceTimeout = 2000; // 2秒静音后自动停止
        this.silenceTimer = null;
        this.isAutoStopping = false;
        
        this.init();
    }
    
    init() {
        this.initElements();
        this.initSocketIO();
        this.initAudioContext();
        this.loadCharacters();
        this.bindEvents();
        this.checkServices();
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
        this.chatContainer = document.getElementById('chat-container');
        this.voiceButton = document.getElementById('voice-button');
        this.voiceStatus = document.getElementById('voice-status');
        this.characterSelect = document.getElementById('character-select');
        this.connectionStatus = document.getElementById('connection-status');
        this.voiceServiceStatus = document.getElementById('voice-service-status');
        this.continuousToggle = document.getElementById('continuous-toggle');
        this.audioVisualizer = document.getElementById('audio-visualizer');
        
        // 创建音频播放器
        this.audioPlayer = document.createElement('audio');
        this.audioPlayer.controls = false;
        
        // 创建音频可视化条
        this.createAudioVisualizer();
    }
    
    createAudioVisualizer() {
        const visualizer = this.audioVisualizer;
        visualizer.innerHTML = '';
        
        for (let i = 0; i < 20; i++) {
            const bar = document.createElement('div');
            bar.className = 'audio-bar';
            bar.style.height = '5px';
            visualizer.appendChild(bar);
        }
    }
    
    initSocketIO() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            this.updateConnectionStatus('已连接', 'success');
            console.log('Socket.IO连接成功');
        });
        
        this.socket.on('disconnect', () => {
            this.updateConnectionStatus('连接断开', 'error');
            console.log('Socket.IO连接断开');
        });
        
        this.socket.on('chat_response', (data) => {
            this.handleAIResponse(data);
        });
        
        this.socket.on('error', (data) => {
            this.showError(data.message);
        });
    }
    
    initAudioContext() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } catch (error) {
            console.error('音频上下文初始化失败:', error);
        }
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
        this.characterSelect.innerHTML = '<option value="">选择AI角色...</option>';
        
        characters.forEach(character => {
            const option = document.createElement('option');
            option.value = character.id;
            option.textContent = `${character.name} - ${character.description}`;
            this.characterSelect.appendChild(option);
        });
    }
    
    bindEvents() {
        // 角色选择事件
        this.characterSelect.addEventListener('change', () => {
            this.selectCharacter();
        });
        
        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && !e.repeat) {
                e.preventDefault();
                if (!this.isListening && this.currentCharacter) {
                    this.startListening();
                }
            }
        });
        
        document.addEventListener('keyup', (e) => {
            if (e.code === 'Space') {
                e.preventDefault();
                if (this.isListening && !this.continuousMode) {
                    this.stopListening();
                }
            }
        });
    }
    
    async checkServices() {
        try {
            const response = await fetch('/api/voice/status');
            const data = await response.json();
            
            if (data.success) {
                const status = data.status;
                const testResult = data.test_result;
                
                if (status.configured && testResult.api_accessible) {
                    this.updateVoiceServiceStatus('语音服务就绪', 'success');
                } else {
                    this.updateVoiceServiceStatus('语音服务异常', 'warning');
                }
            }
        } catch (error) {
            this.updateVoiceServiceStatus('服务检查失败', 'error');
        }
    }
    
    selectCharacter() {
        const characterId = this.characterSelect.value;
        if (characterId) {
            this.currentCharacter = characterId;
            this.updateVoiceStatus('点击麦克风开始对话');
            this.voiceButton.disabled = false;
        } else {
            this.currentCharacter = null;
            this.updateVoiceStatus('请先选择角色');
            this.voiceButton.disabled = true;
        }
    }
    
    toggleVoice() {
        if (!this.currentCharacter) {
            this.showError('请先选择一个角色');
            return;
        }
        
        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }
    
    async startListening() {
        if (this.isListening || this.isProcessing) return;
        
        try {
            // 获取麦克风权限
            this.audioStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                    sampleRate: 16000
                }
            });
            
            // 设置音频分析器
            this.setupAudioAnalyser();
            
            // 创建录音器
            this.mediaRecorder = new MediaRecorder(this.audioStream, {
                mimeType: 'audio/webm;codecs=opus'
            });
            
            this.audioChunks = [];
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            this.mediaRecorder.onstop = () => {
                this.processAudio();
            };
            
            // 开始录音
            this.mediaRecorder.start(100); // 每100ms收集一次数据
            this.isListening = true;
            
            // 更新UI
            this.updateVoiceButton('listening');
            this.updateVoiceStatus('正在聆听...');
            this.audioVisualizer.style.display = 'flex';
            
            // 开始音频可视化
            this.startAudioVisualization();
            
            // 如果不是连续模式，设置静音检测
            if (!this.continuousMode) {
                this.startSilenceDetection();
            }
            
            console.log('开始语音录制');
            
        } catch (error) {
            this.handleMicrophoneError(error);
        }
    }
    
    stopListening() {
        if (!this.isListening) return;
        
        this.isListening = false;
        
        // 停止录音
        if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
            this.mediaRecorder.stop();
        }
        
        // 停止音频流
        if (this.audioStream) {
            this.audioStream.getTracks().forEach(track => track.stop());
            this.audioStream = null;
        }
        
        // 清除静音检测
        if (this.silenceTimer) {
            clearTimeout(this.silenceTimer);
            this.silenceTimer = null;
        }
        
        // 更新UI
        this.updateVoiceButton('processing');
        this.updateVoiceStatus('处理语音中...');
        this.audioVisualizer.style.display = 'none';
        
        console.log('停止语音录制');
    }
    
    setupAudioAnalyser() {
        if (!this.audioContext || !this.audioStream) return;
        
        const source = this.audioContext.createMediaStreamSource(this.audioStream);
        this.analyser = this.audioContext.createAnalyser();
        this.analyser.fftSize = 256;
        source.connect(this.analyser);
    }
    
    startAudioVisualization() {
        if (!this.analyser) return;
        
        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        const bars = this.audioVisualizer.querySelectorAll('.audio-bar');
        
        const animate = () => {
            if (!this.isListening) return;
            
            this.analyser.getByteFrequencyData(dataArray);
            
            // 更新可视化条
            for (let i = 0; i < bars.length; i++) {
                const value = dataArray[i * 2] || 0;
                const height = Math.max(5, (value / 255) * 50);
                bars[i].style.height = height + 'px';
            }
            
            requestAnimationFrame(animate);
        };
        
        animate();
    }
    
    startSilenceDetection() {
        if (!this.analyser) return;
        
        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        
        const checkSilence = () => {
            if (!this.isListening || this.isAutoStopping) return;
            
            this.analyser.getByteTimeDomainData(dataArray);
            
            // 计算音量
            let sum = 0;
            for (let i = 0; i < bufferLength; i++) {
                const sample = (dataArray[i] - 128) / 128;
                sum += sample * sample;
            }
            const volume = Math.sqrt(sum / bufferLength);
            
            if (volume < this.silenceThreshold) {
                // 检测到静音
                if (!this.silenceTimer) {
                    this.silenceTimer = setTimeout(() => {
                        if (this.isListening && !this.continuousMode) {
                            this.isAutoStopping = true;
                            this.stopListening();
                            setTimeout(() => {
                                this.isAutoStopping = false;
                            }, 1000);
                        }
                    }, this.silenceTimeout);
                }
            } else {
                // 有声音，清除静音计时器
                if (this.silenceTimer) {
                    clearTimeout(this.silenceTimer);
                    this.silenceTimer = null;
                }
            }
            
            setTimeout(checkSilence, 100);
        };
        
        checkSilence();
    }
    
    async processAudio() {
        if (this.audioChunks.length === 0) {
            this.resetVoiceButton();
            return;
        }
        
        this.isProcessing = true;
        
        try {
            // 创建音频Blob
            let audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
            let filename = 'recording.webm';
            
            // 检查是否需要格式转换
            if (audioBlob.type.includes('webm') && this.audioConverter) {
                this.updateVoiceStatus('转换音频格式...');
                
                try {
                    // 转换WebM到WAV
                    audioBlob = await this.audioConverter.convertWebMToWAV(audioBlob);
                    filename = 'recording.wav';
                    
                    console.log('音频格式转换成功: WebM -> WAV');
                    this.updateVoiceStatus('音频转换完成，开始识别...');
                    
                } catch (convertError) {
                    console.error('音频转换失败:', convertError);
                    this.showError('音频格式转换失败，请尝试使用其他录音方式');
                    return;
                }
            }
            
            const processedBlob = audioBlob;
            
            // 创建FormData
            const formData = new FormData();
            formData.append('audio', processedBlob, filename);
            
            // 发送到服务器进行语音识别
            const response = await fetch('/api/voice/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                const recognizedText = data.text;
                
                // 显示用户消息
                this.displayMessage(recognizedText, 'user', '🎤 ');
                
                // 发送给AI
                this.socket.emit('chat_message', {
                    message: recognizedText,
                    character_id: this.currentCharacter
                });
                
                this.updateVoiceStatus('等待AI回复...');
            } else {
                this.showError('语音识别失败: ' + data.error);
                this.resetVoiceButton();
            }
            
        } catch (error) {
            this.showError('处理语音失败: ' + error.message);
            this.resetVoiceButton();
        }
        
        this.isProcessing = false;
    }
    
    async convertAudioFormat(audioBlob) {
        // 如果有音频转换器，使用它
        if (this.audioConverter) {
            try {
                return await this.audioConverter.convertWebMToWAV(audioBlob);
            } catch (error) {
                console.warn('音频转换失败，使用原始格式:', error);
                return audioBlob;
            }
        }
        
        return audioBlob;
    }
    
    handleAIResponse(data) {
        // 显示AI回复
        this.displayMessage(data.response, 'ai', data.character);
        
        // 播放语音回复
        if (data.audio_url) {
            this.playAudio(data.audio_url);
        }
        
        // 重置语音按钮
        this.resetVoiceButton();
        
        // 如果是连续模式，自动开始下一轮监听
        if (this.continuousMode && !this.isAutoStopping) {
            setTimeout(() => {
                this.startListening();
            }, 1000);
        }
    }
    
    displayMessage(message, sender, character = null, prefix = '') {
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
        
        messageDiv.innerHTML = `
            <div class="message-content">${prefix}${message}</div>
        `;
        
        this.chatContainer.appendChild(messageDiv);
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
        
        // 清空空状态
        const emptyState = this.chatContainer.querySelector('.empty-state');
        if (emptyState) {
            emptyState.remove();
        }
    }
    
    playAudio(audioUrl) {
        try {
            this.audioPlayer.src = audioUrl;
            
            const playPromise = this.audioPlayer.play();
            
            if (playPromise !== undefined) {
                playPromise.then(() => {
                    console.log('AI语音播放开始');
                }).catch(error => {
                    console.error('AI语音播放失败:', error);
                });
            }
            
        } catch (error) {
            console.error('播放AI语音时出错:', error);
        }
    }
    
    updateVoiceButton(state) {
        this.voiceButton.className = `voice-button ${state}`;
        
        switch (state) {
            case 'idle':
                this.voiceButton.textContent = '🎤';
                break;
            case 'listening':
                this.voiceButton.textContent = '🔴';
                break;
            case 'processing':
                this.voiceButton.textContent = '⏳';
                break;
        }
    }
    
    resetVoiceButton() {
        this.updateVoiceButton('idle');
        this.updateVoiceStatus(this.continuousMode ? '连续对话模式' : '点击开始对话');
    }
    
    updateVoiceStatus(message) {
        this.voiceStatus.textContent = message;
        
        // 更新状态样式
        this.voiceStatus.className = 'voice-status';
        if (message.includes('聆听') || message.includes('录音')) {
            this.voiceStatus.classList.add('listening');
        } else if (message.includes('处理') || message.includes('等待')) {
            this.voiceStatus.classList.add('processing');
        } else {
            this.voiceStatus.classList.add('idle');
        }
    }
    
    updateConnectionStatus(message, type) {
        this.connectionStatus.textContent = message;
        this.connectionStatus.className = `status ${type}`;
    }
    
    updateVoiceServiceStatus(message, type) {
        this.voiceServiceStatus.textContent = message;
        this.voiceServiceStatus.className = `status ${type}`;
    }
    
    toggleContinuousMode() {
        this.continuousMode = !this.continuousMode;
        
        if (this.continuousMode) {
            this.continuousToggle.classList.add('active');
            this.updateVoiceStatus('连续对话模式已开启');
        } else {
            this.continuousToggle.classList.remove('active');
            this.updateVoiceStatus('连续对话模式已关闭');
        }
        
        console.log('连续对话模式:', this.continuousMode ? '开启' : '关闭');
    }
    
    stopAll() {
        // 停止录音
        if (this.isListening) {
            this.stopListening();
        }
        
        // 停止音频播放
        if (this.audioPlayer && !this.audioPlayer.paused) {
            this.audioPlayer.pause();
            this.audioPlayer.currentTime = 0;
        }
        
        // 重置状态
        this.resetVoiceButton();
        this.updateVoiceStatus('已停止');
    }
    
    clearChat() {
        this.chatContainer.innerHTML = `
            <div class="empty-state">
                <h3>🎯 开始语音对话</h3>
                <p>选择一个AI角色，然后点击麦克风按钮开始对话</p>
                <p>💡 支持连续对话模式，让交流更自然</p>
            </div>
        `;
    }
    
    handleMicrophoneError(error) {
        let errorMsg = '无法访问麦克风';
        
        if (error.name === 'NotAllowedError') {
            errorMsg = '麦克风权限被拒绝，请在浏览器设置中允许麦克风访问';
        } else if (error.name === 'NotFoundError') {
            errorMsg = '未找到麦克风设备，请检查设备连接';
        } else if (error.name === 'NotReadableError') {
            errorMsg = '麦克风被其他应用占用，请关闭其他使用麦克风的应用';
        }
        
        this.showError(errorMsg);
        this.resetVoiceButton();
    }
    
    showError(message) {
        console.error(message);
        this.updateVoiceStatus('错误: ' + message);
        
        // 显示错误消息
        this.displayMessage('❌ ' + message, 'system');
        
        // 3秒后重置状态
        setTimeout(() => {
            if (this.currentCharacter) {
                this.resetVoiceButton();
            } else {
                this.updateVoiceStatus('请先选择角色');
            }
        }, 3000);
    }
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.realtimeVoiceApp = new RealtimeVoiceApp();
    
    // 添加使用提示
    console.log('🎤 实时语音对话已就绪');
    console.log('💡 使用提示:');
    console.log('   - 选择AI角色后点击麦克风开始对话');
    console.log('   - 支持空格键快捷操作');
    console.log('   - 开启连续模式可进行自然对话');
    console.log('   - 静音2秒后自动停止录音');
});