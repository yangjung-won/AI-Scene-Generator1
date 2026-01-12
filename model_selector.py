"""
AI场景生成器 - 模型选择模块
从JSON模型库中选择合适的3D模型

作者: coco
版本: 1.0
"""

import json
import os
import random
from pathlib import Path

# ===========================================
# 模型选择模块
# ===========================================

class ModelSelector:
    """模型选择器"""

    def __init__(self):
        self.models_data = []
        self.json_path = r"C:\Users\Lenovo\Desktop\updated_descriptions_json.json"
        self._load_models_data()

        # 模型兼容性评分权重
        self.compatibility_weights = {
            'category_match': 0.4,      # 类别匹配
            'quality_score': 0.25,      # 质量评分
            'file_availability': 0.2,   # 文件可用性
            'attribute_match': 0.15     # 属性匹配
        }
        
        # 程序化生成器（延迟加载）
        self.procedural_generator = None

    def _load_models_data(self):
        """加载模型数据"""
        try:
            print(f"[LOADING] Loading model data: {self.json_path}")
            if os.path.exists(self.json_path):
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if 'models' in data:
                    self.models_data = data['models']
                else:
                    self.models_data = data if isinstance(data, list) else []

                print(f"[OK] Loaded {len(self.models_data)} model definitions")

                # 统计模型类别
                categories = {}
                for model in self.models_data:
                    cat = model.get('category', 'unknown')
                    categories[cat] = categories.get(cat, 0) + 1
                print(f"[INFO] Model category distribution: {categories}")

            else:
                print(f"[WARN] Model file does not exist: {self.json_path}")
                self.models_data = []

        except Exception as e:
            print(f"[ERROR] Model data loading failed: {e}")
            self.models_data = []

    def select_models(self, scene_plan):
        """
        根据场景规划选择模型

        Args:
            scene_plan (dict): 场景规划结果

        Returns:
            dict: 模型选择结果
        """
        print("[SELECTING] Starting model selection...")

        object_counts = scene_plan.get('object_counts', {})
        layout_config = scene_plan.get('layout_config', {})

        selected_models = {
            'trees': [],
            'flowers': [],
            'stones': [],
            'grasses': [],
            'buildings': [],
            'waters': [],
            'bushes': [],
            'paths': []
        }

        selection_stats = {
            'total_requested': 0,
            'total_selected': 0,
            'categories_covered': 0
        }

        # 为每个对象类型选择模型
        for obj_type, count in object_counts.items():
            selection_stats['total_requested'] += count

            if obj_type == 'tree':
                selected_models['trees'] = self._select_tree_models(count, scene_plan)
            elif obj_type == 'flower':
                selected_models['flowers'] = self._select_flower_models(count, scene_plan)
            elif obj_type == 'stone':
                selected_models['stones'] = self._select_stone_models(count, scene_plan)
            elif obj_type == 'grass':
                selected_models['grasses'] = self._select_grass_models(count, scene_plan)
            elif obj_type == 'building':
                selected_models['buildings'] = self._select_building_models(count, scene_plan)
            elif obj_type == 'water':
                selected_models['waters'] = self._select_water_models(count, scene_plan)
            elif obj_type == 'bush':
                selected_models['bushes'] = self._select_bush_models(count, scene_plan)
            elif obj_type == 'path':
                selected_models['paths'] = self._select_path_models(count, scene_plan)

            selected_count = len(selected_models[self._get_model_list_key(obj_type)])
            selection_stats['total_selected'] += selected_count

        selection_stats['categories_covered'] = sum(1 for models in selected_models.values() if models)

        result = {
            'selected_models': selected_models,
            'selection_stats': selection_stats,
            'model_validation': self._validate_selected_models(selected_models)
        }

        print(f"[OK] Model selection completed: {selection_stats['total_selected']}/{selection_stats['total_requested']} models")

        return result

    def _get_model_list_key(self, obj_type):
        """获取模型列表的键名"""
        key_mapping = {
            'tree': 'trees',
            'flower': 'flowers',
            'stone': 'stones',
            'grass': 'grasses',
            'building': 'buildings',
            'water': 'waters',
            'bush': 'bushes',
            'path': 'paths'
        }
        return key_mapping.get(obj_type, f"{obj_type}s")
    
    def _filter_models_by_season(self, models, nlp_result):
        """
        🆕 根据季节属性过滤模型（仅适用于植物）
        
        Args:
            models: 模型列表
            nlp_result: NLP解析结果，包含seasons字段
            
        Returns:
            list: 过滤后的模型列表（只包含season匹配或allseason的模型）
        """
        identified_seasons = nlp_result.get('seasons', []) if nlp_result else []
        
        if not identified_seasons:
            # 如果没有指定季节，返回所有模型
            return models
        
        # 将季节转换为小写列表
        season_list = [s.lower() for s in identified_seasons]
        print(f"[SEASON_FILTER] Filtering {len(models)} models by season: {season_list}")
        
        # 只保留season属性匹配的模型（包括"allseason"）
        filtered_models = []
        for model in models:
            model_season_raw = model.get('season', [])
            
            # 🆕 处理数组格式：JSON中的season是数组，如["winter"]或["allseason"]
            if isinstance(model_season_raw, list):
                model_seasons = [str(s).lower() for s in model_season_raw if s]
            elif model_season_raw:
                # 向后兼容：如果是字符串，转换为列表
                model_seasons = [str(model_season_raw).lower()]
            else:
                model_seasons = []
            
            # 检查模型季节是否匹配：必须是用户输入的季节之一，或者是"allseason"
            if model_seasons:
                matched = False
                for model_season in model_seasons:
                    # 检查是否匹配用户输入的季节
                    if any(season in model_season for season in season_list):
                        matched = True
                        break
                    # 检查是否是allseason（支持多种格式）
                    if 'allseason' in model_season or \
                       'all_season' in model_season or \
                       'all-season' in model_season or \
                       'all season' in model_season:
                        matched = True
                        break
                
                if matched:
                    filtered_models.append(model)
                    print(f"    [MATCH] 季节匹配: Model {model.get('id', 'unknown')} season={model_seasons}")
                else:
                    print(f"    [SKIP] 季节不匹配: Model {model.get('id', 'unknown')} season={model_seasons} (需要: {season_list})")
            else:
                # 如果模型没有season属性，保留（但会在评分中降低优先级）
                filtered_models.append(model)
                print(f"    [WARN] 模型无season属性: Model {model.get('id', 'unknown')}")
        
        if filtered_models:
            print(f"[SEASON_FILTER] After filtering: {len(filtered_models)}/{len(models)} models match season {season_list}")
        else:
            print(f"[WARN] No models match season {season_list}, using all available models")
            # 如果没有匹配的模型，使用所有可用模型（但会在评分中降低优先级）
            filtered_models = models
        
        return filtered_models
    
    def _filter_models_by_style(self, models, nlp_result):
        """
        🆕 根据风格属性过滤模型（适用于所有模型类型）
        
        Args:
            models: 模型列表
            nlp_result: NLP解析结果，包含styles字段
            
        Returns:
            list: 过滤后的模型列表（只包含style匹配的模型）
        """
        identified_styles = nlp_result.get('styles', []) if nlp_result else []
        
        if not identified_styles:
            # 如果没有指定风格，返回所有模型
            return models
        
        # 将风格转换为小写列表
        style_list = [s.lower() for s in identified_styles]
        print(f"[STYLE_FILTER] Filtering {len(models)} models by style: {style_list}")
        
        # 风格关键词映射（支持多种表达方式）
        style_keywords = {
            'cartoon': ['cartoon', '卡通', '可爱', '动画', 'cute', 'kawaii', 'animated', 'anime', '二次元', '萌'],
            'realistic': ['realistic', '写实', '真实', '逼真', 'detailed', 'photorealistic', 'lifelike', 'natural', '照片级', '超写实'],
            'minimal': ['minimal', '简约', '简单', '极简', 'clean', 'simple', 'minimalist', '简洁', '素雅'],
            'natural': ['natural', '自然', '天然', 'organic', '原生态', '野生'],
            'fantasy': ['fantasy', '奇幻', '幻想', '魔幻', 'magical', 'mystical', 'fairy', '童话', '仙境', 'fairytale'],
            'modern': ['modern', '现代', '当代', 'contemporary', '摩登', '时尚'],
            'classical': ['classical', 'classic', '古典', '经典', '传统', 'traditional', '复古', 'vintage', 'retro', '古风'],
            'industrial': ['industrial', '工业', '机械', 'mechanical', 'steampunk', '工业风'],
            'japanese': ['japanese', '日式', '和风', '禅意', 'zen', '和式'],
            'chinese': ['chinese', '中式', '中国风', '东方', 'oriental'],
            'european': ['european', '欧式', '欧洲', '西式', 'western'],
            'futuristic': ['futuristic', '未来', '科幻', 'sci-fi', 'cyberpunk', '赛博'],
        }
        
        # 只保留style属性匹配的模型
        filtered_models = []
        for model in models:
            model_style_raw = model.get('style', [])
            
            # 🆕 处理数组格式：JSON中的style是数组，如["cartoon"]或["realistic", "cute"]
            if isinstance(model_style_raw, list):
                model_styles = [str(s).lower() for s in model_style_raw if s]
            elif model_style_raw:
                # 向后兼容：如果是字符串，转换为列表
                model_styles = [str(model_style_raw).lower()]
            else:
                model_styles = []
            
            # 检查模型风格是否匹配
            if model_styles:
                # 检查是否匹配任何识别的风格
                matched = False
                for identified_style in style_list:
                    # 遍历模型的所有风格
                    for model_style in model_styles:
                        # 直接匹配
                        if identified_style in model_style or model_style in identified_style:
                            matched = True
                            break
                        # 通过关键词映射匹配
                        if identified_style in style_keywords:
                            keywords = style_keywords[identified_style]
                            if any(kw in model_style for kw in keywords):
                                matched = True
                                break
                    if matched:
                        break
                
                if matched:
                    filtered_models.append(model)
                    print(f"    ✅ 风格匹配: Model {model.get('id', 'unknown')} style={model_styles}")
                else:
                    print(f"    ❌ 风格不匹配: Model {model.get('id', 'unknown')} style={model_styles} (需要: {style_list})")
            else:
                # 如果模型没有style属性，保留（但会在评分中降低优先级）
                filtered_models.append(model)
                print(f"    ⚠️ 模型无style属性: Model {model.get('id', 'unknown')}")
        
        if filtered_models:
            print(f"[STYLE_FILTER] After filtering: {len(filtered_models)}/{len(models)} models match style {style_list}")
        else:
            print(f"[WARN] No models match style {style_list}, using all available models")
            # 如果没有匹配的模型，使用所有可用模型（但会在评分中降低优先级）
            filtered_models = models
        
        return filtered_models

    def _select_tree_models(self, count, scene_plan):
        """选择树模型"""
        trees = []
        tree_models = [m for m in self.models_data if m.get('category') == 'tree']

        if not tree_models:
            print("[WARN] No tree models found")
            # 使用程序化生成
            return self._generate_procedural_models('tree', count, scene_plan)

        print(f"[SELECTING] {count} tree models (available: {len(tree_models)})")

        # 获取场景参数
        ltc_params = scene_plan.get('planning_metadata', {})
        # 获取NLP结果，用于语义匹配和风格匹配
        nlp_result = scene_plan.get('nlp_result', {})
        original_text = nlp_result.get('original_text', '').lower()
        
        # 将NLP结果添加到ltc_params中，供评分函数使用
        if isinstance(ltc_params, dict):
            ltc_params['nlp_result'] = nlp_result

        valid_models = [m for m in tree_models if self._is_model_available(m)]
        if not valid_models:
            # 模型库中没有可用模型，使用程序化生成
            print("[WARN] No available tree models found, using procedural generation")
            return self._generate_procedural_models('tree', count, scene_plan)

        print(f"[FILTERING] Before season filter: {len(valid_models)} models")
        
        # 根据季节属性严格过滤模型
        valid_models_before_season = valid_models.copy()
        valid_models = self._filter_models_by_season(valid_models, nlp_result)
        
        print(f"[FILTERING] After season filter: {len(valid_models)} models")
        
        # 如果季节过滤后没有模型了，保留所有可用模型
        if not valid_models and valid_models_before_season:
            print("[WARN] Season filter removed all models. Keeping all available models.")
            valid_models = valid_models_before_season

        # [CRITICAL FIX] 检查用户是否明确要求特定树类型
        # 如果是，只从匹配的模型中选择（允许重复使用）
        oak_keywords = ['oak', '橡树', '橡', 'oak tree', 'oak forest', 'oak grove']
        pine_keywords = ['pine', '松树', '松', 'pine tree', 'conifer']
        tropical_keywords = ['palm', 'coconut', 'tropical', 'tropic', '热带', '棕榈', '椰子树']
        cherry_keywords = ['cherry', '樱花', '櫻花', 'blossom', 'sakura']
        
        user_wants_oak = any(kw in original_text for kw in oak_keywords)
        user_wants_pine = any(kw in original_text for kw in pine_keywords)
        user_wants_tropical = any(kw in original_text for kw in tropical_keywords)
        user_wants_cherry = any(kw in original_text for kw in cherry_keywords)
        
        # 如果用户明确要求特定类型，筛选出匹配的模型
        if user_wants_oak or user_wants_pine or user_wants_tropical or user_wants_cherry:
            filtered_models = []
            for m in valid_models:
                model_id = str(m.get('id', '')).lower()
                model_name = str(m.get('name', '')).lower()
                model_file = str(m.get('file', '') or m.get('file_path', '')).lower()
                model_text = ' '.join([model_id, model_name, model_file])
                
                if user_wants_oak and ('oak' in model_id or 'oak' in model_name or 'oak' in model_file):
                    filtered_models.append(m)
                    print(f"  [OAK FILTER] Match: {m.get('id')}")
                elif user_wants_pine and any(kw in model_text for kw in pine_keywords):
                    filtered_models.append(m)
                elif user_wants_tropical and any(kw in model_text for kw in tropical_keywords):
                    filtered_models.append(m)
                elif user_wants_cherry and any(kw in model_text for kw in cherry_keywords):
                    filtered_models.append(m)
            
            if filtered_models:
                tree_type = 'oak' if user_wants_oak else 'pine' if user_wants_pine else 'tropical' if user_wants_tropical else 'cherry'
                print(f"[FILTER] User wants {tree_type} trees. Found {len(filtered_models)} matching models.")
                print(f"[FILTER] Will ONLY use these {len(filtered_models)} models (with repetition if needed)")
                valid_models = filtered_models
            else:
                tree_type = 'oak' if user_wants_oak else 'pine' if user_wants_pine else 'tropical' if user_wants_tropical else 'cherry'
                print(f"[WARN] User wants {tree_type} trees but no matching models found. Using all available models.")

        # 选择树模型（允许重复使用）
        used_model_ids = set()  # 跟踪已使用的模型ID
        
        for i in range(count):
            # 优先选择未使用过的模型
            available_models = [m for m in valid_models if m.get('id') not in used_model_ids]
            
            # 如果所有模型都已使用过，允许重复
            if not available_models:
                available_models = valid_models
                used_model_ids.clear()  # 重置，允许重复选择
            
            if available_models:
                candidate = self._select_best_tree_model(available_models, ltc_params, i, original_text)
                if candidate:
                    trees.append(candidate)
                    used_model_ids.add(candidate.get('id'))
                    print(f"  Tree {len(trees)}: {candidate.get('id', 'unknown')}")

        # 如果选择的树木数量不足，重复使用已有模型
        if count > len(trees) and valid_models:
            print(f"[INFO] Need {count} trees, selected {len(trees)}, filling with repetition")
            remaining = count - len(trees)
            for i in range(remaining):
                model = random.choice(valid_models)
                trees.append(model)
                print(f"  [REUSE] {model.get('id', 'unknown')}")
        elif count > len(trees):
            remaining = count - len(trees)
            print(f"[WARN] No available models, generating {remaining} procedural trees")
            procedural = self._generate_procedural_models('tree', remaining, scene_plan)
            trees.extend(procedural)

        return trees

    def _select_best_tree_model(self, tree_models, ltc_params, index, original_text=''):
        """选择最佳的树模型"""
        if not tree_models:
            return None

        # 为不同位置选择不同大小的树
        size_preference = 'medium'
        if index % 3 == 0:
            size_preference = 'large'
        elif index % 3 == 1:
            size_preference = 'small'

        # 评分候选模型
        scored_models = []
        for model in tree_models:
            score = self._score_tree_model(model, ltc_params, size_preference, original_text)
            scored_models.append((score, model))

        # 按评分排序并选择
        scored_models.sort(key=lambda x: x[0], reverse=True)

        # 🆕 检查用户是否明确要求特定树类型（oak, pine, tropical等）
        oak_keywords = ['oak', '橡树', '橡', 'oak tree', 'oak forest', 'oak grove']
        pine_keywords = ['pine', '松树', '松', 'pine tree', 'conifer']
        tropical_keywords = ['palm', 'coconut', 'tropical', 'tropic', '热带', '棕榈', '椰子树']
        cherry_keywords = ['cherry', '樱花', '櫻花', 'blossom', 'sakura']
        
        user_wants_oak = any(kw in original_text for kw in oak_keywords)
        user_wants_pine = any(kw in original_text for kw in pine_keywords)
        user_wants_tropical = any(kw in original_text for kw in tropical_keywords)
        user_wants_cherry = any(kw in original_text for kw in cherry_keywords)
        
        # 🆕 调试信息
        if user_wants_oak:
            print(f"    [DEBUG] 用户要求oak树，正在从 {len(tree_models)} 个模型中筛选")
        
        # 🆕 如果用户明确要求特定树类型，优先选择匹配的模型（增强版）
        if user_wants_oak or user_wants_pine or user_wants_tropical or user_wants_cherry:
            # 筛选出匹配的模型
            matching_models = []
            non_matching_models = []  # 🆕 记录不匹配的模型
            
            for score, model in scored_models:
                # 🆕 增强模型文本匹配：包含ID、name、file路径等
                model_id = str(model.get('id', '')).lower()
                model_name = str(model.get('name', '')).lower()
                model_file = str(model.get('file', '') or model.get('file_path', '')).lower()
                model_text = ' '.join([model_id, model_name, model_file])
                
                is_match = False
                # 🆕 增强oak匹配：检查ID中是否包含 "oak"（包括 "tree_oak tree_001" 这种格式）
                if user_wants_oak:
                    # 检查多种匹配方式
                    if 'oak' in model_id:  # 🆕 优先检查ID（最直接）
                        is_match = True
                        print(f"    [OAK MATCH] ID匹配: {model.get('id')} - 文件: {model_file}")
                    elif 'oak' in model_name:  # 检查名称
                        is_match = True
                        print(f"    [OAK MATCH] Name匹配: {model.get('id')} ({model_name})")
                    elif 'oak' in model_file:  # 检查文件路径
                        is_match = True
                        print(f"    [OAK MATCH] File匹配: {model.get('id')} - {model_file}")
                    elif any(kw in model_text for kw in oak_keywords):  # 检查其他关键词
                        is_match = True
                elif user_wants_pine and any(kw in model_text for kw in pine_keywords):
                    is_match = True
                elif user_wants_tropical and any(kw in model_text for kw in tropical_keywords):
                    is_match = True
                elif user_wants_cherry and any(kw in model_text for kw in cherry_keywords):
                    is_match = True
                
                if is_match:
                    matching_models.append((score, model))
                else:
                    non_matching_models.append((score, model))
            
            # 🆕 如果找到匹配的模型，强制从匹配的模型中选择（不允许选择非匹配模型）
            if matching_models:
                print(f"    [PRIORITY] 用户要求特定树类型，从 {len(matching_models)} 个匹配模型中选择（排除 {len(non_matching_models)} 个非匹配模型）")
                # 🆕 按评分排序，优先选择评分最高的匹配模型
                matching_models.sort(key=lambda x: x[0], reverse=True)
                # 从匹配的模型中选择前5个，使用加权随机
                top_matching = matching_models[:min(5, len(matching_models))]
                weights = [max(0, score + 1000) for score, _ in top_matching]  # 🆕 给匹配模型额外加分，确保优先选择
                total_weight = sum(weights)
                if total_weight > 0:
                    weights = [w / total_weight for w in weights]
                    selected = random.choices(top_matching, weights=weights, k=1)[0]
                    print(f"    [SELECTED] 选择了匹配模型: {selected[1].get('id', 'unknown')}")
                    return selected[1]
                else:
                    return top_matching[0][1] if top_matching else None
            else:
                print(f"    [WARN] 用户要求特定树类型，但未找到匹配的模型！使用所有可用模型")
                # 🆕 如果找不到匹配的模型，不返回None，而是使用所有可用模型
                # 这样可以确保调用已有模型，而不是触发程序化生成
                if scored_models:
                    return scored_models[0][1]  # 返回评分最高的模型
                return None
        
        # 🆕 如果没有特定要求，使用多样性选择
        top_candidates = scored_models[:min(5, len(scored_models))]
        if top_candidates:
            # 🆕 使用加权随机选择，高分模型有更高概率，但低分模型也有机会
            # 这样可以确保选择多种不同的树木
            weights = [max(0, score) for score, _ in top_candidates]  # 确保权重非负
            # 归一化权重
            total_weight = sum(weights)
            if total_weight > 0:
                weights = [w / total_weight for w in weights]
                # 使用加权随机选择
                selected = random.choices(top_candidates, weights=weights, k=1)[0]
                return selected[1]
            else:
                # 如果权重都为0，使用均匀随机
                return random.choice(top_candidates)[1]

        return None

    def _score_tree_model(self, model, ltc_params, size_preference, original_text=''):
        """为树模型评分 - 增强：考虑模型风格"""
        score = 0.0

        # 文件可用性评分
        file_path = model.get('file_path') or model.get('file')
        if file_path and os.path.exists(file_path):
            score += self.compatibility_weights['file_availability'] * 100
        else:
            score += self.compatibility_weights['file_availability'] * 10  # 文件不存在但仍给低分

        # 质量评分
        quality = model.get('quality', 50)
        score += self.compatibility_weights['quality_score'] * quality

        # 🆕 风格匹配评分（从JSON中读取style字段）
        # 处理数组格式的style
        model_style_raw = model.get('style', [])
        if isinstance(model_style_raw, list):
            model_styles = [str(s).lower() for s in model_style_raw if s]
        elif model_style_raw:
            model_styles = [str(model_style_raw).lower()]
        else:
            model_styles = []
        
        nlp_result = ltc_params.get('nlp_result', {}) if isinstance(ltc_params, dict) else {}
        nlp_styles = [s.lower() for s in nlp_result.get('styles', [])]
        
        if model_styles and nlp_styles:
            # 检查模型风格是否匹配NLP识别的风格
            style_keywords = {
                'realistic': ['realistic', '写实', '真实', '逼真'],
                'cartoon': ['cartoon', '卡通', '可爱', '动画'],
                'minimal': ['minimal', '简约', '简单', '极简'],
                'natural': ['natural', '自然', '天然'],
                'fantasy': ['fantasy', '奇幻', '幻想', '魔幻'],
                'modern': ['modern', '现代', '当代'],
                'classical': ['classical', 'classic', '古典', '经典'],
                'japanese': ['japanese', '日式', '和风', '禅意'],
                'chinese': ['chinese', '中式', '中国风']
            }
            
            for nlp_style in nlp_styles:
                if nlp_style in style_keywords:
                    keywords = style_keywords[nlp_style]
                    # 检查模型的每个风格是否匹配
                    for model_style in model_styles:
                        if any(kw in model_style for kw in keywords):
                            score += 100  # 风格匹配大幅加分
                            print(f"    🎨 风格匹配: NLP={nlp_style}, Model={model_styles}")
                            break
                    if score > 0:  # 如果已经匹配，跳出外层循环
                        break
        
        # 大小偏好匹配
        model_size = model.get('size', 'medium')
        if model_size == size_preference:
            score += self.compatibility_weights['attribute_match'] * 50
        elif abs(['small', 'medium', 'large'].index(model_size) -
                ['small', 'medium', 'large'].index(size_preference)) == 1:
            score += self.compatibility_weights['attribute_match'] * 25

        # 🆕 语义匹配：检查模型名称、ID、描述中是否包含用户输入的关键词
        if original_text:
            # 🆕 处理数组格式的style和season
            model_style_raw = model.get('style', [])
            model_season_raw = model.get('season', [])
            
            model_style_str = ', '.join([str(s) for s in model_style_raw]) if isinstance(model_style_raw, list) else str(model_style_raw)
            model_season_str = ', '.join([str(s) for s in model_season_raw]) if isinstance(model_season_raw, list) else str(model_season_raw)
            
            model_text = ' '.join([
                str(model.get('id', '')),
                str(model.get('name', '')),
                str(model.get('description', '')),
                model_style_str,
                model_season_str
            ]).lower()
            
            # 🆕 松树相关关键词（高优先级）
            pine_keywords = ['pine', '松树', '松', 'pine tree', 'conifer', '针叶树', '常青树']
            user_has_pine = any(kw in original_text for kw in pine_keywords)
            model_has_pine = any(kw in model_text for kw in pine_keywords)
            
            if user_has_pine and model_has_pine:
                score += 250  # 比樱花更高优先级
                print(f"    🎯 松树匹配: 用户输入包含松树关键词，模型 {model.get('id', 'unknown')} 匹配")
            elif user_has_pine and not model_has_pine:
                score -= 100  # 如果用户要松树但模型不是，大幅降低评分
            
            # 🆕 冬季/雪地相关关键词
            winter_keywords = ['winter', 'wintery', 'wintry', '冬天', '冬季', '雪', 'snow', 'snowy', 
                             'frosty', 'frost', 'frosted', '雪地', '雪白', '积雪']
            user_has_winter = any(kw in original_text for kw in winter_keywords)
            model_has_winter = any(kw in model_text for kw in winter_keywords)
            
            if user_has_winter and model_has_winter:
                score += 200  # 冬季匹配高优先级
                print(f"    ❄️ 冬季匹配: 用户输入包含冬季关键词，模型 {model.get('id', 'unknown')} 匹配")
            elif user_has_winter and not model_has_winter:
                score -= 80  # 如果用户要冬季但模型不是，降低评分
            
            # 樱花相关关键词
            cherry_keywords = ['cherry', '樱花', '櫻花', 'blossom', 'sakura']
            user_has_cherry = any(kw in original_text for kw in cherry_keywords)
            model_has_cherry = any(kw in model_text for kw in cherry_keywords)
            
            if user_has_cherry and model_has_cherry:
                # 如果用户提到樱花，且模型也是樱花树，大幅提高评分
                score += 200  # 高优先级匹配
                print(f"    🎯 语义匹配: 用户输入包含樱花关键词，模型 {model.get('id', 'unknown')} 匹配")
            elif user_has_cherry and not model_has_cherry:
                # 如果用户提到樱花，但模型不是樱花树，降低评分
                score -= 50
            
            # 🆕 橡树相关关键词（高优先级）
            oak_keywords = ['oak', '橡树', '橡', 'oak tree', 'oak forest', 'oak grove']
            user_has_oak = any(kw in original_text for kw in oak_keywords)
            
            # 🆕 增强模型oak检测：检查ID、name、file路径
            model_id = str(model.get('id', '')).lower()
            model_name = str(model.get('name', '')).lower()
            model_file = str(model.get('file', '') or model.get('file_path', '')).lower()
            model_has_oak = (
                any(kw in model_text for kw in oak_keywords) or
                'oak' in model_id or  # 🆕 直接检查ID中是否包含oak（包括 "tree_oak tree_001" 格式）
                'oak' in model_name or  # 🆕 检查name中是否包含oak
                'oak' in model_file  # 🆕 检查文件路径中是否包含oak
            )
            
            if user_has_oak and model_has_oak:
                score += 500  # 🆕 大幅提高橡树匹配优先级（从250增加到500），确保优先选择
                print(f"    [OAK] 橡树匹配: 用户输入包含橡树关键词，模型 {model.get('id', 'unknown')} 匹配，评分+500")
            elif user_has_oak and not model_has_oak:
                score -= 200  # 🆕 如果用户要橡树但模型不是，大幅降低评分（从-100增加到-200）
                print(f"    [OAK] 非橡树模型: 用户要求橡树，但模型 {model.get('id', 'unknown')} 不是橡树，评分-200")
            
            # 🆕 热带树木关键词（如果用户要冬季，应该排除热带树木）
            tropical_keywords = ['palm', 'coconut', 'tropical', 'tropic', '热带', '棕榈', '椰子树', 'rainforest', '雨林']
            user_has_tropical = any(kw in original_text for kw in tropical_keywords)
            model_has_tropical = any(kw in model_text for kw in tropical_keywords)
            
            # 🆕 如果用户要热带场景，且模型是热带树木，大幅提高评分
            if user_has_tropical and model_has_tropical:
                score += 300  # 热带匹配最高优先级
                print(f"    [TROPICAL] 热带匹配: 用户输入包含热带关键词，模型 {model.get('id', 'unknown')} 匹配")
            elif user_has_tropical and not model_has_tropical:
                score -= 100  # 如果用户要热带但模型不是，降低评分
            elif user_has_winter and model_has_tropical:
                score -= 150  # 如果用户要冬季但模型是热带树木，大幅降低评分
                print(f"    ⚠️ 季节冲突: 用户要冬季场景，但模型是热带树木 {model.get('id', 'unknown')}")

        # 🆕 季节匹配（增强：支持所有季节，包括冬天，正确处理数组格式）
        nlp_result = ltc_params.get('nlp_result', {}) if isinstance(ltc_params, dict) else {}
        identified_seasons = nlp_result.get('seasons', [])
        
        # 处理数组格式的season
        model_season_raw = model.get('season', [])
        if isinstance(model_season_raw, list):
            model_seasons = [str(s).lower() for s in model_season_raw if s]
        elif model_season_raw:
            model_seasons = [str(model_season_raw).lower()]
        else:
            model_seasons = []
        
        if identified_seasons and model_seasons:
            # 检查模型季节是否匹配NLP识别的季节
            identified_seasons_lower = [s.lower() for s in identified_seasons]
            matched = False
            
            for model_season in model_seasons:
                # 直接匹配
                if model_season in identified_seasons_lower:
                    matched = True
                    break
                # 检查是否是allseason
                if 'allseason' in model_season or 'all_season' in model_season or 'all-season' in model_season or 'all season' in model_season:
                    matched = True
                    break
            
            if matched:
                score += 150  # 季节匹配大幅加分（比风格匹配更高，因为季节更具体）
                print(f"    ❄️ 季节匹配: NLP={identified_seasons}, Model={model_seasons}")
            else:
                # 如果用户指定了季节，但模型不匹配，降低评分
                score -= 30
                print(f"    ⚠️ 季节不匹配: NLP={identified_seasons}, Model={model_seasons}")
        elif identified_seasons and not model_seasons:
            # 如果用户指定了季节，但模型没有季节信息，轻微降低评分
            score -= 10
        elif model_seasons and not identified_seasons:
            # 如果模型有季节信息，但用户没有指定，不影响评分（保持中性）
            pass

        return score

    def _select_flower_models(self, count, scene_plan):
        """选择花模型"""
        flowers = []
        flower_models = [m for m in self.models_data if m.get('category') == 'flower']

        if not flower_models:
            print("[WARN] No flower models found")
            return self._generate_procedural_models('flower', count, scene_plan)

        print(f"[SELECTING] {count} flower models (available: {len(flower_models)})")

        valid_models = [m for m in flower_models if self._is_model_available(m)]
        if not valid_models:
            return self._generate_procedural_models('flower', count, scene_plan)
        
        # 🆕 先应用风格过滤（适用于所有模型）
        nlp_result = scene_plan.get('nlp_result', {})
        valid_models = self._filter_models_by_style(valid_models, nlp_result)
        
        # 🆕 再应用季节过滤（仅适用于植物）
        valid_models = self._filter_models_by_season(valid_models, nlp_result)

        for i in range(min(count, len(valid_models))):
            flower = random.choice(valid_models)
            flowers.append(flower)

        if count > len(flowers):
            remaining = count - len(flowers)
            procedural = self._generate_procedural_models('flower', remaining, scene_plan)
            flowers.extend(procedural)

        return flowers

    def _select_stone_models(self, count, scene_plan):
        """选择石头模型（根据场景类型过滤钟乳石）"""
        stones = []
        stone_models = [m for m in self.models_data if m.get('category') == 'stone']

        if not stone_models:
            print("[WARN] No stone models found")
            return self._generate_procedural_models('stone', count, scene_plan)

        # 🆕 获取场景类型，过滤钟乳石（从多个来源获取，确保准确性）
        nlp_result = scene_plan.get('nlp_result', {})
        scene_type = (nlp_result.get('scene_type') or 
                     scene_plan.get('scene_type') or 
                     'garden')
        
        # 🆕 强制转换为小写，确保匹配
        scene_type = str(scene_type).lower()
        
        print(f"[STONE_FILTER] 场景类型: {scene_type}")
        
        # 🆕 根据场景类型过滤石头（严格检查：只有 'cave' 才使用钟乳石）
        if scene_type == 'cave':
            # 溶洞场景：只使用钟乳石（检查多个字段）
            cave_stones = []
            for m in stone_models:
                model_id = str(m.get('id', '')).lower()
                model_name = str(m.get('name', '')).lower()
                model_desc = str(m.get('description', '')).lower()
                
                if any(keyword in model_id or keyword in model_name or keyword in model_desc 
                      for keyword in ['stalactite', 'stalagmite', '钟乳石', '石钟乳', '石笋']):
                    cave_stones.append(m)
            
            stone_models = cave_stones if cave_stones else stone_models
            print(f"[SELECTING] {count} cave stone models (stalactites only, available: {len(stone_models)})")
        else:
            # 🆕 其他场景：严格排除钟乳石和温泉（检查 id, name, description 等字段）
            filtered_stones = []
            for m in stone_models:
                model_id = str(m.get('id', '')).lower()
                model_name = str(m.get('name', '')).lower()
                model_desc = str(m.get('description', '')).lower()
                
                # 检查是否包含钟乳石相关关键词
                is_stalactite = any(keyword in model_id or keyword in model_name or keyword in model_desc 
                                   for keyword in ['stalactite', 'stalagmite', '钟乳石', '石钟乳', '石笋'])
                is_hotspring = any(keyword in model_id or keyword in model_name or keyword in model_desc 
                                  for keyword in ['hotspring', '温泉'])
                
                if not is_stalactite and not is_hotspring:
                    filtered_stones.append(m)
            
            stone_models = filtered_stones
            print(f"[SELECTING] {count} stone models (excluding stalactites, available: {len(stone_models)})")

        if not stone_models:
            print("[WARN] No valid stone models after filtering, using procedural generation")
            return self._generate_procedural_models('stone', count, scene_plan)

        valid_models = [m for m in stone_models if self._is_model_available(m)]
        if not valid_models:
            return self._generate_procedural_models('stone', count, scene_plan)
        
        # 🆕 只应用风格过滤（石头不是植物，不需要季节过滤）
        valid_models = self._filter_models_by_style(valid_models, nlp_result)

        for i in range(min(count, len(valid_models))):
            stone = random.choice(valid_models)
            stones.append(stone)

        if count > len(stones):
            remaining = count - len(stones)
            procedural = self._generate_procedural_models('stone', remaining, scene_plan)
            stones.extend(procedural)

        return stones

    def _select_grass_models(self, count, scene_plan):
        """选择草模型"""
        grasses = []
        grass_models = [m for m in self.models_data if m.get('category') == 'grass']

        if not grass_models:
            print("[WARN] No grass models found")
            return self._generate_procedural_models('grass', count, scene_plan)

        print(f"[SELECTING] {count} grass models (available: {len(grass_models)})")

        valid_models = [m for m in grass_models if self._is_model_available(m)]
        if not valid_models:
            return self._generate_procedural_models('grass', count, scene_plan)
        
        # 🆕 先应用风格过滤（适用于所有模型）
        nlp_result = scene_plan.get('nlp_result', {})
        valid_models = self._filter_models_by_style(valid_models, nlp_result)
        
        # 🆕 再应用季节过滤（仅适用于植物）
        valid_models = self._filter_models_by_season(valid_models, nlp_result)

        for i in range(min(count, len(valid_models))):
            grass = random.choice(valid_models)
            grasses.append(grass)

        if count > len(grasses):
            remaining = count - len(grasses)
            procedural = self._generate_procedural_models('grass', remaining, scene_plan)
            grasses.extend(procedural)

        return grasses

    def _select_building_models(self, count, scene_plan):
        """选择建筑模型"""
        buildings = []
        building_models = [m for m in self.models_data if m.get('category') == 'building']

        if not building_models:
            print("[WARN] No building models found")
            return self._generate_procedural_models('building', count, scene_plan)

        print(f"[SELECTING] {count} building models (available: {len(building_models)})")

        valid_models = [m for m in building_models if self._is_model_available(m)]
        if not valid_models:
            return self._generate_procedural_models('building', count, scene_plan)
        
        # 🆕 只应用风格过滤（建筑不是植物，不需要季节过滤）
        nlp_result = scene_plan.get('nlp_result', {})
        valid_models = self._filter_models_by_style(valid_models, nlp_result)

        for i in range(min(count, len(valid_models))):
            building = random.choice(valid_models)
            buildings.append(building)

        if count > len(buildings):
            remaining = count - len(buildings)
            procedural = self._generate_procedural_models('building', remaining, scene_plan)
            buildings.extend(procedural)

        return buildings

    def _select_water_models(self, count, scene_plan):
        """选择水体模型"""
        waters = []
        water_models = [m for m in self.models_data if m.get('category') == 'water']

        if not water_models:
            print("[WARN] No water models found")
            # 使用程序化生成
            return self._generate_procedural_models('water', count, scene_plan)

        print(f"[SELECTING] {count} water models (available: {len(water_models)})")

        valid_models = [m for m in water_models if self._is_model_available(m)]
        if not valid_models:
            # 模型库中没有可用模型，使用程序化生成
            return self._generate_procedural_models('water', count, scene_plan)
        
        # 🆕 只应用风格过滤（水体不是植物，不需要季节过滤）
        nlp_result = scene_plan.get('nlp_result', {})
        valid_models = self._filter_models_by_style(valid_models, nlp_result)

        for i in range(min(count, len(valid_models))):
            water = random.choice(valid_models)
            waters.append(water)

        # 如果需要的数量超过可用模型，补充程序化生成的模型
        if count > len(waters):
            remaining = count - len(waters)
            procedural = self._generate_procedural_models('water', remaining, scene_plan)
            waters.extend(procedural)

        return waters

    def _select_bush_models(self, count, scene_plan):
        """选择灌木模型"""
        bushes = []
        bush_models = [m for m in self.models_data if m.get('category') in ['bush', 'shrub']]

        if not bush_models:
            print("[WARN] No bush models found")
            return self._generate_procedural_models('bush', count, scene_plan)

        print(f"[SELECTING] {count} bush models (available: {len(bush_models)})")

        valid_models = [m for m in bush_models if self._is_model_available(m)]
        if not valid_models:
            return self._generate_procedural_models('bush', count, scene_plan)
        
        # 🆕 先应用风格过滤（适用于所有模型）
        nlp_result = scene_plan.get('nlp_result', {})
        valid_models = self._filter_models_by_style(valid_models, nlp_result)
        
        # 🆕 再应用季节过滤（仅适用于植物）
        valid_models = self._filter_models_by_season(valid_models, nlp_result)

        for i in range(min(count, len(valid_models))):
            bush = random.choice(valid_models)
            bushes.append(bush)

        if count > len(bushes):
            remaining = count - len(bushes)
            procedural = self._generate_procedural_models('bush', remaining, scene_plan)
            bushes.extend(procedural)

        return bushes

    def _select_path_models(self, count, scene_plan):
        """选择路径模型"""
        paths = []
        path_models = [m for m in self.models_data if m.get('category') in ['path', 'trail']]

        if not path_models:
            print("[WARN] No path models found")
            return self._generate_procedural_models('path', count, scene_plan)

        print(f"[SELECTING] {count} path models (available: {len(path_models)})")

        valid_models = [m for m in path_models if self._is_model_available(m)]
        if not valid_models:
            return self._generate_procedural_models('path', count, scene_plan)
        
        # 🆕 只应用风格过滤（路径不是植物，不需要季节过滤）
        nlp_result = scene_plan.get('nlp_result', {})
        valid_models = self._filter_models_by_style(valid_models, nlp_result)

        for i in range(min(count, len(valid_models))):
            path = random.choice(valid_models)
            paths.append(path)

        if count > len(paths):
            remaining = count - len(paths)
            procedural = self._generate_procedural_models('path', remaining, scene_plan)
            paths.extend(procedural)

        return paths

    def _is_model_available(self, model):
        """检查模型是否可用"""
        file_path = model.get('file_path') or model.get('file')
        if not file_path:
            return False

        # 🆕 处理路径格式：统一转换为Windows路径格式
        # 将 "D:/assets/tree/tree_oak tree_001.blend" 转换为 "D:\assets\tree\tree_oak tree_001.blend"
        if '/' in file_path:
            file_path = file_path.replace('/', os.sep)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            # 🆕 如果文件不存在，尝试其他路径格式
            # 尝试反斜杠格式
            alt_path = file_path.replace(os.sep, '/')
            if os.path.exists(alt_path):
                file_path = alt_path
            else:
                # 🆕 尝试原始路径（可能是相对路径）
                if not os.path.isabs(file_path):
                    # 尝试相对于JSON文件目录
                    json_dir = os.path.dirname(self.json_path)
                    rel_path = os.path.join(json_dir, file_path)
                    if os.path.exists(rel_path):
                        file_path = rel_path
                    else:
                        return False
                else:
                    return False

        # 检查文件大小（避免空文件或损坏文件）
        try:
            file_size = os.path.getsize(file_path)
            if file_size < 1000:  # 小于1KB的文件可能是损坏的
                return False
        except:
            return False

        return True

    def _validate_selected_models(self, selected_models):
        """验证选择的模型"""
        validation = {
            'total_models': 0,
            'available_models': 0,
            'missing_models': 0,
            'categories': {}
        }

        for category, models in selected_models.items():
            validation['total_models'] += len(models)
            validation['categories'][category] = {
                'count': len(models),
                'available': 0,
                'missing': 0
            }

            for model in models:
                file_path = model.get('file_path') or model.get('file')
                if file_path and os.path.exists(file_path):
                    validation['available_models'] += 1
                    validation['categories'][category]['available'] += 1
                else:
                    validation['missing_models'] += 1
                    validation['categories'][category]['missing'] += 1

        validation['availability_rate'] = (
            validation['available_models'] / validation['total_models']
            if validation['total_models'] > 0 else 0
        )

        return validation
    
    def _get_procedural_generator(self):
        """获取程序化生成器（延迟加载）"""
        if self.procedural_generator is None:
            try:
                from procedural_model_generator import ProceduralModelGenerator
                self.procedural_generator = ProceduralModelGenerator()
                print("[OK] Procedural model generator loaded")
            except ImportError as e:
                print(f"[WARN] Procedural generator not available: {e}")
                return None
        return self.procedural_generator
    
    def _generate_procedural_models(self, object_type, count, scene_plan):
        """生成程序化模型"""
        generator = self._get_procedural_generator()
        if not generator:
            print(f"[WARN] Cannot generate procedural {object_type}, generator not available")
            return []
        
        if not generator.can_generate(object_type):
            print(f"[WARN] Cannot generate {object_type} procedurally")
            return []
        
        print(f"[GENERATING] {count} procedural {object_type} models")
        
        ltc_params = scene_plan.get('planning_metadata', {})
        procedural_models = []
        
        for i in range(count):
            # 为每个实例生成不同的属性
            attributes = {
                'size': random.choice(['small', 'medium', 'large']),
                'variation': i % 3  # 增加变化
            }
            
            model_config = generator.generate_model(object_type, attributes, ltc_params)
            
            # 创建模型描述（模拟模型库格式）
            procedural_model = {
                'id': f'procedural_{object_type}_{i:03d}',
                'category': object_type,
                'name': f'Procedural {object_type.title()} {i+1}',
                'file_path': None,  # 程序化生成，无文件路径
                'file': None,
                'type': 'procedural',
                'generation_config': model_config,
                'quality': 75,  # 程序化生成的质量评分
                'size': attributes.get('size', 'medium'),
                'metadata': {
                    'generated': True,
                    'generation_method': 'procedural',
                    'complexity': ltc_params.get('complexity_factor', 0.5),
                    'blender_operations': model_config.get('blender_operations', [])
                }
            }
            
            procedural_models.append(procedural_model)
        
        print(f"[OK] Generated {len(procedural_models)} procedural {object_type} models")
        return procedural_models

