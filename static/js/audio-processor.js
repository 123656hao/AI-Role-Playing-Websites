/**
 * AudioWorklet处理器
 * 用于实时音频数据处理
 */

class AudioProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        this.bufferSize = 4096;
        this.buffer = new Float32Array(this.bufferSize);
        this.bufferIndex = 0;
    }
    
    process(inputs, outputs, parameters) {
        const input = inputs[0];
        
        if (input.length > 0) {
            const inputChannel = input[0];
            
            for (let i = 0; i < inputChannel.length; i++) {
                this.buffer[this.bufferIndex] = inputChannel[i];
                this.bufferIndex++;
                
                // 当缓冲区满时，发送数据
                if (this.bufferIndex >= this.bufferSize) {
                    this.port.postMessage({
                        type: 'audio-data',
                        audioData: new Float32Array(this.buffer)
                    });
                    
                    this.bufferIndex = 0;
                }
            }
        }
        
        return true;
    }
}

registerProcessor('audio-processor', AudioProcessor);