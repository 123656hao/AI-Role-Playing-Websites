#!/usr/bin/env python3
"""
音频转换工具
用于处理不同格式的音频文件，转换为百度API支持的格式
"""

import struct
import wave
import io
import logging

logger = logging.getLogger(__name__)

class AudioConverter:
    """音频格式转换器"""
    
    @staticmethod
    def create_wav_from_pcm(pcm_data: bytes, sample_rate: int = 16000, channels: int = 1, sample_width: int = 2) -> bytes:
        """
        从PCM数据创建WAV文件
        
        Args:
            pcm_data: PCM音频数据
            sample_rate: 采样率 (默认16kHz)
            channels: 声道数 (默认单声道)
            sample_width: 采样位深 (默认16位)
        
        Returns:
            WAV格式的音频数据
        """
        try:
            # 创建WAV文件头
            wav_header = AudioConverter._create_wav_header(
                len(pcm_data), sample_rate, channels, sample_width
            )
            
            return wav_header + pcm_data
            
        except Exception as e:
            logger.error(f"创建WAV文件失败: {e}")
            return None
    
    @staticmethod
    def _create_wav_header(data_size: int, sample_rate: int, channels: int, sample_width: int) -> bytes:
        """创建WAV文件头"""
        # 计算参数
        byte_rate = sample_rate * channels * sample_width
        block_align = channels * sample_width
        bits_per_sample = sample_width * 8
        
        # 构建WAV头
        header = bytearray(44)
        
        # RIFF标识
        header[0:4] = b'RIFF'
        # 文件大小 - 8
        header[4:8] = struct.pack('<I', data_size + 36)
        # WAVE标识
        header[8:12] = b'WAVE'
        # fmt 子块标识
        header[12:16] = b'fmt '
        # fmt子块大小
        header[16:20] = struct.pack('<I', 16)
        # 音频格式 (PCM = 1)
        header[20:22] = struct.pack('<H', 1)
        # 声道数
        header[22:24] = struct.pack('<H', channels)
        # 采样率
        header[24:28] = struct.pack('<I', sample_rate)
        # 字节率
        header[28:32] = struct.pack('<I', byte_rate)
        # 块对齐
        header[32:34] = struct.pack('<H', block_align)
        # 位深度
        header[34:36] = struct.pack('<H', bits_per_sample)
        # data子块标识
        header[36:40] = b'data'
        # 数据大小
        header[40:44] = struct.pack('<I', data_size)
        
        return bytes(header)
    
    @staticmethod
    def generate_silence_wav(duration_seconds: float = 1.0, sample_rate: int = 16000) -> bytes:
        """
        生成静音WAV文件
        
        Args:
            duration_seconds: 持续时间（秒）
            sample_rate: 采样率
        
        Returns:
            WAV格式的静音音频数据
        """
        try:
            # 计算样本数
            num_samples = int(duration_seconds * sample_rate)
            
            # 创建静音数据（16位PCM，值为0）
            silence_data = b'\x00\x00' * num_samples
            
            # 创建WAV文件
            return AudioConverter.create_wav_from_pcm(silence_data, sample_rate)
            
        except Exception as e:
            logger.error(f"生成静音WAV失败: {e}")
            return None
    
    @staticmethod
    def validate_wav_format(wav_data: bytes) -> dict:
        """
        验证WAV文件格式
        
        Args:
            wav_data: WAV文件数据
        
        Returns:
            包含格式信息的字典
        """
        try:
            if len(wav_data) < 44:
                return {'valid': False, 'error': 'WAV文件太小'}
            
            # 检查RIFF标识
            if wav_data[0:4] != b'RIFF':
                return {'valid': False, 'error': '不是有效的RIFF文件'}
            
            # 检查WAVE标识
            if wav_data[8:12] != b'WAVE':
                return {'valid': False, 'error': '不是有效的WAVE文件'}
            
            # 读取格式信息
            channels = struct.unpack('<H', wav_data[22:24])[0]
            sample_rate = struct.unpack('<I', wav_data[24:28])[0]
            bits_per_sample = struct.unpack('<H', wav_data[34:36])[0]
            
            return {
                'valid': True,
                'channels': channels,
                'sample_rate': sample_rate,
                'bits_per_sample': bits_per_sample,
                'format': 'PCM' if struct.unpack('<H', wav_data[20:22])[0] == 1 else 'Other'
            }
            
        except Exception as e:
            return {'valid': False, 'error': f'解析WAV文件失败: {e}'}
    
    @staticmethod
    def resample_wav_to_16khz(wav_data: bytes) -> bytes:
        """
        将WAV文件重采样到16kHz
        这是一个简化的实现，仅适用于基本的重采样需求
        
        Args:
            wav_data: 原始WAV数据
        
Returns:
            重采样后的WAV数据
        """
        try:
            # 验证格式
            format_info = AudioConverter.validate_wav_format(wav_data)
            if not format_info['valid']:
                logger.error(f"WAV格式无效: {format_info['error']}")
                return None
            
            current_sample_rate = format_info['sample_rate']
            
            # 如果已经是16kHz，直接返回
            if current_sample_rate == 16000:
                return wav_data
            
            # 简单的重采样：如果是8kHz，复制每个样本；如果是32kHz或48kHz，跳过样本
            if current_sample_rate == 8000:
                # 8kHz -> 16kHz: 复制每个样本
                return AudioConverter._upsample_wav(wav_data, 2)
            elif current_sample_rate == 32000:
                # 32kHz -> 16kHz: 跳过每隔一个样本
                return AudioConverter._downsample_wav(wav_data, 2)
            elif current_sample_rate == 48000:
                # 48kHz -> 16kHz: 跳过每隔两个样本
                return AudioConverter._downsample_wav(wav_data, 3)
            else:
                # 其他采样率，返回原始数据并记录警告
                logger.warning(f"不支持的采样率转换: {current_sample_rate}Hz -> 16000Hz")
                return wav_data
                
        except Exception as e:
            logger.error(f"重采样失败: {e}")
            return wav_data
    
    @staticmethod
    def _upsample_wav(wav_data: bytes, factor: int) -> bytes:
        """上采样WAV文件"""
        try:
            # 提取音频数据部分（跳过44字节的头）
            header = wav_data[:44]
            audio_data = wav_data[44:]
            
            # 假设是16位PCM
            samples = []
            for i in range(0, len(audio_data), 2):
                if i + 1 < len(audio_data):
                    sample = struct.unpack('<h', audio_data[i:i+2])[0]
                    # 复制样本
                    for _ in range(factor):
                        samples.append(sample)
            
            # 重新打包音频数据
            new_audio_data = b''.join(struct.pack('<h', sample) for sample in samples)
            
            # 更新头部信息
            new_header = bytearray(header)
            # 更新采样率
            new_header[24:28] = struct.pack('<I', 16000)
            # 更新字节率
            new_header[28:32] = struct.pack('<I', 16000 * 1 * 2)  # 16kHz * 1channel * 2bytes
            # 更新数据大小
            new_header[40:44] = struct.pack('<I', len(new_audio_data))
            # 更新文件大小
            new_header[4:8] = struct.pack('<I', len(new_audio_data) + 36)
            
            return bytes(new_header) + new_audio_data
            
        except Exception as e:
            logger.error(f"上采样失败: {e}")
            return wav_data
    
    @staticmethod
    def _downsample_wav(wav_data: bytes, factor: int) -> bytes:
        """下采样WAV文件"""
        try:
            # 提取音频数据部分（跳过44字节的头）
            header = wav_data[:44]
            audio_data = wav_data[44:]
            
            # 假设是16位PCM
            samples = []
            for i in range(0, len(audio_data), 2 * factor):
                if i + 1 < len(audio_data):
                    sample = struct.unpack('<h', audio_data[i:i+2])[0]
                    samples.append(sample)
            
            # 重新打包音频数据
            new_audio_data = b''.join(struct.pack('<h', sample) for sample in samples)
            
            # 更新头部信息
            new_header = bytearray(header)
            # 更新采样率
            new_header[24:28] = struct.pack('<I', 16000)
            # 更新字节率
            new_header[28:32] = struct.pack('<I', 16000 * 1 * 2)  # 16kHz * 1channel * 2bytes
            # 更新数据大小
            new_header[40:44] = struct.pack('<I', len(new_audio_data))
            # 更新文件大小
            new_header[4:8] = struct.pack('<I', len(new_audio_data) + 36)
            
            return bytes(new_header) + new_audio_data
            
        except Exception as e:
            logger.error(f"下采样失败: {e}")
            return wav_data