"""
能源化工新闻分析软件 - 量化评分模型实现
================================================
本模块包含完整的评分模型实现，包括：
1. 多维度评分计算
2. 综合评分模型
3. 趋势预测模型
4. 风险预警系统
5. 动态权重调整
"""

import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


class Rating(Enum):
    """评级枚举"""
    STRONG_BULLISH = ("强烈看涨", 80, 100, "#00C853")
    BULLISH = ("看涨", 65, 80, "#69F0AE")
    MILD_BULLISH = ("偏看涨", 55, 65, "#B2FF59")
    NEUTRAL = ("中性", 45, 55, "#FFD54F")
    MILD_BEARISH = ("偏看跌", 35, 45, "#FF8A65")
    BEARISH = ("看跌", 20, 35, "#FF5252")
    STRONG_BEARISH = ("强烈看跌", 0, 20, "#D32F2F")
    
    def __init__(self, label: str, min_score: int, max_score: int, color: str):
        self.label = label
        self.min_score = min_score
        self.max_score = max_score
        self.color = color
    
    @classmethod
    def from_score(cls, score: float) -> "Rating":
        """根据分数获取评级"""
        for rating in cls:
            if rating.min_score <= score <= rating.max_score:
                return rating
        return cls.NEUTRAL


@dataclass
class DimensionScore:
    """维度评分数据结构"""
    fundamental: float = 50.0
    macro: float = 50.0
    sentiment: float = 50.0
    technical: float = 50.0
    
    def to_dict(self) -> Dict:
        return {
            'fundamental': self.fundamental,
            'macro': self.macro,
            'sentiment': self.sentiment,
            'technical': self.technical
        }


@dataclass
class GeopoliticalEvent:
    """地缘风险事件"""
    event_type: str
    description: str
    severity: int  # 1-5
    probability: float  # 0-1
    duration_factor: float  # 短期1.0, 中期0.8, 长期0.6
    impact_description: str = ""


class FundamentalScorer:
    """基本面评分器"""
    
    SUB_WEIGHTS = {
        'supply_demand': 0.30,
        'inventory': 0.25,
        'capacity': 0.20,
        'trade': 0.15,
        'seasonal': 0.10
    }
    
    def calculate(self, market_data: Dict) -> float:
        """
        计算基本面评分
        
        Args:
            market_data: 包含库存、产量、开工率等数据
        
        Returns:
            float: 0-100的评分
        """
        scores = {}
        
        # 1. 供需平衡评分 (基于库存变化)
        if 'inventory_change' in market_data and 'historical_std' in market_data:
            inv_change = market_data['inventory_change']
            hist_std = market_data['historical_std']
            scores['supply_demand'] = max(0, min(100, 50 - (inv_change / (hist_std + 1e-6)) * 10))
        else:
            scores['supply_demand'] = 50
        
        # 2. 库存水平评分
        if 'inventory_level' in market_data and 'historical_mean' in market_data:
            inv_level = market_data['inventory_level']
            hist_mean = market_data['historical_mean']
            hist_std = market_data.get('historical_std', 1)
            deviation = abs(inv_level - hist_mean) / (hist_std + 1e-6)
            scores['inventory'] = max(0, min(100, 50 - deviation * 10))
        else:
            scores['inventory'] = 50
        
        # 3. 产能利用率评分
        if 'utilization_rate' in market_data:
            util = market_data['utilization_rate']
            # 产能利用率80-95%为理想区间
            if 80 <= util <= 95:
                scores['capacity'] = 70 + (util - 80) / 15 * 30
            elif util < 80:
                scores['capacity'] = 40 + util / 80 * 30
            else:
                scores['capacity'] = max(0, 100 - (util - 95) * 5)
        else:
            scores['capacity'] = 50
        
        # 4. 进出口数据评分
        if 'trade_balance' in market_data:
            trade = market_data['trade_balance']
            scores['trade'] = max(0, min(100, 50 + trade * 10))
        else:
            scores['trade'] = 50
        
        # 5. 季节性因素评分
        if 'seasonal_factor' in market_data:
            seasonal = market_data['seasonal_factor']
            scores['seasonal'] = max(0, min(100, 50 + seasonal * 20))
        else:
            scores['seasonal'] = 50
        
        # 加权计算
        total_score = sum(scores[k] * self.SUB_WEIGHTS[k] for k in scores)
        return round(total_score, 2)


