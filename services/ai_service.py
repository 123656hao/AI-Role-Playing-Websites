"""
AI服务模块 - 处理角色扮演对话和技能执行
"""

from openai import OpenAI
import json
import os
from typing import Dict, Any, List
from datetime import datetime

class AIRoleplayService:
    def __init__(self):
        # 从环境变量获取API配置
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.api_base = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4')
        
        if not self.api_key:
            raise ValueError("请设置OPENAI_API_KEY环境变量")
        
        # 初始化OpenAI客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base
        )
        
        print(f"✅ AI服务初始化完成")
        print(f"   API端点: {self.api_base}")
        print(f"   使用模型: {self.model}")
        
        # 存储会话历史
        self.chat_histories = {}
        
    def generate_welcome_message(self, character: Dict[str, Any]) -> str:
        """生成角色欢迎消息"""
        prompt = f"""
你现在要扮演{character['name']}。
角色背景：{character['background']}
性格特点：{character['personality']}
专业领域：{character['expertise']}

请以{character['name']}的身份，用第一人称生成一段简短的欢迎语，体现角色的性格和特点。
欢迎语应该：
1. 符合角色身份和时代背景
2. 体现角色的说话风格
3. 简洁有趣，不超过100字
4. 表达愿意与用户交流的意愿
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "请生成欢迎语"}
                ],
                max_tokens=200,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ 欢迎消息生成失败: {e}")
            return f"你好！我是{character['name']}，很高兴与你交流！"
    
    def generate_response(self, character: Dict[str, Any], user_message: str, session_id: str) -> str:
        """生成AI角色回复"""
        # 获取或初始化会话历史
        if session_id not in self.chat_histories:
            self.chat_histories[session_id] = []
        
        history = self.chat_histories[session_id]
        
        # 构建系统提示
        system_prompt = f"""
你现在要完全扮演{character['name']}，请严格按照以下设定进行对话：

角色信息：
- 姓名：{character['name']}
- 背景：{character['background']}
- 性格：{character['personality']}
- 专业领域：{character['expertise']}
- 技能：{', '.join(character.get('skills', []))}

扮演要求：
1. 完全以{character['name']}的身份回答，使用第一人称
2. 回答要符合角色的时代背景、知识水平和说话风格
3. 体现角色的性格特点和专业知识
4. 如果用户问题涉及你的专业领域，要展现专业性
5. 保持角色一致性，不要跳出角色设定
6. 回答要自然、有趣，避免过于正式
7. 适当使用角色相关的典型表达方式

