/**
 * 浏览器端音频格式转换工具
 * 将WebM格式转换为WAV格式
 */

class AudioConverter {
    constructor() {
        this.audioContext = null;
        this.initAudioContext();
    }
    
    initAudioContext() {
        try {
            // 创建音频上下文
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            this.audioContext = new AudioContext();
        } catch (error) {
            console.error('音频上下文初始化失败:', error);
        }
    }
    
    /**
     * 将WebM音频转换为WAV格式
     * @param {Blob} webmBlob - WebM格式的音频Blob
     * @returns {Promise<Blob>} WAV格式的音频Blob
     */
    async convertWebMToWAV(webmBlob) {
        try {
            console.log('开始转换WebM到WAV格式...');
            
            // 读取WebM文件为ArrayBuffer
            const arrayBuffer = await this.blobToArrayBuffer(webmBlob);
            
            // 解码音频数据
            let audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
            
            // 确保音频是16kHz采样率
            if (audioBuffer.sampleRate !== 16000) {
                console.log(`重采样: ${audioBuffer.sampleRate}Hz -> 16000Hz`);
                audioBuffer = await this.resampleAudio(audioBuffer, 16000);
            }
            
            // 转换为WAV格式
            const wavBlob = this.audioBufferToWAV(audioBuffer, 16000);
            
            console.log('WebM到WAV转换完成，采样率: 16000Hz');
            return wavBlob;
            
        } catch (error) {
            console.error('WebM到WAV转换失败:', error);
            throw new Error('音频格式转换失败: ' + error.message);
        }
    }
    
    /**
     * 将Blob转换为ArrayBuffer
     */
    blobToArrayBuffer(blob) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsArrayBuffer(blob);
        });
    }
    
    /**
     * 将AudioBuffer转换为WAV格式的Blob
     */
    audioBufferToWAV(audioBuffer, targetSampleRate = 16000) {
        const length = audioBuffer.length;
        const sampleRate = targetSampleRate; // 使用目标采样率
        const channels = 1; // 强制单声道
        
        // 创建WAV文件缓冲区
        const buffer = new ArrayBuffer(44 + length * channels * 2);
        const view = new DataView(buffer);
        
        // 写入WAV文件头
        this.writeWAVHeader(view, length, sampleRate, channels);
        
        // 写入音频数据（转换为单声道）
        this.writeAudioDataMono(view, audioBuffer, length);
        
        return new Blob([buffer], { type: 'audio/wav' });
    }
    
    /**
     * 写入WAV文件头
     */
    writeWAVHeader(view, length, sampleRate, channels) {
        const byteRate = sampleRate * channels * 2;
        const blockAlign = channels * 2;
        
        // RIFF标识符
        this.writeString(view, 0, 'RIFF');
        // 文件大小
        view.setUint32(4, 36 + length * channels * 2, true);
        // WAVE标识符
        this.writeString(view, 8, 'WAVE');
        // fmt子块
        this.writeString(view, 12, 'fmt ');
        // fmt子块大小
        view.setUint32(16, 16, true);
        // 音频格式 (PCM = 1)
        view.setUint16(20, 1, true);
        // 声道数
        view.setUint16(22, channels, true);
        // 采样率
        view.setUint32(24, sampleRate, true);
        // 字节率
        view.setUint32(28, byteRate, true);
        // 块对齐
        view.setUint16(32, blockAlign, true);
        // 位深度
        view.setUint16(34, 16, true);
        // data子块
        this.writeString(view, 36, 'data');
        // 数据大小
        view.setUint32(40, length * channels * 2, true);
    }
    
    /**
     * 写入音频数据
     */
    writeAudioData(view, audioBuffer, length, channels) {
        let offset = 44;
        
        for (let i = 0; i < length; i++) {
            for (let channel = 0; channel < channels; channel++) {
                const channelData = audioBuffer.getChannelData(channel);
                // 将浮点数转换为16位整数
                const sample = Math.max(-1, Math.min(1, channelData[i]));
                const intSample = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
                view.setInt16(offset, intSample, true);
                offset += 2;
            }
        }
    }
    
    /**
     * 写入单声道音频数据
     */
    writeAudioDataMono(view, audioBuffer, length) {
        let offset = 44;
        const channels = audioBuffer.numberOfChannels;
        
        for (let i = 0; i < length; i++) {
            let sample = 0;
            
            // 如果是多声道，混合为单声道
            if (channels > 1) {
                for (let channel = 0; channel < channels; channel++) {
                    const channelData = audioBuffer.getChannelData(channel);
                    sample += channelData[i];
                }
                sample /= channels; // 平均值
            } else {
                const channelData = audioBuffer.getChannelData(0);
                sample = channelData[i];
            }
            
            // 将浮点数转换为16位整数
            sample = Math.max(-1, Math.min(1, sample));
            const intSample = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
            view.setInt16(offset, intSample, true);
            offset += 2;
        }
    }
    
    /**
     * 写入字符串到DataView
     */
    writeString(view, offset, string) {
        for (let i = 0; i < string.length; i++) {
            view.setUint8(offset + i, string.charCodeAt(i));
        }
    }
    
    /**
     * 重采样音频到指定采样率
     */
    async resampleAudio(audioBuffer, targetSampleRate = 16000) {
        try {
            const currentSampleRate = audioBuffer.sampleRate;
            
            if (currentSampleRate === targetSampleRate) {
                return audioBuffer;
            }
            
            console.log(`重采样: ${currentSampleRate}Hz -> ${targetSampleRate}Hz`);
            
            // 创建离线音频上下文进行重采样
            const offlineContext = new OfflineAudioContext(
                audioBuffer.numberOfChannels,
                audioBuffer.duration * targetSampleRate,
                targetSampleRate
            );
            
            // 创建音频源
            const source = offlineContext.createBufferSource();
            source.buffer = audioBuffer;
            source.connect(offlineContext.destination);
            source.start();
            
            // 渲染重采样后的音频
            const resampledBuffer = await offlineContext.startRendering();
            
            console.log('重采样完成');
            return resampledBuffer;
            
        } catch (error) {
            console.error('重采样失败:', error);
            return audioBuffer; // 返回原始音频
        }
    }
    
    /**
     * 获取音频信息
     */
    getAudioInfo(audioBuffer) {
        return {
            duration: audioBuffer.duration,
            sampleRate: audioBuffer.sampleRate,
            channels: audioBuffer.numberOfChannels,
            length: audioBuffer.length
        };
    }
    
    /**
     * 检查浏览器是否支持音频转换
     */
    static isSupported() {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        return !!(AudioContext && window.FileReader);
    }
}

// 导出类
window.AudioConverter = AudioConverter;