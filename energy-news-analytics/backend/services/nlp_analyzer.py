"""
NLP分析服务 - 实体识别、情感分析、事件提取
"""
import re
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
from loguru import logger

# 尝试导入ML库，如果不可用则使用规则引擎
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers库不可用，将使用规则引擎")

try:
    import jieba
    import jieba.posseg as pseg
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False
    logger.warning("Jieba库不可用")

from models.schemas import (
    NLPAnalysisResult, Entity, SentimentResult, 
    EventInfo, Sentiment, Dimension
)

class NLPAnalyzerService:
    """NLP分析服务"""
    
    # 品种词典
    PRODUCT_PATTERNS = {
        "WTI": ["WTI", "西德克萨斯", "West Texas Intermediate", "美原油"],
        "Brent": ["Brent", "布伦特", "北海原油", "Brent原油"],
        "HH": ["Henry Hub", "HH", "亨利港", "美国天然气"],
        "TTF": ["TTF", "Title Transfer Facility", "荷兰天然气", "欧洲天然气"],
        "JKM": ["JKM", "日韩基准", "Japan Korea Marker", "亚洲LNG"],
        "PG": ["PG", "Propane", "丙烷", "液化石油气", "LPG"],
        "PP": ["PP", "丙烯", "Propylene"],
        "MB": ["MB", "Mont Belvieu"],
        "FEI": ["FEI", "Far East Index", "远东指数"],
        "CP": ["CP", "Contract Price", "沙特合同价", "沙特CP"],
        "原油": ["原油", "石油", "crude oil", "petroleum"],
        "天然气": ["天然气", "natural gas", "燃气"],
        "液化气": ["液化气", "LPG", "液化石油气"],
        "成品油": ["成品油", "汽油", "柴油", "煤油", "燃料油"]
    }
    
    # 实体类型词典
    ORGANIZATION_PATTERNS = [
        "OPEC", "OPEC+", "IEA", "EIA", "API", "SPR",
        "沙特阿美", "俄罗斯石油", "中石油", "中石化", "中海油",
        "埃克森美孚", "壳牌", "BP", "道达尔", "雪佛龙",
        "高盛", "摩根", "花旗", "摩根士丹利", "美银",
        "美联储", "欧洲央行", "中国人民银行", "日本央行"
    ]
    
    LOCATION_PATTERNS = [
        "库欣", "休斯顿", "纽约", "伦敦", "新加坡", "鹿特丹", "富查伊拉",
        "波斯湾", "霍尔木兹海峡", "马六甲海峡", "苏伊士运河",
        "沙特阿拉伯", "俄罗斯", "伊朗", "伊拉克", "阿联酋", "科威特", "卡塔尔",
        "美国", "中国", "印度", "日本", "韩国", "德国", "法国", "英国"
    ]
    
    # 事件类型词典
    EVENT_PATTERNS = {
        "产量变化": ["增产", "减产", "提高产量", "降低产量", "产能", "产量"],
        "库存数据": ["库存增加", "库存减少", "EIA报告", "API报告", "库存数据"],
        "OPEC政策": ["OPEC会议", "减产协议", "增产决议", "配额", "OPEC+"],
        "地缘冲突": ["冲突", "战争", "袭击", "爆炸", "军事"],
        "制裁措施": ["制裁", "禁运", "封锁", "限制", "禁止出口"],
        "经济数据": ["GDP", "PMI", "CPI", "通胀", "就业数据", "非农就业"],
        "货币政策": ["美联储加息", "降息", "QE", "量化宽松", "利率"],
        "自然灾害": ["飓风", "地震", "火灾", "爆炸", "泄漏"]
    }
    
    # 情感词典
    SENTIMENT_WORDS = {
        "positive": {
            "需求": ["强劲", "增长", "超预期", "旺盛", "回暖", "复苏", "增加"],
            "价格": ["上涨", "反弹", "走高", "突破", "飙升", "大涨", "上升"],
            "库存": ["下降", "减少", "去化", "低位", "紧张", "减少"],
            "供应": ["减产", "中断", "收缩", "不足", "紧张", "减少"],
            "宏观": ["复苏", "增长", "向好", "改善", "扩张", "积极"]
        },
        "negative": {
            "需求": ["疲软", "下滑", "萎缩", "低迷", "不足", "放缓", "减少"],
            "价格": ["下跌", "回落", "走低", "暴跌", "下挫", "承压", "下降"],
            "库存": ["增加", "累积", "高企", "过剩", "压力", "上升"],
            "供应": ["增产", "过剩", "恢复", "充裕", "增加", "增长"],
            "宏观": ["衰退", "萎缩", "下行", "恶化", "收缩", "消极"]
        }
    }
    
    # 维度关键词
    DIMENSION_KEYWORDS = {
        "fundamental": {
            "供应": ["产量", "产能", "OPEC", "减产", "增产", "页岩油", "钻机数"],
            "需求": ["需求", "消费", "进口", "出口", "炼厂开工", "炼厂加工量"],
            "库存": ["库存", "EIA", "API", "库欣", "战略储备", "商业库存"]
        },
        "macro": {
            "经济数据": ["GDP", "PMI", "CPI", "就业", "通胀", "衰退", "增长"],
            "货币政策": ["美联储", "加息", "降息", "QE", "美元", "利率"],
            "金融市场": ["美股", "美债", "美元指数", "VIX", "股市", "债市"]
        },
        "sentiment": {
            "市场情绪": ["持仓", "CFTC", "净多头", "投机", "情绪", "恐慌", "贪婪"],
            "机构观点": ["高盛", "摩根", "花旗", "评级", "目标价", "预测"],
            "媒体情绪": ["看涨", "看跌", "乐观", "悲观", "看好", "看空"]
        },
        "technical": {
            "价格形态": ["突破", "支撑", "阻力", "趋势", "均线", "上升通道", "下降通道"],
            "技术指标": ["MACD", "RSI", "布林带", "KDJ", "CCI", "ATR"],
            "量价关系": ["成交量", "持仓量", "放量", "缩量", "量价齐升"]
        },
        "geopolitical": {
            "地区冲突": ["冲突", "战争", "袭击", "中东", "伊朗", "俄罗斯", "以色列"],
            "制裁风险": ["制裁", "禁运", "封锁", "限制", "关税"],
            "运输风险": ["霍尔木兹", "苏伊士", "马六甲", "海峡", "通道", "航运"]
        }
    }
    
    def __init__(self):
        self.sentiment_pipeline = None
        self.ner_pipeline = None
        self.initialized = False
    
    async def initialize(self):
        """初始化NLP模型"""
        try:
            if TRANSFORMERS_AVAILABLE:
                logger.info("加载NLP模型...")
                # 情感分析模型
                self.sentiment_pipeline = pipeline(
                    "sentiment-analysis",
                    model="uer/roberta-base-finetuned-jd-binary-chinese",
                    device=0 if torch.cuda.is_available() else -1
                )
                logger.info("NLP模型加载完成")
            
            # 加载jieba词典
            if JIEBA_AVAILABLE:
                for product, keywords in self.PRODUCT_PATTERNS.items():
                    for keyword in keywords:
                        jieba.add_word(keyword, tag="PRODUCT")
                
                for org in self.ORGANIZATION_PATTERNS:
                    jieba.add_word(org, tag="ORG")
                
                for loc in self.LOCATION_PATTERNS:
                    jieba.add_word(loc, tag="LOC")
            
            self.initialized = True
            logger.info("NLP分析服务初始化完成")
        except Exception as e:
            logger.error(f"NLP初始化失败: {e}")
            self.initialized = False
    
    async def analyze(self, news_item: Dict[str, Any]) -> NLPAnalysisResult:
        """分析单条新闻"""
        start_time = time.time()
        
        try:
            content = news_item.get("content", "")
            title = news_item.get("title", "")
            full_text = f"{title}。{content}"
            
            # 1. 实体识别
            entities = await self._extract_entities(full_text)
            
            # 2. 关键词提取
            keywords = await self._extract_keywords(full_text)
            
            # 3. 情感分析
            sentiment = await self._analyze_sentiment(full_text, entities)
            
            # 4. 事件提取
            events = await self._extract_events(full_text, entities)
            
            # 5. 多维度分析
            dimensions = await self._map_to_dimensions(full_text, entities, events)
            
            # 6. 计算综合得分
            overall_score = self._calculate_overall_score(sentiment, dimensions)
            
            # 7. 生成交易信号
            trading_signal = self._generate_trading_signal(overall_score, sentiment)
            
            processing_time = time.time() - start_time
            
            return NLPAnalysisResult(
                news_id=news_item.get("id", ""),
                entities=entities,
                keywords=keywords,
                sentiment=sentiment,
                events=events,
                dimensions=dimensions,
                dimension_weights=self._calculate_dimension_weights(dimensions),
                overall_score=overall_score,
                trading_signal=trading_signal,
                processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"NLP分析失败: {e}")
            raise
    
    async def analyze_batch(self, news_items: List[Dict[str, Any]]) -> List[NLPAnalysisResult]:
        """批量分析新闻"""
        tasks = [self.analyze(item) for item in news_items]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"分析新闻失败 {news_items[i].get('id')}: {result}")
            else:
                valid_results.append(result)
        
        return valid_results
    
    async def _extract_entities(self, text: str) -> List[Entity]:
        """提取命名实体"""
        entities = []
        
        # 基于规则的实体识别
        # 1. 识别品种
        for product, patterns in self.PRODUCT_PATTERNS.items():
            for pattern in patterns:
                for match in re.finditer(re.escape(pattern), text, re.IGNORECASE):
                    entities.append(Entity(
                        text=match.group(),
                        type="PRODUCT",
                        start=match.start(),
                        end=match.end(),
                        confidence=0.9
                    ))
        
        # 2. 识别组织
        for org in self.ORGANIZATION_PATTERNS:
            for match in re.finditer(re.escape(org), text):
                entities.append(Entity(
                    text=match.group(),
                    type="ORGANIZATION",
                    start=match.start(),
                    end=match.end(),
                    confidence=0.85
                ))
        
        # 3. 识别地点
        for loc in self.LOCATION_PATTERNS:
            for match in re.finditer(re.escape(loc), text):
                entities.append(Entity(
                    text=match.group(),
                    type="LOCATION",
                    start=match.start(),
                    end=match.end(),
                    confidence=0.8
                ))
        
        # 4. 识别价格
        price_patterns = [
            r'\$?\d+\.?\d*\s*(美元|美金|\$)?\s*/?\s*(桶|吨|立方米|MMBtu)?',
            r'\d+\.?\d*\s*(元|人民币|¥)',
        ]
        for pattern in price_patterns:
            for match in re.finditer(pattern, text):
                entities.append(Entity(
                    text=match.group(),
                    type="PRICE",
                    start=match.start(),
                    end=match.end(),
                    confidence=0.75
                ))
        
        # 去重和合并重叠实体
        entities = self._deduplicate_entities(entities)
        
        return entities
    
    async def _extract_keywords(self, text: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """提取关键词"""
        keywords = []
        
        if JIEBA_AVAILABLE:
            # 使用jieba分词
            words = pseg.cut(text)
            word_freq = {}
            
            for word, flag in words:
                # 过滤停用词和短词
                if len(word) < 2 or flag in ['x', 'u', 'c', 'p', 'm', 'f']:
                    continue
                
                # 统计词频
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # 按词频排序
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            
            # 转换为关键词格式
            for word, freq in sorted_words[:top_k]:
                keywords.append({
                    "word": word,
                    "weight": min(freq / 10, 1.0),
                    "pos": "unknown"
                })
        else:
            # 备用方案：基于规则的关键词提取
            for event_type, event_keywords in self.EVENT_PATTERNS.items():
                for keyword in event_keywords:
                    if keyword in text:
                        keywords.append({
                            "word": keyword,
                            "weight": 0.8,
                            "category": event_type
                        })
        
        return keywords[:top_k]
    
    async def _analyze_sentiment(self, text: str, entities: List[Entity]) -> SentimentResult:
        """分析情感倾向"""
        # 基于规则的情感分析
        positive_count = 0
        negative_count = 0
        
        # 统计情感词
        for category, words in self.SENTIMENT_WORDS["positive"].items():
            for word in words:
                positive_count += text.count(word)
        
        for category, words in self.SENTIMENT_WORDS["negative"].items():
            for word in words:
                negative_count += text.count(word)
        
        # 判断情感极性
        if positive_count > negative_count * 1.5:
            overall = Sentiment.POSITIVE
            intensity = min((positive_count - negative_count) / 5 * 100, 100)
        elif negative_count > positive_count * 1.5:
            overall = Sentiment.NEGATIVE
            intensity = min((negative_count - positive_count) / 5 * 100, 100)
        else:
            overall = Sentiment.NEUTRAL
            intensity = 30
        
        # 按品种分析情感
        by_product = {}
        for entity in entities:
            if entity.type == "PRODUCT":
                # 提取产品相关句子
                product_text = self._extract_product_sentences(text, entity.text)
                if product_text:
                    # 分析产品相关情感
                    product_sentiment = await self._analyze_sentiment(product_text, [])
                    by_product[entity.text] = {
                        "sentiment": product_sentiment.overall,
                        "intensity": product_sentiment.intensity
                    }
        
        return SentimentResult(
            overall=overall,
            intensity=intensity,
            confidence=0.7 + min(abs(positive_count - negative_count) / 10, 0.25),
            by_product=by_product
        )
    
    async def _extract_events(self, text: str, entities: List[Entity]) -> List[EventInfo]:
        """提取事件信息"""
        events = []
        
        for event_type, keywords in self.EVENT_PATTERNS.items():
            for keyword in keywords:
                if keyword in text:
                    # 判断事件重要性
                    importance = self._calculate_event_importance(text, keyword, event_type)
                    
                    # 判断情感倾向
                    sentiment = await self._analyze_event_sentiment(text, keyword)
                    
                    # 获取相关产品
                    related_products = [e.text for e in entities if e.type == "PRODUCT"]
                    if not related_products:
                        related_products = ["原油", "天然气"]  # 默认产品
                    
                    events.append(EventInfo(
                        type=event_type,
                        subtype=keyword,
                        importance=importance,
                        sentiment=sentiment,
                        related_products=related_products
                    ))
        
        # 按重要性排序
        events.sort(key=lambda x: x.importance, reverse=True)
        
        return events[:5]  # 最多返回5个事件
    
    async def _map_to_dimensions(self, text: str, entities: List[Entity], events: List[EventInfo]) -> Dict[str, Dict[str, Any]]:
        """映射到五个分析维度"""
        dimensions = {}
        
        for dim_name, dim_keywords in self.DIMENSION_KEYWORDS.items():
            score = 0
            matched_keywords = []
            
            for category, keywords in dim_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        score += 10
                        matched_keywords.append(keyword)
            
            # 归一化分数
            score = min(score, 100)
            
            # 计算置信度
            confidence = 0.5 + min(len(matched_keywords) / 10, 0.5)
            
            dimensions[dim_name] = {
                "score": score,
                "confidence": confidence,
                "keywords": list(set(matched_keywords)),
                "factors": matched_keywords[:5]
            }
        
        return dimensions
    
    def _calculate_dimension_weights(self, dimensions: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """计算维度权重"""
        total_score = sum(d["score"] for d in dimensions.values())
        
        if total_score == 0:
            # 默认权重
            return {
                "fundamental": 0.30,
                "macro": 0.20,
                "sentiment": 0.15,
                "technical": 0.15,
                "geopolitical": 0.20
            }
        
        weights = {}
        for dim_name, dim_data in dimensions.items():
            weights[dim_name] = dim_data["score"] / total_score
        
        return weights
    
    def _calculate_overall_score(self, sentiment: SentimentResult, dimensions: Dict[str, Dict[str, Any]]) -> float:
        """计算综合得分"""
        # 基于情感和维度的综合评分
        sentiment_score = sentiment.intensity
        if sentiment.overall == Sentiment.NEGATIVE:
            sentiment_score = -sentiment_score
        
        dimension_score = sum(d["score"] for d in dimensions.values()) / len(dimensions)
        
        # 综合计算
        overall = (sentiment_score + dimension_score) / 2
        
        # 归一化到0-100
        return max(0, min(100, overall + 50))
    
    def _generate_trading_signal(self, score: float, sentiment: SentimentResult) -> Optional[str]:
        """生成交易信号"""
        if score >= 70:
            return "强烈买入"
        elif score >= 60:
            return "买入"
        elif score >= 45:
            return "持有"
        elif score >= 30:
            return "减仓"
        else:
            return "卖出"
    
    def _deduplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        """去重实体"""
        seen = set()
        unique_entities = []
        
        for entity in entities:
            key = (entity.text, entity.type, entity.start)
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities
    
    def _extract_product_sentences(self, text: str, product: str) -> str:
        """提取产品相关句子"""
        sentences = re.split(r'[。！？\n]', text)
        product_sentences = []
        
        for sentence in sentences:
            if product in sentence:
                product_sentences.append(sentence)
        
        return "。".join(product_sentences)
    
    def _calculate_event_importance(self, text: str, keyword: str, event_type: str) -> float:
        """计算事件重要性"""
        base_score = 50
        
        # 根据事件类型调整
        if event_type in ["OPEC政策", "地缘冲突", "制裁措施"]:
            base_score += 20
        elif event_type in ["产量变化", "库存数据"]:
            base_score += 15
        
        # 根据文本位置调整（标题更重要）
        if keyword in text[:100]:
            base_score += 10
        
        # 根据程度词调整
        intensity_words = ["大幅", "剧烈", "严重", "重大", "显著"]
        for word in intensity_words:
            if word in text:
                base_score += 5
        
        return min(base_score, 100)
    
    async def _analyze_event_sentiment(self, text: str, keyword: str) -> Sentiment:
        """分析事件情感"""
        # 提取关键词周围文本
        idx = text.find(keyword)
        if idx == -1:
            return Sentiment.NEUTRAL
        
        context = text[max(0, idx-50):min(len(text), idx+50)]
        
        # 分析上下文情感
        positive_count = sum(context.count(w) for w in ["增长", "上涨", "增加", "利好", "积极"])
        negative_count = sum(context.count(w) for w in ["下降", "下跌", "减少", "利空", "消极"])
        
        if positive_count > negative_count:
            return Sentiment.POSITIVE
        elif negative_count > positive_count:
            return Sentiment.NEGATIVE
        else:
            return Sentiment.NEUTRAL
    
    async def close(self):
        """关闭服务"""
        logger.info("NLP分析服务已关闭")