class MacroScorer:
    """宏观面评分器"""
    
    SUB_WEIGHTS = {
        'dollar': 0.25,
        'interest_rate': 0.25,
        'inflation': 0.20,
        'economy': 0.20,
        'currency': 0.10
    }
    
    def calculate(self, macro_data: Dict) -> float:
        """计算宏观面评分"""
        scores = {}
        
        # 1. 美元指数影响 (负相关)
        if 'dxy_change' in macro_data:
            dxy_change = macro_data['dxy_change']
            sensitivity = macro_data.get('dollar_sensitivity', 1.0)
            scores['dollar'] = max(0, min(100, 50 - dxy_change * 10 * sensitivity))
        else:
            scores['dollar'] = 50
        
        # 2. 利率政策评分
        if 'interest_policy' in macro_data:
            policy = macro_data['interest_policy']
            if policy == 'cut':
                scores['interest_rate'] = 80
            elif policy == 'hike':
                scores['interest_rate'] = 20
            else:
                scores['interest_rate'] = 50
        else:
            scores['interest_rate'] = 50
        
        # 3. 通胀预期评分
        if 'inflation_expectation' in macro_data:
            inflation = macro_data['inflation_expectation']
            scores['inflation'] = max(0, min(100, 50 + inflation * 20))
        else:
            scores['inflation'] = 50
        
        # 4. 经济增长评分
        if 'pmi' in macro_data:
            pmi = macro_data['pmi']
            scores['economy'] = max(0, min(100, pmi))
        elif 'gdp_growth' in macro_data:
            gdp = macro_data['gdp_growth']
            scores['economy'] = max(0, min(100, 50 + gdp * 10))
        else:
            scores['economy'] = 50
        
        # 5. 汇率波动评分
        if 'currency_volatility' in macro_data:
            vol = macro_data['currency_volatility']
            scores['currency'] = max(0, min(100, 100 - vol * 100))
        else:
            scores['currency'] = 50
        
        total_score = sum(scores[k] * self.SUB_WEIGHTS[k] for k in scores)
        return round(total_score, 2)


class SentimentScorer:
    """情绪面评分器"""
    
    SUB_WEIGHTS = {
        'news_sentiment': 0.35,
        'market_sentiment': 0.25,
        'position': 0.25,
        'volatility_sentiment': 0.15
    }
    
    def calculate(self, news_items: List[Dict], position_data: Dict = None) -> float:
        """计算情绪面评分"""
        scores = {}
        
        # 1. 新闻情感评分 (NLP)
        if news_items:
            sentiment_weights = {'positive': 1.0, 'neutral': 0.5, 'negative': 0.0}
            weighted_sum = sum(
                item.get('confidence', 0.5) * sentiment_weights.get(item.get('sentiment', 'neutral'), 0.5)
                for item in news_items
            )
            avg_sentiment = weighted_sum / len(news_items)
            scores['news_sentiment'] = avg_sentiment * 100
        else:
            scores['news_sentiment'] = 50
        
        # 2. 市场情绪指标
        scores['market_sentiment'] = 50  # 默认值
        
        # 3. 持仓数据评分
        if position_data and 'net_position' in position_data and 'total_position' in position_data:
            net_pos = position_data['net_position']
            total_pos = position_data['total_position']
            if total_pos > 0:
                position_ratio = net_pos / total_pos
                scores['position'] = max(0, min(100, 50 + position_ratio * 50))
            else:
                scores['position'] = 50
        else:
            scores['position'] = 50
        
        # 4. 波动率情绪 (VIX等)
        if position_data and 'vix' in position_data:
            vix = position_data['vix']
            # VIX越高，恐慌情绪越强，评分越低
            scores['volatility_sentiment'] = max(0, min(100, 100 - vix * 5))
        else:
            scores['volatility_sentiment'] = 50
        
        total_score = sum(scores[k] * self.SUB_WEIGHTS[k] for k in scores)
        return round(total_score, 2)


