"""
AI场景生成器 - 语义关系解析模块
解析输入指令中的成对关系和组间关系，利用LTC机制进行语义映射

作者: AI Team
版本: 1.0
"""

import re
from typing import List, Dict, Tuple, Optional


class SemanticRelationParser:
    """
    语义关系解析器
    提取空间关系、成对关系、组间关系
    """
    
    def __init__(self):
        """初始化关系解析器"""
        # 成对关系关键词（中英文）
        self.pair_relation_keywords = {
            'next_to': ['旁边', '附近', '邻近', 'next to', 'beside', 'near', 'adjacent'],
            'around': ['围绕', '环绕', 'around', 'surrounding', 'encircling'],
            'behind': ['后面', '后方', 'behind', 'back'],
            'in_front_of': ['前面', '前方', 'in front of', 'before'],
            'on': ['上面', '上', 'on', 'above', 'over'],
            'under': ['下面', '下', 'under', 'beneath', 'below'],
            'between': ['之间', '中间', 'between', 'among'],
            'inside': ['里面', '内部', 'inside', 'within', 'in'],
            'outside': ['外面', '外部', 'outside', 'out'],
            'along': ['沿着', '顺着', 'along', 'following'],
            'across': ['对面', 'across', 'opposite'],
            'towards': ['朝向', 'towards', 'facing']
        }
        
        # 组间关系关键词
        self.group_relation_keywords = {
            'circle_around': ['一圈', '围绕', '环绕', 'circle around', 'surround', 'encircle'],
            'line_along': ['一排', '一行', '沿着', 'line along', 'row of'],
            'cluster_near': ['聚集', '簇拥', 'cluster near', 'group around'],
            'scatter_around': ['散布', '分散', 'scatter around', 'distribute'],
            'symmetrical': ['对称', '对称的', 'symmetrical', 'balanced'],
            'random': ['随机', '随意', 'random', 'irregular']
        }
        
        # 数量修饰词
        self.quantity_modifiers = {
            'many': ['许多', '很多', '大量', 'many', 'lots', 'numerous'],
            'few': ['几个', '少量', 'few', 'several', 'a couple'],
            'one': ['一个', '一块', '一棵', 'one', 'a', 'an'],
            'some': ['一些', 'some', 'a few']
        }
        
        print("[OK] Semantic relation parser initialized")
    
    def parse_relations(self, text: str, nlp_objects: List[str]) -> Dict:
        """
        解析文本中的语义关系
        
        Args:
            text: 输入文本
            nlp_objects: NLP识别到的对象列表
        
        Returns:
            dict: 关系解析结果
        """
        print(f"[PARSING] Extracting semantic relations from: {text[:50]}...")
        
        text_lower = text.lower()
        
        # 1. 提取成对关系
        pair_relations = self._extract_pair_relations(text_lower, nlp_objects)
        
        # 2. 提取组间关系
        group_relations = self._extract_group_relations(text_lower, nlp_objects)
        
        # 3. 构建关系图
        relation_graph = self._build_relation_graph(pair_relations, group_relations, nlp_objects)
        
        result = {
            'pair_relations': pair_relations,
            'group_relations': group_relations,
            'relation_graph': relation_graph,
            'has_spatial_constraints': len(pair_relations) > 0 or len(group_relations) > 0
        }
        
        print(f"[OK] Extracted {len(pair_relations)} pair relations, {len(group_relations)} group relations")
        
        return result
    
    def _extract_pair_relations(self, text_lower: str, objects: List[str]) -> List[Dict]:
        """提取成对关系"""
        relations = []
        
        # 模式1: "A在B旁边" / "A next to B"
        patterns = [
            r'(\w+)\s*(?:在|is|are)\s*(\w+)\s*(旁边|附近|next to|beside|near)',
            r'(\w+)\s*(旁边|附近|next to|beside|near)\s*(\w+)',
            r'(\w+)\s*(?:和|and)\s*(\w+)\s*(?:一起|together)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                obj1 = match.group(1).strip()
                obj2 = match.group(2).strip() if len(match.groups()) >= 2 else None
                relation_type = match.group(3).strip() if len(match.groups()) >= 3 else 'near'
                
                # 映射到标准关系类型
                relation_type = self._map_relation_type(relation_type)
                
                # 检查对象是否在识别列表中
                obj1_type = self._match_object_type(obj1, objects)
                obj2_type = self._match_object_type(obj2, objects) if obj2 else None
                
                if obj1_type and obj2_type:
                    relations.append({
                        'type': relation_type,
                        'subject': obj1_type,
                        'object': obj2_type,
                        'distance': self._estimate_relation_distance(relation_type),
                        'confidence': 0.8
                    })
        
        # 模式2: 使用关键词直接匹配
        for relation_type, keywords in self.pair_relation_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # 尝试找到关系涉及的对象
                    context = self._extract_context(text_lower, keyword)
                    if context:
                        obj1, obj2 = context
                        obj1_type = self._match_object_type(obj1, objects)
                        obj2_type = self._match_object_type(obj2, objects)
                        
                        if obj1_type and obj2_type:
                            relations.append({
                                'type': relation_type,
                                'subject': obj1_type,
                                'object': obj2_type,
                                'distance': self._estimate_relation_distance(relation_type),
                                'confidence': 0.7
                            })
        
        return relations
    
    def _extract_group_relations(self, text_lower: str, objects: List[str]) -> List[Dict]:
        """提取组间关系"""
        relations = []
        
        # 模式: "一圈树围绕石头" / "a circle of trees around stone"
        patterns = [
            r'(一圈|一排|一群|many|several)\s*(\w+)\s*(围绕|环绕|around|surround)\s*(\w+)',
            r'(\w+)\s*(围绕|环绕|around|surround)\s*(\w+)',
            r'(对称|symmetrical)\s*(?:的|的)?\s*(\w+)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                quantity = match.group(1) if len(match.groups()) >= 1 else None
                group_obj = match.group(2) if len(match.groups()) >= 2 else None
                relation_type = match.group(3) if len(match.groups()) >= 3 else None
                center_obj = match.group(4) if len(match.groups()) >= 4 else None
                
                # 如果没有明确的关系类型，尝试推断
                if not relation_type:
                    if quantity and '一圈' in quantity or 'circle' in str(quantity).lower():
                        relation_type = 'circle_around'
                    elif quantity and '一排' in quantity or 'line' in str(quantity).lower():
                        relation_type = 'line_along'
                    else:
                        relation_type = 'cluster_near'
                
                # 映射到标准关系类型
                relation_type = self._map_group_relation_type(relation_type)
                
                # 匹配对象类型
                group_obj_type = self._match_object_type(group_obj, objects) if group_obj else None
                center_obj_type = self._match_object_type(center_obj, objects) if center_obj else None
                
                if group_obj_type:
                    relations.append({
                        'type': relation_type,
                        'group_type': group_obj_type,
                        'center_type': center_obj_type,
                        'quantity': self._parse_quantity(quantity),
                        'radius': self._estimate_group_radius(relation_type),
                        'confidence': 0.75
                    })
        
        # 直接关键词匹配
        for relation_type, keywords in self.group_relation_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # 提取上下文
                    context = self._extract_group_context(text_lower, keyword)
                    if context:
                        group_obj, center_obj = context
                        group_obj_type = self._match_object_type(group_obj, objects)
                        center_obj_type = self._match_object_type(center_obj, objects)
                        
                        if group_obj_type:
                            relations.append({
                                'type': relation_type,
                                'group_type': group_obj_type,
                                'center_type': center_obj_type,
                                'radius': self._estimate_group_radius(relation_type),
                                'confidence': 0.7
                            })
        
        return relations
    
    def _map_relation_type(self, relation_str: str) -> str:
        """映射关系字符串到标准类型"""
        relation_str_lower = relation_str.lower()
        
        for std_type, keywords in self.pair_relation_keywords.items():
            if any(kw in relation_str_lower for kw in keywords):
                return std_type
        
        return 'next_to'  # 默认
    
    def _map_group_relation_type(self, relation_str: str) -> str:
        """映射组关系字符串到标准类型"""
        relation_str_lower = str(relation_str).lower()
        
        for std_type, keywords in self.group_relation_keywords.items():
            if any(kw in relation_str_lower for kw in keywords):
                return std_type
        
        return 'cluster_near'  # 默认
    
    def _match_object_type(self, obj_str: str, objects: List[str]) -> Optional[str]:
        """匹配对象字符串到对象类型"""
        if not obj_str:
            return None
        
        obj_str_lower = obj_str.lower()
        
        # 直接匹配
        for obj_type in objects:
            if obj_type.lower() == obj_str_lower:
                return obj_type
        
        # 部分匹配（支持中文）
        obj_keywords = {
            'tree': ['树', 'tree', '树木'],
            'flower': ['花', 'flower', '花朵'],
            'stone': ['石头', 'stone', '岩石', 'rock'],
            'grass': ['草', 'grass', '草地'],
            'water': ['水', 'water', '水体'],
            'path': ['路', 'path', '道路'],
            'building': ['建筑', 'building', '房子'],
            'bush': ['灌木', 'bush', '树丛']
        }
        
        for obj_type, keywords in obj_keywords.items():
            if any(kw in obj_str_lower for kw in keywords):
                if obj_type in objects:
                    return obj_type
        
        return None
    
    def _extract_context(self, text: str, keyword: str) -> Optional[Tuple[str, str]]:
        """提取关键词上下文中的对象"""
        # 简化实现：在关键词前后查找对象
        keyword_pos = text.find(keyword)
        if keyword_pos == -1:
            return None
        
        # 提取前后各20个字符
        context_before = text[max(0, keyword_pos - 20):keyword_pos]
        context_after = text[keyword_pos + len(keyword):keyword_pos + len(keyword) + 20]
        
        # 尝试提取对象（简化）
        words_before = context_before.split()
        words_after = context_after.split()
        
        obj1 = words_before[-1] if words_before else None
        obj2 = words_after[0] if words_after else None
        
        return (obj1, obj2) if obj1 and obj2 else None
    
    def _extract_group_context(self, text: str, keyword: str) -> Optional[Tuple[str, str]]:
        """提取组关系上下文"""
        keyword_pos = text.find(keyword)
        if keyword_pos == -1:
            return None
        
        context = text[max(0, keyword_pos - 30):keyword_pos + len(keyword) + 30]
        words = context.split()
        
        # 尝试找到组对象和中心对象
        group_obj = None
        center_obj = None
        
        for i, word in enumerate(words):
            if word.lower() in ['tree', '花', 'flower', 'stone', '石头']:
                if not group_obj:
                    group_obj = word
                elif not center_obj:
                    center_obj = word
        
        return (group_obj, center_obj) if group_obj else None
    
    def _estimate_relation_distance(self, relation_type: str) -> float:
        """估计关系距离"""
        distance_map = {
            'next_to': 3.0,
            'around': 5.0,
            'behind': 4.0,
            'in_front_of': 4.0,
            'on': 0.5,
            'under': 0.5,
            'between': 2.0,
            'inside': 1.0,
            'outside': 6.0,
            'along': 2.0,
            'across': 8.0,
            'towards': 5.0
        }
        return distance_map.get(relation_type, 3.0)
    
    def _estimate_group_radius(self, relation_type: str) -> float:
        """估计组关系半径"""
        radius_map = {
            'circle_around': 5.0,
            'line_along': 10.0,
            'cluster_near': 4.0,
            'scatter_around': 8.0,
            'symmetrical': 6.0,
            'random': 7.0
        }
        return radius_map.get(relation_type, 5.0)
    
    def _parse_quantity(self, quantity_str: Optional[str]) -> int:
        """解析数量"""
        if not quantity_str:
            return 5  # 默认
        
        quantity_str_lower = str(quantity_str).lower()
        
        if any(kw in quantity_str_lower for kw in ['many', '许多', '很多', '大量']):
            return 10
        elif any(kw in quantity_str_lower for kw in ['few', '几个', '少量']):
            return 3
        elif any(kw in quantity_str_lower for kw in ['one', '一个', '一块']):
            return 1
        else:
            return 5
    
    def _build_relation_graph(self, pair_relations: List[Dict], 
                             group_relations: List[Dict],
                             objects: List[str]) -> Dict:
        """构建关系图"""
        graph = {
            'nodes': [{'id': i, 'type': obj_type} for i, obj_type in enumerate(objects)],
            'edges': [],
            'groups': []
        }
        
        # 添加成对关系边
        for rel in pair_relations:
            subject_idx = objects.index(rel['subject']) if rel['subject'] in objects else None
            object_idx = objects.index(rel['object']) if rel['object'] in objects else None
            
            if subject_idx is not None and object_idx is not None:
                graph['edges'].append({
                    'from': subject_idx,
                    'to': object_idx,
                    'relation': rel['type'],
                    'distance': rel['distance'],
                    'confidence': rel['confidence']
                })
        
        # 添加组关系
        for rel in group_relations:
            graph['groups'].append({
                'type': rel['type'],
                'group_type': rel['group_type'],
                'center_type': rel.get('center_type'),
                'radius': rel['radius'],
                'quantity': rel.get('quantity', 5)
            })
        
        return graph
















