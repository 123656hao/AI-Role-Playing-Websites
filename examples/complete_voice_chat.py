"""
完整的语音聊天示例
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.voice_chat_client import VoiceChatClient


class VoiceChatDemo:
    def __init__(self):
        self.client = None
        self.running = False
    
    def on_message_received(self, message_data):
        """处理接收到的文本消息"""
        text = message_data.get("text", "")
        print(f"AI回复: {text}")
    
    def on_audio_received(self, audio_data):
        """处理接收到的音频数据"""
        print("收到音频数据，正在播放...")
        # 这里可以解码并播放音频
        if self.client:
            # 假设audio_data是十六进制字符串，需要转换为bytes
            try:
                audio_bytes = bytes.fromhex(audio_data)
                self.client.play_audio(audio_bytes)
            except Exception as e:
                print(f"音频播放错误: {e}")
    
    def on_error(self, error_message):
        """处理错误"""
        print(f"错误: {error_message}")
    
    async def start_chat(self, character_id: str, voice_type: str = "female"):
        """开始语音聊天"""
        try:
            # 创建客户端
            self.client = VoiceChatClient(character_id, voice_type)
            
            # 设置回调函数
            self.client.set_callbacks(
                on_message_received=self.on_message_received,
                on_audio_received=self.on_audio_received,
                on_error=self.on_error
            )
            
            # 连接到服务器
            await self.client.connect()
            
            # 启动音频输入输出
            self.client.start_audio_input()
            self.client.start_audio_output()
            
            self.running = True
            print(f"\n开始与 {character_id} 聊天!")
            print("输入 'quit' 退出，输入 'voice' 切换到语音模式")
            print("=" * 50)
            
            # 主循环
            while self.running:
                try:
                    # 获取用户输入
                    user_input = input("\n你: ")
                    
                    if user_input.lower() == 'quit':
                        break
                    elif user_input.lower() == 'voice':
                        print("语音模式已启动，请开始说话...")
                        # 在实际应用中，这里会启动语音识别
                        await asyncio.sleep(5)  # 模拟语音输入时间
                        continue
                    elif user_input.strip():
                        # 发送文本消息
                        await self.client.send_text(user_input)
                    
                    # 短暂等待，让异步任务有机会执行
                    await asyncio.sleep(0.1)
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"输入处理错误: {e}")
            
        except Exception as e:
            print(f"聊天启动失败: {e}")
        finally:
            # 清理资源
            if self.client:
                await self.client.disconnect()
            self.running = False
    
    async def demo_multiple_characters(self):
        """演示多个角色的语音配置"""
        characters = [
            ("socrates", "male", "与苏格拉底对话"),
            ("einstein", "male", "与爱因斯坦对话"),
            ("marie_curie", "female", "与居里夫人对话"),
            ("chinese_teacher", "female", "与李老师学中文")
        ]
        
        print("可用角色演示:")
        for i, (char_id, voice, desc) in enumerate(characters, 1):
            print(f"{i}. {desc}")
        
        try:
            choice = int(input("\n请选择角色 (1-4): ")) - 1
            if 0 <= choice < len(characters):
                char_id, voice_type, desc = characters[choice]
                print(f"\n开始 {desc}")
                await self.start_chat(char_id, voice_type)
            else:
                print("无效选择")
        except ValueError:
            print("请输入有效数字")


async def main():
    demo = VoiceChatDemo()
    
    print("语音聊天演示程序")
    print("=" * 30)
    
    # 显示菜单
    print("1. 演示多个角色")
    print("2. 直接与苏格拉底对话")
    print("3. 直接与李老师对话")
    
    try:
        choice = input("\n请选择 (1-3): ")
        
        if choice == "1":
            await demo.demo_multiple_characters()
        elif choice == "2":
            await demo.start_chat("socrates", "male")
        elif choice == "3":
            await demo.start_chat("chinese_teacher", "female")
        else:
            print("无效选择")
            
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        print(f"程序错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())