class TechnicalScorer:
    """技术面评分器"""
    
    SUB_WEIGHTS = {
        'trend': 0.30,
        'momentum': 0.25,
        'levels': 0.25,
        'pattern': 0.20
    }
    
    def calculate(self, price_data: List[float]) -> Tuple[float, Dict]:
        """计算技术面评分"""
        scores = {}
        details = {}
        
        if len(price_data) < 20:
            return 50.0, {'error': 'Insufficient data'}
        
        prices = np.array(price_data)
        
        # 1. 趋势评分
        ma5 = np.mean(prices[-5:])
        ma10 = np.mean(prices[-10:])
        ma20 = np.mean(prices[-20:])
        
        # 均线多头排列
        if ma5 > ma10 > ma20:
            trend_score = 70 + min(30, (ma5 - ma20) / ma20 * 500)
        # 均线空头排列
        elif ma5 < ma10 < ma20:
            trend_score = max(0, 30 - (ma20 - ma5) / ma20 * 500)
        else:
            trend_score = 50
        
        scores['trend'] = trend_score
        details['ma5'] = ma5
        details['ma10'] = ma10
        details['ma20'] = ma20
        
        # 2. 动量评分 (RSI简化版)
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-14:]) if len(gains) >= 14 else np.mean(gains)
        avg_loss = np.mean(losses[-14:]) if len(losses) >= 14 else np.mean(losses)
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        # RSI评分 (50为中性，>70超买，<30超卖)
        if rsi > 70:
            momentum_score = max(0, 100 - (rsi - 70) * 3)  # 超买扣分
        elif rsi < 30:
            momentum_score = min(100, (30 - rsi) * 3)  # 超卖加分
        else:
            momentum_score = 40 + (rsi - 30) / 40 * 20  # 正常区间
        
        scores['momentum'] = momentum_score
        details['rsi'] = rsi
        
        # 3. 支撑阻力评分 (简化)
        recent_high = np.max(prices[-20:])
        recent_low = np.min(prices[-20:])
        current = prices[-1]
        
        # 距离支撑/阻力的位置
        range_size = recent_high - recent_low
        if range_size > 0:
            position_in_range = (current - recent_low) / range_size
            # 接近支撑(低位)加分，接近阻力(高位)扣分
            levels_score = 100 - position_in_range * 100
        else:
            levels_score = 50
        
        scores['levels'] = levels_score
        details['support'] = recent_low
        details['resistance'] = recent_high
        
        # 4. 形态评分 (简化)
        scores['pattern'] = 50  # 需要更复杂的形态识别算法
        
        total_score = sum(scores[k] * self.SUB_WEIGHTS[k] for k in scores)
        details['sub_scores'] = scores
        
        return round(total_score, 2), details


class GeopoliticalRiskScorer:
    """地缘风险评分器"""
    
    EVENT_WEIGHTS = {
        'conflict': 0.30,
        'sanction': 0.25,
        'transport': 0.20,
        'policy': 0.15,
        'natural_disaster': 0.10
    }
    
    def calculate(self, events: List[GeopoliticalEvent]) -> float:
        """
        计算地缘风险评分
        
        Returns:
            float: -15 到 +15 的风险调整分
        """
        risk_score = 0
        
        for event in events:
            event_type_weight = self.EVENT_WEIGHTS.get(event.event_type, 0.10)
            
            # 计算单个事件风险
            event_risk = (
                event.severity * 
                event.probability * 
                event.duration_factor * 
                event_type_weight * 
                10  # 放大系数
            )
            
            risk_score += event_risk
        
        # 限制在±15范围内
        return round(max(-15, min(15, risk_score)), 2)


