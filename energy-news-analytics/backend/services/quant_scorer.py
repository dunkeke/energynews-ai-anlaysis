"""
量化评分服务 - 多维度评分模型
"""
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import deque
from loguru import logger

from models.schemas import (
    QuantScore, Rating, Signal, Dimension,
    TrendPrediction, AlertLevel
)

class QuantScorerService:
    """量化评分服务"""
    
    # 品种基础权重配置
    BASE_WEIGHTS = {
        "WTI": {
            "fundamental": 0.30,
            "macro": 0.15,
            "sentiment": 0.20,
            "technical": 0.20,
            "geopolitical": 0.15
        },
        "Brent": {
            "fundamental": 0.30,
            "macro": 0.15,
            "sentiment": 0.20,
            "technical": 0.20,
            "geopolitical": 0.15
        },
        "HH": {
            "fundamental": 0.35,
            "macro": 0.10,
            "sentiment": 0.20,
            "technical": 0.25,
            "geopolitical": 0.10
        },
        "TTF": {
            "fundamental": 0.35,
            "macro": 0.10,
            "sentiment": 0.25,
            "technical": 0.20,
            "geopolitical": 0.10
        },
        "JKM": {
            "fundamental": 0.35,
            "macro": 0.10,
            "sentiment": 0.25,
            "technical": 0.20,
            "geopolitical": 0.10
        },
        "PG": {
            "fundamental": 0.30,
            "macro": 0.15,
            "sentiment": 0.25,
            "technical": 0.20,
            "geopolitical": 0.10
        },
        "CP": {
            "fundamental": 0.35,
            "macro": 0.15,
            "sentiment": 0.20,
            "technical": 0.20,
            "geopolitical": 0.10
        },
        "FEI": {
            "fundamental": 0.30,
            "macro": 0.15,
            "sentiment": 0.25,
            "technical": 0.20,
            "geopolitical": 0.10
        }
    }
    
    # 评分区间定义
    SCORE_RANGES = {
        "strong_bullish": (80, 100, Rating.STRONG_BULLISH, Signal.STRONG_BUY),
        "bullish": (65, 80, Rating.BULLISH, Signal.BUY),
        "mild_bullish": (55, 65, Rating.MILD_BULLISH, Signal.BUY),
        "neutral": (45, 55, Rating.NEUTRAL, Signal.HOLD),
        "mild_bearish": (35, 45, Rating.MILD_BEARISH, Signal.SELL),
        "bearish": (20, 35, Rating.BEARISH, Signal.SELL),
        "strong_bearish": (0, 20, Rating.STRONG_BEARISH, Signal.STRONG_SELL)
    }
    
    def __init__(self):
        self.score_history = {}
        self.initialized = False
    
    async def initialize(self):
        """初始化评分服务"""
        try:
            # 初始化各品种的历史分数缓存
            for commodity in self.BASE_WEIGHTS.keys():
                self.score_history[commodity] = deque(maxlen=100)
            
            self.initialized = True
            logger.info("量化评分服务初始化完成")
        except Exception as e:
            logger.error(f"量化评分服务初始化失败: {e}")
            raise
    
    async def calculate_score(
        self,
        commodity: str,
        nlp_results: List[Any],
        dimensions: Optional[List[Dimension]] = None
    ) -> Dict[str, Any]:
        """
        计算综合评分
        """
        try:
            # 获取基础权重
            weights = self.BASE_WEIGHTS.get(commodity, self.BASE_WEIGHTS["WTI"])
            
            # 计算各维度得分
            dimension_scores = self._calculate_dimension_scores(nlp_results, weights)
            
            # 计算地缘风险调整分
            geo_adjustment = self._calculate_geo_adjustment(nlp_results)
            
            # 计算基础加权得分
            base_score = sum(
                dimension_scores[dim] * weights[dim]
                for dim in ["fundamental", "macro", "sentiment", "technical"]
            )
            
            # 应用地缘风险调整
            adjusted_score = base_score + geo_adjustment
            
            # 确保在有效范围内
            final_score = max(0, min(100, adjusted_score))
            
            # 生成评级和信号
            rating, signal = self._get_rating_and_signal(final_score)
            
            # 计算置信度
            confidence = self._calculate_confidence(nlp_results, dimension_scores)
            
            # 提取关键因子
            key_factors = self._extract_key_factors(nlp_results)
            
            result = {
                "commodity": commodity,
                "timestamp": datetime.now(),
                "composite_score": round(final_score, 2),
                "base_score": round(base_score, 2),
                "geo_adjustment": round(geo_adjustment, 2),
                "rating": rating,
                "signal": signal,
                "confidence": round(confidence, 2),
                "dimensions": dimension_scores,
                "weights": weights,
                "key_factors": key_factors
            }
            
            # 保存到历史记录
            self.score_history[commodity].append({
                "timestamp": datetime.now(),
                "score": final_score,
                "dimensions": dimension_scores
            })
            
            return result
        except Exception as e:
            logger.error(f"计算评分失败: {e}")
            raise
    
    async def get_current_score(
        self,
        commodity: str,
        include_history: bool = True
    ) -> QuantScore:
        """获取当前评分"""
        try:
            # 从数据库获取最新评分
            # 这里简化处理，实际应从数据库查询
            
            # 获取历史数据
            historical_scores = None
            if include_history and commodity in self.score_history:
                historical_scores = list(self.score_history[commodity])
            
            # 计算趋势
            trend_direction, trend_strength = self._calculate_trend(commodity)
            
            # 构造返回对象
            score = QuantScore(
                commodity=commodity,
                timestamp=datetime.now(),
                composite_score=50.0,  # 默认值
                base_score=50.0,
                geo_adjustment=0.0,
                rating=Rating.NEUTRAL,
                signal=Signal.HOLD,
                confidence=0.5,
                dimension_breakdown={},
                weights=self.BASE_WEIGHTS.get(commodity, {}),
                historical_scores=historical_scores,
                trend_direction=trend_direction,
                trend_strength=trend_strength
            )
            
            return score
        except Exception as e:
            logger.error(f"获取当前评分失败: {e}")
            raise
    
    async def compare_commodities(
        self,
        commodities: List[str],
        dimension: Optional[str] = None
    ) -> Dict[str, Any]:
        """多品种对比分析"""
        try:
            comparison = {
                "timestamp": datetime.now(),
                "commodities": [],
                "dimension": dimension,
                "rankings": []
            }
            
            scores = []
            for commodity in commodities:
                score = await self.get_current_score(commodity, include_history=False)
                scores.append({
                    "commodity": commodity,
                    "score": score.composite_score,
                    "rating": score.rating,
                    "signal": score.signal
                })
            
            # 排序
            scores.sort(key=lambda x: x["score"], reverse=True)
            
            comparison["rankings"] = scores
            comparison["average_score"] = round(
                sum(s["score"] for s in scores) / len(scores), 2
            ) if scores else 0
            
            return comparison
        except Exception as e:
            logger.error(f"对比分析失败: {e}")
            raise
    
    async def get_realtime_score(self, commodity: str) -> Dict[str, Any]:
        """获取实时评分（用于仪表盘）"""
        try:
            score = await self.get_current_score(commodity)
            
            # 计算24小时变化
            change_24h = 0
            if commodity in self.score_history and len(self.score_history[commodity]) >= 2:
                recent = self.score_history[commodity][-1]["score"]
                previous = self.score_history[commodity][-2]["score"]
                change_24h = round(recent - previous, 2)
            
            return {
                "commodity": commodity,
                "score": score.composite_score,
                "rating": score.rating.value,
                "signal": score.signal.value,
                "confidence": score.confidence,
                "change_24h": change_24h,
                "trend": score.trend_direction,
                "timestamp": score.timestamp
            }
        except Exception as e:
            logger.error(f"获取实时评分失败: {e}")
            raise
    
    def _calculate_dimension_scores(
        self,
        nlp_results: List[Any],
        weights: Dict[str, float]
    ) -> Dict[str, float]:
        """计算各维度得分"""
        dimension_scores = {
            "fundamental": 50,
            "macro": 50,
            "sentiment": 50,
            "technical": 50,
            "geopolitical": 50
        }
        
        if not nlp_results:
            return dimension_scores
        
        # 汇总各维度的分数
        dim_sums = {dim: [] for dim in dimension_scores.keys()}
        
        for result in nlp_results:
            if hasattr(result, 'dimensions'):
                for dim_name, dim_data in result.dimensions.items():
                    if dim_name in dim_sums and isinstance(dim_data, dict):
                        score = dim_data.get("score", 50)
                        confidence = dim_data.get("confidence", 0.5)
                        # 加权平均
                        dim_sums[dim_name].append(score * confidence)
        
        # 计算平均分
        for dim_name, scores in dim_sums.items():
            if scores:
                dimension_scores[dim_name] = sum(scores) / len(scores)
        
        return dimension_scores
    
    def _calculate_geo_adjustment(self, nlp_results: List[Any]) -> float:
        """计算地缘风险调整分"""
        if not nlp_results:
            return 0
        
        geo_score = 50
        geo_events = []
        
        for result in nlp_results:
            if hasattr(result, 'events'):
                for event in result.events:
                    if hasattr(event, 'type') and "地缘" in event.type or "冲突" in event.type or "制裁" in event.type:
                        importance = getattr(event, 'importance', 50)
                        sentiment = getattr(event, 'sentiment', None)
                        
                        if sentiment and sentiment.value == "positive":
                            geo_score += importance * 0.1
                        elif sentiment and sentiment.value == "negative":
                            geo_score -= importance * 0.1
                        
                        geo_events.append(event)
        
        # 转换为调整分 (-15 到 +15)
        adjustment = (geo_score - 50) / 50 * 15
        
        return round(adjustment, 2)
    
    def _get_rating_and_signal(self, score: float) -> tuple:
        """根据分数获取评级和信号"""
        for range_name, (min_score, max_score, rating, signal) in self.SCORE_RANGES.items():
            if min_score <= score < max_score:
                return rating, signal
        
        # 默认返回中性
        return Rating.NEUTRAL, Signal.HOLD
    
    def _calculate_confidence(
        self,
        nlp_results: List[Any],
        dimension_scores: Dict[str, float]
    ) -> float:
        """计算置信度"""
        if not nlp_results:
            return 0.5
        
        # 基于数据量的置信度
        data_confidence = min(len(nlp_results) / 20, 1.0) * 0.4
        
        # 基于维度分数分布的置信度
        score_variance = np.var(list(dimension_scores.values()))
        consistency_confidence = (1 - min(score_variance / 1000, 1.0)) * 0.3
        
        # 基于NLP结果平均置信度的置信度
        nlp_confidences = []
        for result in nlp_results:
            if hasattr(result, 'sentiment') and hasattr(result.sentiment, 'confidence'):
                nlp_confidences.append(result.sentiment.confidence)
        
        nlp_confidence = sum(nlp_confidences) / len(nlp_confidences) if nlp_confidences else 0.5
        nlp_confidence *= 0.3
        
        total_confidence = data_confidence + consistency_confidence + nlp_confidence
        
        return round(min(total_confidence, 1.0), 2)
    
    def _extract_key_factors(self, nlp_results: List[Any]) -> List[str]:
        """提取关键因子"""
        factors = []
        
        # 统计高频关键词
        keyword_freq = {}
        for result in nlp_results:
            if hasattr(result, 'keywords'):
                for kw in result.keywords:
                    if isinstance(kw, dict):
                        word = kw.get("word", "")
                        weight = kw.get("weight", 0.5)
                        keyword_freq[word] = keyword_freq.get(word, 0) + weight
        
        # 取前5个关键词
        sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
        factors = [kw[0] for kw in sorted_keywords[:5]]
        
        return factors
    
    def _calculate_trend(self, commodity: str) -> tuple:
        """计算趋势方向和强度"""
        if commodity not in self.score_history or len(self.score_history[commodity]) < 3:
            return "stable", 0.0
        
        history = list(self.score_history[commodity])
        recent_scores = [h["score"] for h in history[-5:]]
        
        if len(recent_scores) < 2:
            return "stable", 0.0
        
        # 计算变化
        changes = [recent_scores[i+1] - recent_scores[i] for i in range(len(recent_scores)-1)]
        avg_change = sum(changes) / len(changes)
        
        # 判断方向
        if avg_change > 3:
            direction = "up"
        elif avg_change < -3:
            direction = "down"
        else:
            direction = "stable"
        
        # 计算强度
        strength = min(abs(avg_change) / 5, 1.0)
        
        return direction, round(strength, 2)
    
    async def predict_trend(
        self,
        commodity: str,
        horizon_days: int = 5
    ) -> TrendPrediction:
        """预测未来趋势"""
        try:
            if commodity not in self.score_history:
                return TrendPrediction(
                    horizon_days=horizon_days,
                    direction="unknown",
                    probability=0.5,
                    confidence="low"
                )
            
            history = list(self.score_history[commodity])
            if len(history) < 5:
                return TrendPrediction(
                    horizon_days=horizon_days,
                    direction="unknown",
                    probability=0.5,
                    confidence="low"
                )
            
            # 基于历史趋势预测
            recent_scores = [h["score"] for h in history[-10:]]
            score_change = recent_scores[-1] - recent_scores[0]
            
            # 计算动量
            momentum = score_change / len(recent_scores)
            
            # 预测方向
            if momentum > 2:
                direction = "up"
                probability = min(0.5 + momentum / 10, 0.9)
            elif momentum < -2:
                direction = "down"
                probability = min(0.5 + abs(momentum) / 10, 0.9)
            else:
                direction = "stable"
                probability = 0.5
            
            # 置信度
            confidence = "high" if len(history) > 20 else "medium" if len(history) > 10 else "low"
            
            return TrendPrediction(
                horizon_days=horizon_days,
                direction=direction,
                probability=round(probability, 2),
                confidence=confidence
            )
        except Exception as e:
            logger.error(f"趋势预测失败: {e}")
            return TrendPrediction(
                horizon_days=horizon_days,
                direction="unknown",
                probability=0.5,
                confidence="low"
            )
    
    async def close(self):
        """关闭服务"""
        logger.info("量化评分服务已关闭")
