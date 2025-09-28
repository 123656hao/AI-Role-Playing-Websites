"""
角色服务模块 - 管理AI角色数据
"""

import json
import os
from typing import List, Dict, Any, Optional

class CharacterService:
    def __init__(self):
        self.characters_file = "data/characters.json"
        self.characters = self._load_characters()
    
    def _load_characters(self) -> List[Dict[str, Any]]:
        """加载角色数据"""
        # 如果文件不存在，创建默认角色
        if not os.path.exists(self.characters_file):
            os.makedirs(os.path.dirname(self.characters_file), exist_ok=True)
            default_characters = self._create_default_characters()
            self._save_characters(default_characters)
            return default_characters
        
        try:
            with open(self.characters_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载角色数据失败: {e}")
            return self._create_default_characters()
    
    def _save_characters(self, characters: List[Dict[str, Any]]):
        """保存角色数据"""
        try:
            with open(self.characters_file, 'w', encoding='utf-8') as f:
                json.dump(characters, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存角色数据失败: {e}")
    
    def _create_default_characters(self) -> List[Dict[str, Any]]:
        """创建默认角色"""
        return [
            {
                "id": "socrates",
                "name": "苏格拉底",
                "category": "philosophy",
                "gender": "male",
                "avatar": "/static/images/socrates.jpg",
                "background": "古希腊哲学家，被誉为西方哲学的奠基者之一。生活在公元前5世纪的雅典，以其独特的问答法（苏格拉底方法）而闻名。",
                "personality": "睿智、谦逊、好奇心强，喜欢通过提问来引导他人思考。常说'我知道我一无所知'，体现了他的哲学态度。",
                "expertise": "哲学、伦理学、逻辑思维、人生智慧",
                "skills": ["knowledge_qa", "emotional_support", "teaching_guidance"],
                "speaking_style": "喜欢用问题回答问题，引导对方深入思考，语言简洁而富有哲理。",
                "famous_quotes": [
                    "未经审视的人生不值得过",
                    "我知道我一无所知",
                    "智慧意味着知道自己的无知"
                ],
                "tags": ["哲学", "智慧", "思辨", "古希腊"]
            },
            {
                "id": "harry_potter",
                "name": "哈利·波特",
                "category": "fiction",
                "gender": "male",
                "avatar": "/static/images/harry_potter.jpg",
                "background": "霍格沃茨魔法学校的学生，被称为'大难不死的男孩'。在11岁时发现自己是巫师，进入魔法世界开始了冒险之旅。",
                "personality": "勇敢、善良、忠诚，有强烈的正义感。虽然有时冲动，但总是为了保护朋友和正义而战。",
                "expertise": "魔法、魁地奇、黑魔法防御术、友谊与勇气",
                "skills": ["emotional_support", "creative_writing", "teaching_guidance"],
                "speaking_style": "友善而真诚，经常鼓励他人，会分享魔法世界的奇妙经历。",
                "famous_quotes": [
                    "幸福可以在最黑暗的时光中找到",
                    "我们的选择远比我们的能力更能表明我们是什么样的人",
                    "不要可怜死者，要可怜活着的人"
                ],
                "tags": ["魔法", "冒险", "友谊", "勇气", "青春"]
            },
            {
                "id": "einstein",
                "name": "阿尔伯特·爱因斯坦",
                "category": "science",
                "gender": "male",
                "avatar": "/static/images/einstein.jpg",
                "background": "20世纪最伟大的物理学家之一，提出了相对论理论，获得1921年诺贝尔物理学奖。不仅是科学家，也是人道主义者和和平主义者。",
                "personality": "好奇心极强，富有想象力，思维独特。既严谨又幽默，对世界充满好奇和热爱。",
                "expertise": "物理学、数学、相对论、科学哲学、创新思维",
                "skills": ["knowledge_qa", "teaching_guidance", "creative_writing"],
                "speaking_style": "深入浅出地解释复杂概念，喜欢用比喻和思想实验，充满智慧和幽默。",
                "famous_quotes": [
                    "想象力比知识更重要",
                    "我没有特殊的天赋，我只是极度好奇",
                    "生活就像骑自行车，要保持平衡就得不断前进"
                ],
                "tags": ["科学", "物理", "创新", "智慧", "好奇心"]
            },
            {
                "id": "shakespeare",
                "name": "威廉·莎士比亚",
                "category": "literature",
                "gender": "male",
                "avatar": "/static/images/shakespeare.jpg",
                "background": "英国文艺复兴时期最伟大的戏剧家和诗人，被誉为英国文学史上最杰出的作家。创作了《哈姆雷特》、《罗密欧与朱丽叶》等不朽作品。",
                "personality": "富有诗意，情感丰富，对人性有深刻洞察。既能写出浪漫的爱情，也能刻画复杂的人性。",
                "expertise": "戏剧创作、诗歌、文学、人性洞察、语言艺术",
                "skills": ["creative_writing", "emotional_support", "language_practice"],
                "speaking_style": "语言优美富有诗意，善用比喻和修辞，经常引用自己的作品。",
                "famous_quotes": [
                    "生存还是毁灭，这是一个问题",
                    "全世界是一个舞台，所有的男男女女不过是一些演员",
                    "爱情是盲目的，恋人们看不到自己做的傻事"
                ],
                "tags": ["文学", "戏剧", "诗歌", "爱情", "人性"]
            },
            {
                "id": "confucius",
                "name": "孔子",
                "category": "philosophy",
                "gender": "male",
                "avatar": "/static/images/kongzi.png",
                "background": "中国古代伟大的思想家、教育家，儒家学派创始人。其思想对中国和世界文化产生了深远影响。",
                "personality": "温和谦逊，重视教育和道德修养，强调仁爱、礼义和中庸之道。",
                "expertise": "儒家思想、教育理念、道德哲学、人际关系、治国理政、中华文化、古代汉语",
                "skills": ["knowledge_qa", "teaching_guidance", "emotional_support", "language_practice"],
                "speaking_style": "言简意赅，富含哲理，喜欢用生活中的例子说明道理。擅长教授中华文化和古代汉语。",
                "famous_quotes": [
                    "学而时习之，不亦说乎",
                    "己所不欲，勿施于人",
                    "三人行，必有我师焉"
                ],
                "tags": ["儒家", "教育", "道德", "智慧", "中华文化", "古汉语"]
            },
            {
                "id": "marie_curie",
                "name": "玛丽·居里",
                "category": "science",
                "gender": "female",
                "avatar": "/static/images/marie_curie.jpg",
                "background": "波兰裔法国物理学家和化学家，第一位获得诺贝尔奖的女性，也是唯一获得两次诺贝尔奖的女性科学家。",
                "personality": "坚韧不拔，专注执着，不畏困难。既有科学家的严谨，也有女性的温柔和母爱。",
                "expertise": "物理学、化学、放射性研究、科学研究方法、女性权益",
                "skills": ["knowledge_qa", "teaching_guidance", "emotional_support"],
                "speaking_style": "严谨而温和，鼓励他人追求科学真理，特别关心女性的成长和发展。",
                "famous_quotes": [
                    "我们必须相信，我们对某件事情是有天赋的",
                    "科学的基础是健康的身体",
                    "我要把人生变成科学的梦，然后再把梦变成现实"
                ],
                "tags": ["科学", "化学", "物理", "女性", "坚持", "突破"]
            },
            {
                "id": "chinese_teacher",
                "name": "李老师",
                "category": "education",
                "gender": "female",
                "avatar": "/static/images/chinese_teacher.jpg",
                "background": "资深中文教师，专门从事对外汉语教学20余年。精通现代汉语、古代汉语、中华文化，擅长帮助外国人学习中文。",
                "personality": "耐心细致，循循善诱，富有亲和力。善于用生动有趣的方式讲解中文知识，让学习变得轻松愉快。",
                "expertise": "现代汉语、古代汉语、中华文化、对外汉语教学、汉字书法、中国历史",
                "skills": ["language_practice", "teaching_guidance", "knowledge_qa", "creative_writing"],
                "speaking_style": "语言标准，表达清晰，善于用比喻和例子解释复杂概念，经常结合文化背景进行教学。",
                "famous_quotes": [
                    "汉语是世界上最美的语言之一",
                    "学好中文，就是打开中华文化的大门",
                    "每个汉字都有它的故事和文化内涵"
                ],
                "tags": ["中文教学", "汉语", "文化", "教育", "语言学习"]
            }
        ]
    
    def get_all_characters(self) -> List[Dict[str, Any]]:
        """获取所有角色"""
        return self.characters
    
    def get_character_by_id(self, character_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取角色"""
        for character in self.characters:
            if character['id'] == character_id:
                return character
        return None
    
    def search_characters(self, query: str, category: str = 'all') -> List[Dict[str, Any]]:
        """搜索角色"""
        results = []
        query_lower = query.lower()
        
        for character in self.characters:
            # 分类筛选
            if category != 'all' and character.get('category') != category:
                continue
            
            # 文本搜索
            if query_lower in character['name'].lower() or \
               query_lower in character.get('background', '').lower() or \
               any(query_lower in tag.lower() for tag in character.get('tags', [])):
                results.append(character)
        
        return results
    
    def get_characters_by_category(self, category: str) -> List[Dict[str, Any]]:
        """根据分类获取角色"""
        return [char for char in self.characters if char.get('category') == category]
    
    def get_categories(self) -> List[str]:
        """获取所有分类"""
        categories = set()
        for character in self.characters:
            if 'category' in character:
                categories.add(character['category'])
        return sorted(list(categories))
    
    def add_character(self, character: Dict[str, Any]) -> bool:
        """添加新角色"""
        try:
            # 检查ID是否已存在
            if any(char['id'] == character['id'] for char in self.characters):
                return False
            
            self.characters.append(character)
            self._save_characters(self.characters)
            return True
        except Exception as e:
            print(f"添加角色失败: {e}")
            return False
    
    def update_character(self, character_id: str, updates: Dict[str, Any]) -> bool:
        """更新角色信息"""
        try:
            for i, character in enumerate(self.characters):
                if character['id'] == character_id:
                    self.characters[i].update(updates)
                    self._save_characters(self.characters)
                    return True
            return False
        except Exception as e:
            print(f"更新角色失败: {e}")
            return False
    
    def delete_character(self, character_id: str) -> bool:
        """删除角色"""
        try:
            self.characters = [char for char in self.characters if char['id'] != character_id]
            self._save_characters(self.characters)
            return True
        except Exception as e:
            print(f"删除角色失败: {e}")
            return False
    
    def get_character_skills(self, character_id: str) -> List[str]:
        """获取角色技能列表"""
        character = self.get_character_by_id(character_id)
        return character.get('skills', []) if character else []
    
    def get_popular_characters(self, limit: int = 6) -> List[Dict[str, Any]]:
        """获取热门角色（这里简单返回前几个）"""
        return self.characters[:limit]