class CompositeScoringModel:
    """
    能化品种综合评分模型
    """
    
    PRODUCT_WEIGHTS = {
        'crude_wti': {
            'fundamental': 0.30, 'macro': 0.15, 'sentiment': 0.20,
            'technical': 0.20, 'geopolitical': 0.15
        },
        'crude_brent': {
            'fundamental': 0.30, 'macro': 0.15, 'sentiment': 0.20,
            'technical': 0.20, 'geopolitical': 0.15
        },
        'gas_hh': {
            'fundamental': 0.35, 'macro': 0.10, 'sentiment': 0.20,
            'technical': 0.25, 'geopolitical': 0.10
        },
        'gas_jkm': {
            'fundamental': 0.35, 'macro': 0.10, 'sentiment': 0.25,
            'technical': 0.20, 'geopolitical': 0.10
        },
        'gas_ttf': {
            'fundamental': 0.35, 'macro': 0.10, 'sentiment': 0.25,
            'technical': 0.20, 'geopolitical': 0.10
        },
        'lpg_pg': {
            'fundamental': 0.30, 'macro': 0.15, 'sentiment': 0.25,
            'technical': 0.20, 'geopolitical': 0.10
        },
        'lpg_cp': {
            'fundamental': 0.35, 'macro': 0.15, 'sentiment': 0.20,
            'technical': 0.20, 'geopolitical': 0.10
        },
        'product_oil': {
            'fundamental': 0.35, 'macro': 0.15, 'sentiment': 0.20,
            'technical': 0.20, 'geopolitical': 0.10
        }
    }
    
    def __init__(self, product_type: str):
        self.product = product_type
        self.weights = self.PRODUCT_WEIGHTS.get(product_type, self.PRODUCT_WEIGHTS['crude_wti'])
        
        # 初始化各维度评分器
        self.fundamental_scorer = FundamentalScorer()
        self.macro_scorer = MacroScorer()
        self.sentiment_scorer = SentimentScorer()
        self.technical_scorer = TechnicalScorer()
        self.geo_scorer = GeopoliticalRiskScorer()
    
    def calculate_all_dimensions(self, data: Dict) -> Dict:
        """计算所有维度评分"""
        return {
            'fundamental': self.fundamental_scorer.calculate(data.get('market', {})),
            'macro': self.macro_scorer.calculate(data.get('macro', {})),
            'sentiment': self.sentiment_scorer.calculate(
                data.get('news', []), 
                data.get('position', {})
            ),
            'technical': self.technical_scorer.calculate(data.get('prices', []))[0]
        }
    
    def calculate_composite_score(self, dimension_scores: Dict, geo_risk_score: float) -> Dict:
        """
        计算综合评分
        
        Args:
            dimension_scores: 各维度得分字典
            geo_risk_score: 地缘风险调整分 (-15 to +15)
        
        Returns:
            dict: 完整的评分结果
        """
        # 基础加权得分
        base_score = (
            dimension_scores['fundamental'] * self.weights['fundamental'] +
            dimension_scores['macro'] * self.weights['macro'] +
            dimension_scores['sentiment'] * self.weights['sentiment'] +
            dimension_scores['technical'] * self.weights['technical']
        )
        
        # 地缘风险调整
        adjusted_score = base_score + geo_risk_score
        
        # 确保在有效范围内
        final_score = max(0, min(100, adjusted_score))
        
        # 获取评级
        rating = Rating.from_score(final_score)
        
        return {
            'composite_score': round(final_score, 2),
            'base_score': round(base_score, 2),
            'geo_adjustment': round(geo_risk_score, 2),
            'rating': rating.label,
            'rating_color': rating.color,
            'dimension_breakdown': dimension_scores,
            'weights': self.weights,
            'timestamp': datetime.now().isoformat()
        }
    
    def full_analysis(self, data: Dict, geo_events: List[GeopoliticalEvent]) -> Dict:
        """执行完整分析"""
        # 1. 计算各维度评分
        dimension_scores = self.calculate_all_dimensions(data)
        
        # 2. 计算地缘风险
        geo_risk = self.geo_scorer.calculate(geo_events)
        
        # 3. 计算综合评分
        result = self.calculate_composite_score(dimension_scores, geo_risk)
        
        # 4. 添加地缘风险详情
        result['geo_risk_events'] = [
            {
                'type': e.event_type,
                'description': e.description,
                'severity': e.severity,
                'impact': e.impact_description
            }
            for e in geo_events
        ]
        
        return result


