#!/usr/bin/env python3
"""
语音服务工厂模块
用于创建和管理不同的语音识别服务实例
"""

import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class VoiceFactory:
    """语音识别服务工厂类，用于创建不同的语音识别服务实例"""
    
    @staticmethod
    def create_voice_service(service_type: str = 'auto') -> Any:
        """
        创建语音识别服务实例
        
        参数:
            service_type: 服务类型，可选值：'auto', 'baidu', 'local'
                - 'auto': 自动选择可用的服务
                - 'baidu': 百度语音识别服务
                - 'local': 本地语音识别服务
        
        返回:
            语音识别服务实例
        """
        # 首先检查环境变量
        baidu_api_key = os.getenv('BAIDU_API_KEY')
        baidu_secret_key = os.getenv('BAIDU_SECRET_KEY')
        
        # 根据服务类型创建实例
        if service_type == 'auto':
            # 自动选择：优先使用百度服务，如果配置不可用则使用本地服务
            if baidu_api_key and baidu_secret_key and baidu_api_key != 'your_baidu_api_key_here':
                logger.info("使用百度语音识别服务")
                return VoiceFactory.create_voice_service('baidu')
            else:
                logger.info("使用本地语音识别服务")
                return VoiceFactory.create_voice_service('local')
        
        elif service_type == 'baidu':
            # 使用百度语音识别服务
            try:
                from services.baidu_voice_service import BaiduVoiceService
                service = BaiduVoiceService()
                if service.is_configured:
                    return service
                else:
                    logger.warning("百度语音识别服务配置不可用，尝试使用本地语音识别服务")
                    return VoiceFactory.create_voice_service('local')
            except ImportError as e:
                logger.error(f"导入百度语音识别服务失败: {e}")
                return VoiceFactory.create_voice_service('local')
        
        elif service_type == 'local':
            # 使用本地语音识别服务
            try:
                from services.local_stt_service import LocalSTTService
                return LocalSTTService()
            except ImportError as e:
                logger.error(f"导入本地语音识别服务失败: {e}")
                return None
        
        else:
            logger.error(f"未知的语音识别服务类型: {service_type}")
            return None
    
    @staticmethod
    def get_available_services() -> Dict[str, bool]:
        """获取可用的语音识别服务列表"""
        services = {
            'baidu': False,
            'local': False
        }
        
        # 检查百度服务
        try:
            from services.baidu_voice_service import BaiduVoiceService
            baidu_service = BaiduVoiceService()
            services['baidu'] = baidu_service.is_configured
        except ImportError:
            pass
        
        # 检查本地服务
        try:
            from services.local_stt_service import LocalSTTService
            local_service = LocalSTTService()
            services['local'] = local_service.is_configured
        except ImportError:
            pass
        
        return services
