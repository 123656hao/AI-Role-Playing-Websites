#!/usr/bin/env python3
"""
TTS服务工厂模块
用于创建和管理不同的TTS服务实例
"""

import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class TTSFactory:
    """TTS服务工厂类，用于创建不同的TTS服务实例"""
    
    @staticmethod
    def create_tts_service(service_type: str = 'auto') -> Any:
        """
        创建TTS服务实例
        
        参数:
            service_type: 服务类型，可选值：'auto', 'baidu', 'local'
                - 'auto': 自动选择可用的服务
                - 'baidu': 百度语音合成服务
                - 'local': 本地TTS服务
        
        返回:
            TTS服务实例
        """
        # 首先检查环境变量
        baidu_api_key = os.getenv('BAIDU_API_KEY')
        baidu_secret_key = os.getenv('BAIDU_SECRET_KEY')
        
        # 根据服务类型创建实例
        if service_type == 'auto':
            # 自动选择：优先使用百度服务，如果配置不可用则使用本地服务
            if baidu_api_key and baidu_secret_key and baidu_api_key != 'your_baidu_api_key_here':
                logger.info("使用百度语音合成服务")
                return TTSFactory.create_tts_service('baidu')
            else:
                logger.info("使用本地TTS服务")
                return TTSFactory.create_tts_service('local')
        
        elif service_type == 'baidu':
            # 使用百度语音合成服务
            try:
                from services.baidu_tts_service import BaiduTTSService
                service = BaiduTTSService()
                if service.is_configured:
                    return service
                else:
                    logger.warning("百度TTS服务配置不可用，尝试使用本地TTS服务")
                    return TTSFactory.create_tts_service('local')
            except ImportError as e:
                logger.error(f"导入百度TTS服务失败: {e}")
                return TTSFactory.create_tts_service('local')
        
        elif service_type == 'local':
            # 使用本地TTS服务
            try:
                from services.local_tts_service import LocalTTSService
                return LocalTTSService()
            except ImportError as e:
                logger.error(f"导入本地TTS服务失败: {e}")
                return None
        
        else:
            logger.error(f"未知的TTS服务类型: {service_type}")
            return None
    
    @staticmethod
    def get_available_services() -> Dict[str, bool]:
        """获取可用的TTS服务列表"""
        services = {
            'baidu': False,
            'local': False
        }
        
        # 检查百度服务
        try:
            from services.baidu_tts_service import BaiduTTSService
            baidu_service = BaiduTTSService()
            services['baidu'] = baidu_service.is_configured
        except ImportError:
            pass
        
        # 检查本地服务
        try:
            from services.local_tts_service import LocalTTSService
            local_service = LocalTTSService()
            services['local'] = local_service.is_configured
        except ImportError:
            pass
        
        return services