class DynamicWeightAdjuster:
    """动态权重调整器"""
    
    def __init__(self, base_weights: Dict):
        self.base_weights = base_weights
        self.adjustment_history = []
    
    def adjust_weights(self, market_context: Dict, event_signals: Dict) -> Dict:
        """
        根据市场情境动态调整权重
        """
        adjusted_weights = self.base_weights.copy()
        adjustments = {}
        
        # 1. 地缘事件调整
        if event_signals.get('geopolitical_event'):
            adjustments['geopolitical'] = 0.05
            adjustments['fundamental'] = -0.03
            adjustments['sentiment'] = -0.02
        
        # 2. 重大数据发布调整
        if event_signals.get('major_data_release'):
            adjustments['fundamental'] = 0.05
            adjustments['macro'] = 0.03
            adjustments['technical'] = -0.08
        
        # 3. 央行政策会议调整
        if event_signals.get('central_bank_meeting'):
            adjustments['macro'] = 0.08
            adjustments['sentiment'] = 0.02
            adjustments['fundamental'] = -0.10
        
        # 4. 市场波动率调整
        volatility = market_context.get('volatility', 0)
        if volatility > 0.30:
            adjustments['technical'] = 0.05
            adjustments['sentiment'] = 0.03
            adjustments['fundamental'] = -0.08
        
        # 5. 持仓报告发布调整
        if event_signals.get('cot_report'):
            adjustments['sentiment'] = 0.05
            adjustments['technical'] = -0.05
        
        # 应用调整
        for dimension, adjustment in adjustments.items():
            if dimension in adjusted_weights:
                adjusted_weights[dimension] += adjustment
        
        # 归一化权重
        total = sum(adjusted_weights.values())
        adjusted_weights = {k: v/total for k, v in adjusted_weights.items()}
        
        # 记录调整
        self.adjustment_history.append({
            'timestamp': datetime.now().isoformat(),
            'context': market_context,
            'signals': event_signals,
            'adjustments': adjustments,
            'final_weights': adjusted_weights
        })
        
        return adjusted_weights


