#!/usr/bin/env python3
"""
端口管理工具
检查和管理WebSocket服务器端口
"""

import socket
import subprocess
import sys
import logging
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

class PortManager:
    """端口管理器"""
    
    @staticmethod
    def is_port_available(host: str, port: int) -> bool:
        """检查端口是否可用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                return result != 0  # 0表示连接成功，即端口被占用
        except Exception as e:
            logger.error(f"检查端口 {host}:{port} 失败: {e}")
            return False
    
    @staticmethod
    def find_available_port(host: str, start_port: int, end_port: int = None) -> Optional[int]:
        """查找可用端口"""
        if end_port is None:
            end_port = start_port + 100
        
        for port in range(start_port, end_port + 1):
            if PortManager.is_port_available(host, port):
                return port
        
        return None
    
    @staticmethod
    def get_port_info(port: int) -> dict:
        """获取端口占用信息"""
        info = {
            'port': port,
            'available': False,
            'process_info': None,
            'error': None
        }
        
        try:
            # 检查端口是否可用
            info['available'] = PortManager.is_port_available('localhost', port)
            
            if not info['available']:
                # 获取占用进程信息
                if sys.platform == 'win32':
                    info['process_info'] = PortManager._get_windows_port_info(port)
                else:
                    info['process_info'] = PortManager._get_unix_port_info(port)
                    
        except Exception as e:
            info['error'] = str(e)
        
        return info
    
    @staticmethod
    def _get_windows_port_info(port: int) -> Optional[str]:
        """获取Windows系统端口占用信息"""
        try:
            # 使用netstat命令查找端口占用
            result = subprocess.run(
                ['netstat', '-ano', '-p', 'TCP'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if f':{port}' in line and 'LISTENING' in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            # 获取进程名称
                            try:
                                tasklist_result = subprocess.run(
                                    ['tasklist', '/FI', f'PID eq {pid}', '/FO', 'CSV'],
                                    capture_output=True,
                                    text=True,
                                    timeout=5
                                )
                                if tasklist_result.returncode == 0:
                                    lines = tasklist_result.stdout.split('\n')
                                    if len(lines) > 1:
                                        process_name = lines[1].split(',')[0].strip('"')
                                        return f"PID: {pid}, 进程: {process_name}"
                            except Exception:
                                pass
                            return f"PID: {pid}"
                            
        except Exception as e:
            logger.error(f"获取Windows端口信息失败: {e}")
        
        return None
    
    @staticmethod
    def _get_unix_port_info(port: int) -> Optional[str]:
        """获取Unix系统端口占用信息"""
        try:
            # 使用lsof命令查找端口占用
            result = subprocess.run(
                ['lsof', '-i', f':{port}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout:
                lines = result.stdout.split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) >= 2:
                        return f"进程: {parts[0]}, PID: {parts[1]}"
                        
        except Exception as e:
            logger.error(f"获取Unix端口信息失败: {e}")
        
        return None
    
    @staticmethod
    def kill_process_on_port(port: int) -> bool:
        """终止占用端口的进程"""
        try:
            if sys.platform == 'win32':
                return PortManager._kill_windows_process_on_port(port)
            else:
                return PortManager._kill_unix_process_on_port(port)
        except Exception as e:
            logger.error(f"终止端口 {port} 上的进程失败: {e}")
            return False
    
    @staticmethod
    def _kill_windows_process_on_port(port: int) -> bool:
        """终止Windows系统上占用端口的进程"""
        try:
            # 查找PID
            result = subprocess.run(
                ['netstat', '-ano', '-p', 'TCP'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if f':{port}' in line and 'LISTENING' in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            # 终止进程
                            kill_result = subprocess.run(
                                ['taskkill', '/F', '/PID', pid],
                                capture_output=True,
                                text=True,
                                timeout=10
                            )
                            return kill_result.returncode == 0
                            
        except Exception as e:
            logger.error(f"终止Windows进程失败: {e}")
        
        return False
    
    @staticmethod
    def _kill_unix_process_on_port(port: int) -> bool:
        """终止Unix系统上占用端口的进程"""
        try:
            # 查找PID
            result = subprocess.run(
                ['lsof', '-t', '-i', f':{port}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout:
                pid = result.stdout.strip()
                # 终止进程
                kill_result = subprocess.run(
                    ['kill', '-9', pid],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                return kill_result.returncode == 0
                
        except Exception as e:
            logger.error(f"终止Unix进程失败: {e}")
        
        return False
    
    @staticmethod
    def get_recommended_ports(base_ports: List[int]) -> List[Tuple[int, int]]:
        """获取推荐的可用端口"""
        recommendations = []
        
        for base_port in base_ports:
            available_port = PortManager.find_available_port('localhost', base_port, base_port + 50)
            if available_port:
                recommendations.append((base_port, available_port))
            else:
                recommendations.append((base_port, None))
        
        return recommendations