注意：你就是{character['name']}，不是AI助手，不要提及你是AI或者模型。
"""
        
        # 构建对话历史
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加历史对话（最近10轮）
        for msg in history[-10:]:
            messages.append({"role": "user", "content": msg["user"]})
            messages.append({"role": "assistant", "content": msg["assistant"]})
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.8,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # 保存对话历史
            history.append({
                "user": user_message,
                "assistant": ai_response,
                "timestamp": datetime.now().isoformat()
            })
            
            return ai_response
            
        except Exception as e:
            print(f"⚠️ AI回复生成失败: {e}")
            return f"抱歉，我现在有些困惑，能否重新说一遍？"
    
    def execute_skill(self, character: Dict[str, Any], skill_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行角色技能"""
        skills_map = {
            'knowledge_qa': self._knowledge_qa_skill,
            'emotional_support': self._emotional_support_skill,
            'teaching_guidance': self._teaching_guidance_skill,
            'creative_writing': self._creative_writing_skill,
            'language_practice': self._language_practice_skill
        }
        
        if skill_name not in skills_map:
            return {"error": "未知技能"}
        
        try:
            return skills_map[skill_name](character, data)
        except Exception as e:
            return {"error": f"技能执行失败: {str(e)}"}
    
    def _knowledge_qa_skill(self, character: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """知识问答技能"""
        question = data.get('question', '')
        
        prompt = f"""
作为{character['name']}，请回答以下问题：{question}

要求：
1. 基于你的专业知识和历史背景回答
2. 如果问题超出你的知识范围，诚实说明
3. 回答要准确、详细但易懂
4. 体现你的专业权威性
5. 可以结合你的时代背景和个人经历
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"你是{character['name']}，专业领域：{character['expertise']}"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.7
            )
            
            return {
                "skill": "knowledge_qa",
                "question": question,
                "answer": response.choices[0].message.content.strip(),
                "character": character['name']
            }
        except Exception as e:
            return {"error": f"知识问答失败: {str(e)}"}
    
    def _emotional_support_skill(self, character: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """情感陪伴技能"""
        user_emotion = data.get('emotion', '')
        user_message = data.get('message', '')
        
        prompt = f"""
用户现在的情绪状态：{user_emotion}
用户说：{user_message}

作为{character['name']}，请提供情感支持和安慰。要求：
1. 体现同理心和理解
2. 结合你的人生智慧和经历
3. 给出积极正面的建议
4. 语气温暖、真诚
5. 避免说教，更多是陪伴和理解
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"你是{character['name']}，以温暖理解的方式提供情感支持"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.8
            )
            
            return {
                "skill": "emotional_support",
                "support_message": response.choices[0].message.content.strip(),
                "character": character['name']
            }
        except Exception as e:
            return {"error": f"情感支持失败: {str(e)}"}
    
    def _teaching_guidance_skill(self, character: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """教学指导技能"""
        topic = data.get('topic', '')
        level = data.get('level', 'beginner')  # beginner, intermediate, advanced
        
        prompt = f"""
请以{character['name']}的身份，教授关于"{topic}"的知识。
学习者水平：{level}

要求：
1. 根据学习者水平调整教学内容和方式
2. 结合你的专业背景和教学风格
3. 提供清晰的解释和实例
4. 循序渐进，易于理解
5. 可以提出思考问题或练习建议
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"你是{character['name']}，专业教师，擅长{character['expertise']}"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.7
            )
            
            return {
                "skill": "teaching_guidance",
                "topic": topic,
                "level": level,
                "lesson": response.choices[0].message.content.strip(),
                "character": character['name']
            }
        except Exception as e:
            return {"error": f"教学指导失败: {str(e)}"}
    
    def _creative_writing_skill(self, character: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """创作协助技能"""
        writing_type = data.get('type', 'story')  # story, poem, essay, dialogue
        theme = data.get('theme', '')
        style = data.get('style', '')
        
        prompt = f"""
请以{character['name']}的身份，协助创作一个{writing_type}。
主题：{theme}
风格要求：{style}

要求：
1. 体现你的文学素养和创作风格
2. 结合你的时代背景和文化特色
3. 内容要有创意和深度
4. 符合指定的文体和风格
5. 可以提供创作建议和技巧
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"你是{character['name']}，具有深厚的文学造诣"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=700,
                temperature=0.9
            )
            
            return {
                "skill": "creative_writing",
                "type": writing_type,
                "theme": theme,
                "creation": response.choices[0].message.content.strip(),
                "character": character['name']
            }
        except Exception as e:
            return {"error": f"创作协助失败: {str(e)}"}
    
    def _language_practice_skill(self, character: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """语言练习技能"""
        target_language = data.get('language', 'Chinese')
        practice_type = data.get('type', 'conversation')  # conversation, grammar, vocabulary, pronunciation, writing
        topic = data.get('topic', 'daily life')
        
        # 根据目标语言调整提示语言
        if target_language == 'Chinese':
            system_content = f"你是{character['name']}，中文语言专家，帮助用户学习和提高中文水平"
            prompt = f"""
请以{character['name']}的身份，帮助用户练习中文。
练习类型：{practice_type}
话题：{topic}

要求：
1. 主要使用中文进行交流，适当使用其他语言解释
2. 根据练习类型提供相应的帮助：
   - 对话练习：进行自然的中文对话
   - 语法练习：讲解中文语法规则和用法
   - 词汇练习：教授新词汇和用法
   - 发音练习：指导声调和发音技巧
   - 写作练习：指导中文写作技巧
3. 纠正语言错误并给出详细建议
4. 提供文化背景知识
5. 鼓励用户多说多练，保持耐心友善
"""
        else:
            system_content = f"你是{character['name']}，多语言专家，帮助用户学习{target_language}"
            prompt = f"""
请以{character['name']}的身份，帮助用户练习{target_language}。
练习类型：{practice_type}
话题：{topic}

要求：
1. 主要使用{target_language}进行交流，适当使用中文解释
2. 根据练习类型提供相应的帮助：
   - 对话练习：进行自然的{target_language}对话
   - 语法练习：讲解语法规则和用法
   - 词汇练习：教授新词汇和用法
   - 发音练习：指导发音技巧
   - 写作练习：指导写作技巧
3. 纠正语言错误并给出建议
4. 提供文化背景知识
5. 鼓励用户多说多练，保持耐心友善
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return {
                "skill": "language_practice",
                "language": target_language,
                "type": practice_type,
                "topic": topic,
                "practice_content": response.choices[0].message.content.strip(),
                "character": character['name']
            }
        except Exception as e:
            return {"error": f"语言练习失败: {str(e)}"}