class RiskAlertSystem:
    """风险预警系统"""
    
    ALERT_THRESHOLDS = {
        'composite_change': 15,
        'composite_shock': 20,
        'dimension_change': 15,
        'geo_risk': 10,
        'consecutive_periods': 3,
        'consecutive_change': 10
    }
    
    def check_alerts(self, current_data: Dict, historical_data: List[Dict]) -> List[Dict]:
        """检查预警条件"""
        alerts = []
        
        # 1. 综合评分突变预警
        if len(historical_data) >= 2:
            prev_score = historical_data[-1].get('composite_score', 50)
            curr_score = current_data.get('composite_score', 50)
            score_change = abs(curr_score - prev_score)
            
            if score_change >= self.ALERT_THRESHOLDS['composite_shock']:
                alerts.append({
                    'level': 'red',
                    'type': 'composite_shock',
                    'message': f'综合评分剧烈变化: {prev_score:.1f} → {curr_score:.1f}',
                    'timestamp': datetime.now().isoformat()
                })
            elif score_change >= self.ALERT_THRESHOLDS['composite_change']:
                alerts.append({
                    'level': 'orange',
                    'type': 'composite_significant_change',
                    'message': f'综合评分显著变化: {prev_score:.1f} → {curr_score:.1f}',
                    'timestamp': datetime.now().isoformat()
                })
        
        # 2. 地缘风险预警
        geo_risk = current_data.get('geo_risk_score', 0)
        if abs(geo_risk) >= self.ALERT_THRESHOLDS['geo_risk']:
            alerts.append({
                'level': 'red',
                'type': 'geopolitical_risk',
                'message': f'地缘风险急剧上升: {geo_risk:.1f}',
                'timestamp': datetime.now().isoformat()
            })
        
        # 3. 单维度突变预警
        for dimension in ['fundamental', 'macro', 'sentiment', 'technical']:
            if len(historical_data) >= 2:
                prev_dim = historical_data[-1].get('dimensions', {}).get(dimension, 50)
                curr_dim = current_data.get('dimensions', {}).get(dimension, 50)
                dim_change = abs(curr_dim - prev_dim)
                
                if dim_change >= self.ALERT_THRESHOLDS['dimension_change']:
                    alerts.append({
                        'level': 'orange',
                        'type': f'{dimension}_significant_change',
                        'message': f'{dimension}评分显著变化: {prev_dim:.1f} → {curr_dim:.1f}',
                        'timestamp': datetime.now().isoformat()
                    })
        
        # 4. 连续趋势预警
        if len(historical_data) >= 3:
            recent_scores = [d.get('composite_score', 50) for d in historical_data[-3:]]
            changes = [recent_scores[i+1] - recent_scores[i] for i in range(2)]
            
            if all(c > self.ALERT_THRESHOLDS['consecutive_change'] for c in changes):
                alerts.append({
                    'level': 'yellow',
                    'type': 'consecutive_up_trend',
                    'message': '综合评分连续上升，趋势可能反转',
                    'timestamp': datetime.now().isoformat()
                })
            elif all(c < -self.ALERT_THRESHOLDS['consecutive_change'] for c in changes):
                alerts.append({
                    'level': 'yellow',
                    'type': 'consecutive_down_trend',
                    'message': '综合评分连续下降，趋势可能反转',
                    'timestamp': datetime.now().isoformat()
                })
        
        return alerts


class TrendPredictionModel:
    """趋势预测模型"""
    
    def __init__(self):
        self.prediction_horizons = [1, 3, 5, 10]
    
    def predict_trend(self, historical_scores: List[float], current_price: float) -> Dict:
        """预测未来价格趋势"""
        predictions = {}
        
        for horizon in self.prediction_horizons:
            # 基于评分动量预测
            score_momentum = self._calculate_score_momentum(historical_scores, horizon)
            
            # 简化预测逻辑
            if score_momentum['direction'] == 'up':
                direction = 'up'
                probability = 0.55 + min(0.3, score_momentum['strength'] * 0.05)
                confidence = 'high' if score_momentum['strength'] > 2 else 'medium'
            elif score_momentum['direction'] == 'down':
                direction = 'down'
                probability = 0.55 + min(0.3, score_momentum['strength'] * 0.05)
                confidence = 'high' if score_momentum['strength'] > 2 else 'medium'
            else:
                direction = 'neutral'
                probability = 0.5
                confidence = 'low'
            
            # 计算目标区间
            volatility = 0.02 * horizon  # 假设2%日波动率
            if direction == 'up':
                target_low = current_price * (1 + 0.01 * horizon)
                target_high = current_price * (1 + volatility)
            elif direction == 'down':
                target_low = current_price * (1 - volatility)
                target_high = current_price * (1 - 0.01 * horizon)
            else:
                target_low = current_price * (1 - volatility/2)
                target_high = current_price * (1 + volatility/2)
            
            predictions[f'{horizon}d'] = {
                'direction': direction,
                'probability': round(min(probability, 0.9), 2),
                'confidence': confidence,
                'target_range': [round(target_low, 2), round(target_high, 2)]
            }
        
        return predictions
    
    def _calculate_score_momentum(self, scores: List[float], period: int) -> Dict:
        """计算评分动量"""
        if len(scores) < period:
            return {'direction': 'neutral', 'strength': 0, 'score_change': 0}
        
        recent_scores = scores[-period:]
        score_change = recent_scores[-1] - recent_scores[0]
        score_volatility = np.std(recent_scores) if len(recent_scores) > 1 else 1
        
        momentum_strength = abs(score_change) / (score_volatility + 1e-6)
        
        if score_change > 5:
            direction = 'up'
        elif score_change < -5:
            direction = 'down'
        else:
            direction = 'neutral'
        
        return {
            'direction': direction,
            'strength': min(momentum_strength, 5),
            'score_change': score_change
        }


# ==================== 使用示例 ====================

def demo():
    """演示如何使用评分模型"""
    
    # 1. 创建评分模型
    model = CompositeScoringModel('crude_wti')
    
    # 2. 准备数据
    data = {
        'market': {
            'inventory_change': -5.0,  # 库存减少500万桶
            'inventory_level': 420.0,
            'historical_mean': 450.0,
            'historical_std': 20.0,
            'utilization_rate': 92.5
        },
        'macro': {
            'dxy_change': -0.5,
            'interest_policy': 'neutral',
            'pmi': 52.0
        },
        'news': [
            {'sentiment': 'positive', 'confidence': 0.8},
            {'sentiment': 'positive', 'confidence': 0.7},
            {'sentiment': 'neutral', 'confidence': 0.6}
        ],
        'position': {
            'net_position': 150000,
            'total_position': 500000,
            'vix': 18.0
        },
        'prices': [72.0, 72.5, 73.0, 73.5, 74.0, 74.5, 75.0, 75.5, 76.0, 76.5,
                   76.0, 76.5, 77.0, 77.5, 78.0, 78.5, 79.0, 79.5, 80.0, 80.5]
    }
    
    # 3. 创建地缘风险事件
    geo_events = [
        GeopoliticalEvent(
            event_type='conflict',
            description='中东地区紧张局势升级',
            severity=4,
            probability=0.7,
            duration_factor=0.8,
            impact_description='可能导致供应中断'
        )
    ]
    
    # 4. 执行完整分析
    result = model.full_analysis(data, geo_events)
    
    print("=" * 60)
    print("能源化工评分模型 - 分析结果")
    print("=" * 60)
    print(f"\n品种: WTI原油")
    print(f"综合评分: {result['composite_score']}")
    print(f"基础评分: {result['base_score']}")
    print(f"地缘调整: {result['geo_adjustment']}")
    print(f"评级: {result['rating']}")
    print(f"\n各维度评分:")
    for dim, score in result['dimension_breakdown'].items():
        print(f"  - {dim}: {score}")
    print(f"\n地缘风险事件:")
    for event in result['geo_risk_events']:
        print(f"  - {event['description']} (严重度: {event['severity']})")
    
    # 5. 趋势预测
    predictor = TrendPredictionModel()
    historical_scores = [60, 62, 65, 68, 70, 72, 73, 74, 75, result['composite_score']]
    predictions = predictor.predict_trend(historical_scores, 80.5)
    
    print(f"\n趋势预测:")
    for horizon, pred in predictions.items():
        print(f"  - {horizon}: {pred['direction']} (概率: {pred['probability']}, 置信度: {pred['confidence']})")
        print(f"    目标区间: {pred['target_range']}")
    
    # 6. 预警检查
    alert_system = RiskAlertSystem()
    historical_data = [
        {'composite_score': 60, 'dimensions': {'fundamental': 55, 'macro': 60, 'sentiment': 58, 'technical': 62}},
        {'composite_score': 65, 'dimensions': {'fundamental': 60, 'macro': 60, 'sentiment': 62, 'technical': 65}},
        {'composite_score': 70, 'dimensions': {'fundamental': 68, 'macro': 60, 'sentiment': 68, 'technical': 70}}
    ]
    current = {
        'composite_score': result['composite_score'],
        'geo_risk_score': result['geo_adjustment'],
        'dimensions': result['dimension_breakdown']
    }
    alerts = alert_system.check_alerts(current, historical_data)
    
    if alerts:
        print(f"\n预警信息:")
        for alert in alerts:
            print(f"  - [{alert['level'].upper()}] {alert['message']}")
    else:
        print(f"\n暂无预警")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    demo()
