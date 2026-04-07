# 能源化工新闻分析软件 - 量化分析与可视化方案

## 目录
1. [量化分析模型设计](#1-量化分析模型设计)
2. [评分权重体系](#2-评分权重体系)
3. [可视化展示方案](#3-可视化展示方案)
4. [报告输出格式](#4-报告输出格式)
5. [推荐技术栈](#5-推荐技术栈)

---

## 1. 量化分析模型设计

### 1.1 多维度评分体系架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    综合评分模型 (Composite Score Model)            │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ 基本面评分 │  │ 宏观面评分 │  │ 情绪面评分 │  │ 技术面评分 │        │
│  │  (F) 25% │  │  (M) 20% │  │  (S) 25% │  │  (T) 20% │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
│       │             │             │             │               │
│       └─────────────┴─────────────┴─────────────┘               │
│                         │                                       │
│                    ┌────┴────┐                                  │
│                    │ 加权求和 │                                  │
│                    └────┬────┘                                  │
│                         │                                       │
│  ┌──────────────────────┴──────────────────────┐               │
│  │              综合评分 (0-100)                │               │
│  │         + 地缘风险调整系数 (±15)              │               │
│  └─────────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 各维度评分模型详解

#### 1.2.1 基本面评分模型 (Fundamental Score)

**评分维度构成：**

| 子维度 | 权重 | 数据来源 | 评分方法 |
|--------|------|----------|----------|
| 供需平衡 | 30% | 库存数据、产量报告 | 库存变化率评分 |
| 库存水平 | 25% | EIA/API/IEA报告 | 偏离度评分 |
| 产能利用率 | 20% | 炼厂开工率 | 区间评分 |
| 进出口数据 | 15% | 海关数据 | 同比环比分析 |
| 季节性因素 | 10% | 历史同期对比 | 偏离度评分 |

**计算公式：**
```
F_score = Σ(子维度得分 × 子维度权重)

其中：
- 库存变化率评分 = 50 - (当前库存变化率 / 历史标准差) × 10
- 偏离度评分 = 50 - |(当前值 - 历史均值)| / 历史标准差 × 10
- 区间评分 = 根据预设区间映射到0-100分
```

**评分区间定义：**
```python
fundamental_score_ranges = {
    "极强": (80, 100),   # 供不应求，库存极低
    "偏强": (60, 80),    # 供需偏紧
    "中性": (40, 60),    # 供需平衡
    "偏弱": (20, 40),    # 供需偏松
    "极弱": (0, 20)      # 供过于求，库存高企
}
```

#### 1.2.2 宏观面评分模型 (Macro Score)

**评分维度构成：**

| 子维度 | 权重 | 数据来源 | 评分方法 |
|--------|------|----------|----------|
| 美元指数 | 25% | DXY指数 | 负相关评分 |
| 利率政策 | 25% | 美联储/央行政策 | 事件驱动评分 |
| 通胀预期 | 20% | CPI/PPI/breakeven | 趋势评分 |
| 经济增长 | 20% | GDP/PMI数据 | 综合评分 |
| 汇率波动 | 10% | 主要货币对 | 波动率评分 |

**计算公式：**
```
M_score = Σ(子维度得分 × 子维度权重)

美元影响评分 = 50 - (美元指数变化率 × 敏感系数)
利率评分 = 降息利好(70-100) / 加息利空(0-30) / 中性(40-60)
```

#### 1.2.3 情绪面评分模型 (Sentiment Score)

**评分维度构成：**

| 子维度 | 权重 | 数据来源 | 评分方法 |
|--------|------|----------|----------|
| 新闻情感 | 35% | NLP情感分析 | 情感极性得分 |
| 市场情绪指标 | 25% | 调查/指数 | 直接映射 |
| 持仓数据 | 25% | CFTC/交易所 | 净持仓分析 |
| 波动率情绪 | 15% | VIX/OVX等 | 逆序评分 |

**NLP情感分析评分：**
```python
def calculate_sentiment_score(news_items):
    sentiment_weights = {'positive': 1.0, 'neutral': 0.5, 'negative': 0.0}
    weighted_score = sum(
        item['confidence'] * sentiment_weights[item['sentiment']]
        for item in news_items
    ) / len(news_items)
    return weighted_score * 100
```

**持仓情绪评分：**
```
持仓评分 = 50 + (净多持仓变化 / 总持仓) × 100
- 净多增加 → 看涨情绪增强
- 净多减少 → 看跌情绪增强
```

#### 1.2.4 技术面评分模型 (Technical Score)

**评分维度构成：**

| 子维度 | 权重 | 技术指标 | 评分方法 |
|--------|------|----------|----------|
| 趋势方向 | 30% | MA/ADX | 趋势强度评分 |
| 动量指标 | 25% | RSI/MACD | 超买超卖评分 |
| 支撑阻力 | 25% | 关键价位 | 位置评分 |
| 形态识别 | 20% | 图表形态 | 形态确认评分 |

**技术面综合评分算法：**
```python
def calculate_technical_score(price_data):
    scores = {}
    
    # 趋势评分 (0-100)
    ma_trend = calculate_ma_trend(price_data)  # 均线排列
    adx_strength = calculate_adx(price_data)   # 趋势强度
    scores['trend'] = (ma_trend * 0.6 + adx_strength * 0.4)
    
    # 动量评分 (0-100)
    rsi_score = calculate_rsi_score(price_data)  # RSI位置
    macd_score = calculate_macd_score(price_data)  # MACD信号
    scores['momentum'] = (rsi_score * 0.5 + macd_score * 0.5)
    
    # 支撑阻力评分
    sr_score = calculate_support_resistance(price_data)
    scores['levels'] = sr_score
    
    # 形态评分
    pattern_score = detect_patterns(price_data)
    scores['pattern'] = pattern_score
    
    # 加权综合
    weights = {'trend': 0.30, 'momentum': 0.25, 'levels': 0.25, 'pattern': 0.20}
    total_score = sum(scores[k] * weights[k] for k in scores)
    
    return total_score, scores
```

#### 1.2.5 地缘风险评分模型 (Geopolitical Risk Score)

**风险事件分类与权重：**

| 风险类型 | 权重 | 影响程度 | 持续时间 |
|----------|------|----------|----------|
| 产油国冲突 | 30% | 极高 | 短期-中期 |
| 制裁政策 | 25% | 高 | 中期-长期 |
| 运输通道 | 20% | 高 | 短期 |
| 政策变动 | 15% | 中 | 中期 |
| 自然灾害 | 10% | 中 | 短期 |

**风险评分算法：**
```python
def calculate_geopolitical_risk(events):
    """
    地缘风险评分 (-15 到 +15)
    正值表示风险溢价上升（利好价格）
    负值表示风险缓解（利空价格）
    """
    risk_score = 0
    
    for event in events:
        base_impact = event['severity']  # 1-5
        probability = event['probability']  # 0-1
        duration_factor = event['duration_factor']  # 短期1.0, 中期0.8, 长期0.6
        
        event_risk = base_impact * probability * duration_factor * 3
        risk_score += event_risk
    
    # 限制在±15范围内
    return max(-15, min(15, risk_score))
```

### 1.3 综合评分算法

**核心算法：**
```python
class CompositeScoringModel:
    """
    能化品种综合评分模型
    """
    
    def __init__(self, product_type):
        self.product = product_type
        self.weights = self._get_product_weights()
    
    def _get_product_weights(self):
        """获取品种特定权重"""
        weights_config = {
            'crude': {      # 原油
                'fundamental': 0.30,
                'macro': 0.15,
                'sentiment': 0.20,
                'technical': 0.20,
                'geopolitical': 0.15
            },
            'natural_gas': {  # 天然气
                'fundamental': 0.35,
                'macro': 0.10,
                'sentiment': 0.20,
                'technical': 0.25,
                'geopolitical': 0.10
            },
            'lpg': {        # 液化气
                'fundamental': 0.30,
                'macro': 0.15,
                'sentiment': 0.25,
                'technical': 0.20,
                'geopolitical': 0.10
            },
            'product_oil': {  # 成品油
                'fundamental': 0.35,
                'macro': 0.15,
                'sentiment': 0.20,
                'technical': 0.20,
                'geopolitical': 0.10
            }
        }
        return weights_config.get(self.product, weights_config['crude'])
    
    def calculate_composite_score(self, dimension_scores, geo_risk_score):
        """
        计算综合评分
        
        Args:
            dimension_scores: dict, 各维度得分
            geo_risk_score: float, 地缘风险调整分 (-15 to +15)
        
        Returns:
            dict: 包含综合评分和各维度详情
        """
        # 基础加权得分 (0-100)
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
        
        # 生成评级
        rating = self._get_rating(final_score)
        
        return {
            'composite_score': round(final_score, 2),
            'base_score': round(base_score, 2),
            'geo_adjustment': round(geo_risk_score, 2),
            'rating': rating,
            'dimension_breakdown': dimension_scores,
            'weights': self.weights,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_rating(self, score):
        """根据得分生成评级"""
        if score >= 80: return '强烈看涨'
        elif score >= 65: return '看涨'
        elif score >= 55: return '偏看涨'
        elif score >= 45: return '中性'
        elif score >= 35: return '偏看跌'
        elif score >= 20: return '看跌'
        else: return '强烈看跌'
```

### 1.4 趋势预测模型

**多因子趋势预测模型：**
```python
class TrendPredictionModel:
    """
    基于多维度评分的趋势预测模型
    """
    
    def __init__(self):
        self.lookback_periods = [5, 10, 20]  # 回顾周期
        self.prediction_horizons = [1, 3, 5, 10]  # 预测周期(天)
    
    def predict_trend(self, historical_scores, current_price, technical_data):
        """
        预测未来价格趋势
        
        Returns:
            dict: 预测结果
        """
        predictions = {}
        
        for horizon in self.prediction_horizons:
            # 基于评分动量预测
            score_momentum = self._calculate_score_momentum(historical_scores, horizon)
            
            # 基于技术面预测
            tech_signal = self._analyze_technical_signal(technical_data, horizon)
            
            # 综合预测
            trend_probability = self._ensemble_prediction(score_momentum, tech_signal)
            
            predictions[f'{horizon}d'] = {
                'direction': trend_probability['direction'],
                'probability': trend_probability['probability'],
                'confidence': trend_probability['confidence'],
                'target_range': self._calculate_target_range(
                    current_price, 
                    trend_probability,
                    horizon
                )
            }
        
        return predictions
    
    def _calculate_score_momentum(self, scores, period):
        """计算评分动量"""
        if len(scores) < period:
            return {'direction': 'neutral', 'strength': 0}
        
        recent_scores = scores[-period:]
        score_change = recent_scores[-1] - recent_scores[0]
        score_volatility = np.std(recent_scores)
        
        # 动量强度
        momentum_strength = abs(score_change) / (score_volatility + 1e-6)
        
        direction = 'up' if score_change > 5 else 'down' if score_change < -5 else 'neutral'
        
        return {
            'direction': direction,
            'strength': min(momentum_strength, 5),
            'score_change': score_change
        }
    
    def _ensemble_prediction(self, score_momentum, tech_signal):
        """集成预测"""
        # 加权投票
        score_weight = 0.4
        tech_weight = 0.6
        
        # 方向一致性检查
        if score_momentum['direction'] == tech_signal['direction']:
            confidence = 'high'
            probability = 0.6 + 0.1 * min(score_momentum['strength'], 3)
        else:
            confidence = 'medium'
            probability = 0.5 + 0.05 * min(score_momentum['strength'], 2)
        
        # 最终方向
        if score_momentum['direction'] == tech_signal['direction']:
            direction = score_momentum['direction']
        else:
            # 技术信号权重更高
            direction = tech_signal['direction']
        
        return {
            'direction': direction,
            'probability': round(min(probability, 0.9), 2),
            'confidence': confidence
        }
```

### 1.5 风险预警指标体系

**风险预警等级定义：**

| 预警等级 | 触发条件 | 颜色标识 | 响应时间 |
|----------|----------|----------|----------|
| 红色预警 | 综合评分突变±20分或地缘风险>10 | 红色 | 即时 |
| 橙色预警 | 单维度评分突变±15分或综合评分±15分 | 橙色 | 15分钟内 |
| 黄色预警 | 连续3个周期评分同向变化>10分 | 黄色 | 1小时内 |
| 蓝色预警 | 评分趋势与价格背离 | 蓝色 | 日报中提示 |

**预警指标计算：**
```python
class RiskAlertSystem:
    """
    风险预警系统
    """
    
    def __init__(self):
        self.alert_thresholds = {
            'composite_change': 15,      # 综合评分变化阈值
            'dimension_change': 15,      # 单维度变化阈值
            'geo_risk': 10,              # 地缘风险阈值
            'consecutive_periods': 3,    # 连续周期数
            'consecutive_change': 10     # 连续变化阈值
        }
    
    def check_alerts(self, current_data, historical_data):
        """
        检查预警条件
        """
        alerts = []
        
        # 1. 综合评分突变预警
        if len(historical_data) >= 2:
            prev_score = historical_data[-1]['composite_score']
            curr_score = current_data['composite_score']
            score_change = abs(curr_score - prev_score)
            
            if score_change >= 20:
                alerts.append({
                    'level': 'red',
                    'type': 'composite_shock',
                    'message': f'综合评分剧烈变化: {prev_score:.1f} → {curr_score:.1f}',
                    'timestamp': datetime.now().isoformat()
                })
            elif score_change >= 15:
                alerts.append({
                    'level': 'orange',
                    'type': 'composite_significant_change',
                    'message': f'综合评分显著变化: {prev_score:.1f} → {curr_score:.1f}',
                    'timestamp': datetime.now().isoformat()
                })
        
        # 2. 地缘风险预警
        geo_risk = current_data.get('geo_risk_score', 0)
        if abs(geo_risk) >= 10:
            alerts.append({
                'level': 'red',
                'type': 'geopolitical_risk',
                'message': f'地缘风险急剧上升: {geo_risk:.1f}',
                'timestamp': datetime.now().isoformat()
            })
        
        # 3. 单维度突变预警
        for dimension in ['fundamental', 'macro', 'sentiment', 'technical']:
            if len(historical_data) >= 2:
                prev_dim = historical_data[-1]['dimensions'].get(dimension, 50)
                curr_dim = current_data['dimensions'].get(dimension, 50)
                dim_change = abs(curr_dim - prev_dim)
                
                if dim_change >= 15:
                    alerts.append({
                        'level': 'orange',
                        'type': f'{dimension}_significant_change',
                        'message': f'{dimension}评分显著变化: {prev_dim:.1f} → {curr_dim:.1f}',
                        'timestamp': datetime.now().isoformat()
                    })
        
        # 4. 连续趋势预警
        if len(historical_data) >= 3:
            recent_scores = [d['composite_score'] for d in historical_data[-3:]]
            changes = [recent_scores[i+1] - recent_scores[i] for i in range(2)]
            
            if all(c > 10 for c in changes):
                alerts.append({
                    'level': 'yellow',
                    'type': 'consecutive_up_trend',
                    'message': '综合评分连续上升，趋势可能反转',
                    'timestamp': datetime.now().isoformat()
                })
            elif all(c < -10 for c in changes):
                alerts.append({
                    'level': 'yellow',
                    'type': 'consecutive_down_trend',
                    'message': '综合评分连续下降，趋势可能反转',
                    'timestamp': datetime.now().isoformat()
                })
        
        # 5. 背离预警
        if self._check_divergence(current_data, historical_data):
            alerts.append({
                'level': 'blue',
                'type': 'price_score_divergence',
                'message': '价格与评分出现背离',
                'timestamp': datetime.now().isoformat()
            })
        
        return alerts
    
    def _check_divergence(self, current, historical):
        """检查价格与评分背离"""
        # 简化实现：检查价格趋势与评分趋势是否相反
        if len(historical) < 5:
            return False
        
        recent_prices = [d['price'] for d in historical[-5:]]
        recent_scores = [d['composite_score'] for d in historical[-5:]]
        
        price_trend = recent_prices[-1] - recent_prices[0]
        score_trend = recent_scores[-1] - recent_scores[0]
        
        # 趋势相反且幅度较大
        return (price_trend > 0 and score_trend < -5) or (price_trend < 0 and score_trend > 5)
```

---

## 2. 评分权重体系

### 2.1 基础权重配置

**通用权重模板：**

```python
BASE_WEIGHTS = {
    'fundamental': 0.25,    # 基本面
    'macro': 0.20,          # 宏观面
    'sentiment': 0.25,      # 情绪面
    'technical': 0.20,      # 技术面
    'geopolitical': 0.10    # 地缘风险
}
```

### 2.2 品种差异化权重

**各品种权重配置：**

| 品种类别 | 基本面 | 宏观面 | 情绪面 | 技术面 | 地缘风险 |
|----------|--------|--------|--------|--------|----------|
| **原油(WTI/Brent)** | 30% | 15% | 20% | 20% | 15% |
| **天然气(HH)** | 35% | 10% | 20% | 25% | 10% |
| **天然气(JKM/TTF)** | 35% | 10% | 25% | 20% | 10% |
| **液化气(PG/PP)** | 30% | 15% | 25% | 20% | 10% |
| **液化气(CP/MB/FEI)** | 35% | 15% | 20% | 20% | 10% |
| **成品油** | 35% | 15% | 20% | 20% | 10% |

**权重差异说明：**

```python
PRODUCT_WEIGHTS = {
    'crude_wti': {
        'fundamental': 0.30,    # 原油受库存、产量影响大
        'macro': 0.15,          # 宏观影响相对适中
        'sentiment': 0.20,      # 市场情绪重要
        'technical': 0.20,      # 技术面交易活跃
        'geopolitical': 0.15    # 地缘风险影响显著
    },
    'crude_brent': {
        'fundamental': 0.30,
        'macro': 0.15,
        'sentiment': 0.20,
        'technical': 0.20,
        'geopolitical': 0.15
    },
    'gas_hh': {
        'fundamental': 0.35,    # 美国天然气基本面主导
        'macro': 0.10,          # 宏观影响较小
        'sentiment': 0.20,
        'technical': 0.25,      # 技术面交易活跃
        'geopolitical': 0.10
    },
    'gas_jkm': {
        'fundamental': 0.35,    # 亚洲LNG供需主导
        'macro': 0.10,
        'sentiment': 0.25,      # 市场情绪波动大
        'technical': 0.20,
        'geopolitical': 0.10
    },
    'gas_ttf': {
        'fundamental': 0.35,    # 欧洲供需主导
        'macro': 0.10,
        'sentiment': 0.25,      # 地缘事件影响情绪
        'technical': 0.20,
        'geopolitical': 0.10
    },
    'lpg_pg': {
        'fundamental': 0.30,
        'macro': 0.15,
        'sentiment': 0.25,      # 化工需求预期影响情绪
        'technical': 0.20,
        'geopolitical': 0.10
    },
    'lpg_cp': {
        'fundamental': 0.35,    # CP定价机制影响
        'macro': 0.15,
        'sentiment': 0.20,
        'technical': 0.20,
        'geopolitical': 0.10
    },
    'product_oil': {
        'fundamental': 0.35,    # 炼厂开工、库存主导
        'macro': 0.15,
        'sentiment': 0.20,
        'technical': 0.20,
        'geopolitical': 0.10
    }
}
```

### 2.3 动态权重调整机制

**调整触发条件：**

| 触发场景 | 调整策略 | 调整幅度 |
|----------|----------|----------|
| 地缘事件爆发 | 地缘风险权重上升 | +5% to +10% |
| 重大数据发布 | 基本面权重上升 | +5% to +10% |
| 央行政策会议 | 宏观面权重上升 | +5% to +10% |
| 市场剧烈波动 | 技术面权重上升 | +5% to +10% |
| 持仓报告发布 | 情绪面权重上升 | +5% to +10% |
| 节假日/休市 | 技术面权重上升 | +10% |

**动态调整算法：**
```python
class DynamicWeightAdjuster:
    """
    动态权重调整器
    """
    
    def __init__(self, base_weights):
        self.base_weights = base_weights
        self.adjustment_history = []
    
    def adjust_weights(self, market_context, event_signals):
        """
        根据市场情境动态调整权重
        
        Args:
            market_context: 当前市场环境
            event_signals: 事件信号列表
        
        Returns:
            dict: 调整后的权重
        """
        adjusted_weights = self.base_weights.copy()
        adjustments = {}
        
        # 1. 地缘事件调整
        if event_signals.get('geopolitical_event'):
            adjustments['geopolitical'] = adjustments.get('geopolitical', 0) + 0.05
            adjustments['fundamental'] = adjustments.get('fundamental', 0) - 0.03
            adjustments['sentiment'] = adjustments.get('sentiment', 0) - 0.02
        
        # 2. 重大数据发布调整
        if event_signals.get('major_data_release'):
            adjustments['fundamental'] = adjustments.get('fundamental', 0) + 0.05
            adjustments['macro'] = adjustments.get('macro', 0) + 0.03
            adjustments['technical'] = adjustments.get('technical', 0) - 0.08
        
        # 3. 央行政策会议调整
        if event_signals.get('central_bank_meeting'):
            adjustments['macro'] = adjustments.get('macro', 0) + 0.08
            adjustments['sentiment'] = adjustments.get('sentiment', 0) + 0.02
            adjustments['fundamental'] = adjustments.get('fundamental', 0) - 0.10
        
        # 4. 市场波动率调整
        volatility = market_context.get('volatility', 0)
        if volatility > 0.30:  # 高波动
            adjustments['technical'] = adjustments.get('technical', 0) + 0.05
            adjustments['sentiment'] = adjustments.get('sentiment', 0) + 0.03
            adjustments['fundamental'] = adjustments.get('fundamental', 0) - 0.08
        
        # 5. 持仓报告发布调整
        if event_signals.get('cot_report'):
            adjustments['sentiment'] = adjustments.get('sentiment', 0) + 0.05
            adjustments['technical'] = adjustments.get('technical', 0) - 0.05
        
        # 6. 节假日/休市调整
        if market_context.get('market_status') == 'holiday':
            adjustments['technical'] = 0.10  # 技术面主导
            adjustments['fundamental'] = -0.05
            adjustments['macro'] = -0.05
        
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
    
    def get_adjustment_summary(self, n_recent=5):
        """获取最近调整摘要"""
        return self.adjustment_history[-n_recent:]
```

---

## 3. 可视化展示方案

### 3.1 仪表盘整体布局

**主仪表盘布局设计：**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  [Header] 能源化工新闻分析系统                    [时间] [刷新] [设置]       │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    综合评分概览区 (Score Overview)                    │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │   │
│  │  │  WTI    │ │  Brent  │ │   HH    │ │   JKM   │ │   PG    │       │   │
│  │  │  72.5   │ │  68.3   │ │  55.2   │ │  61.7   │ │  48.9   │       │   │
│  │  │  看涨   │ │  偏看涨 │ │  中性   │ │  偏看涨 │ │  中性   │       │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────┐  ┌─────────────────────────────────────┐ │
│  │    品种对比雷达图             │  │      评分趋势时间序列               │ │
│  │    (Radar Chart)             │  │      (Time Series)                  │ │
│  │                              │  │                                     │ │
│  │         基本面                │  │   100 ┤                             │ │
│  │           ▲                  │  │    80 ┤    ╭─╮                      │ │
│  │          /│\                 │  │    60 ┤───╯  ╰──                    │ │
│  │  技术面 ◄──┼──► 情绪面        │  │    40 ┤                             │ │
│  │          \│/                 │  │    20 ┤                             │ │
│  │           ▼                  │  │     0 ┼────────────────             │ │
│  │        宏观面                │  │         1d  3d  5d  10d  20d        │ │
│  │                              │  │                                     │ │
│  └──────────────────────────────┘  └─────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────┐  ┌─────────────────────────────────────┐ │
│  │    多维度评分热力图           │  │      地缘风险仪表盘                  │ │
│  │    (Heatmap)                 │  │      (Risk Gauge)                   │ │
│  │                              │  │                                     │ │
│  │   品种  │基│宏│情│技│地│      │  │        ╭─────────╮                 │ │
│  │  ─────┼─┼─┼─┼─┼─┤      │  │       ╱    中    \                │ │
│  │   WTI  │█│░│█│▓│░│      │  │      │  低  ╱╲  高  │               │ │
│  │  Brent │▓│░│▓│█│░│      │  │      │    ╱  \    │               │ │
│  │   HH   │░│█│░│▓│█│      │  │       ╰──┤    ├──╯                │ │
│  │   JKM  │█│░│█│░│▓│      │  │          │ 12.5 │                   │ │
│  │   PG   │░│▓│░│█│░│      │  │          ╰──────╯                   │ │
│  │                              │  │         风险等级: 高              │ │
│  └──────────────────────────────┘  └─────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    预警信息区 (Alert Panel)                          │   │
│  │  [红色] WTI地缘风险急剧上升 (+12.5)                    2分钟前       │   │
│  │  [橙色] Brent基本面评分显著变化 (45→62)                15分钟前      │   │
│  │  [黄色] HH综合评分连续下降3周期                        1小时前       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 图表类型详细设计

#### 3.2.1 综合评分卡片 (Score Card)

**设计规范：**
- 尺寸: 180px × 120px
- 圆角: 12px
- 背景: 根据评分动态变化
- 动画: 数值变化时平滑过渡

```css
.score-card {
    width: 180px;
    height: 120px;
    border-radius: 12px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all 0.3s ease;
}

/* 评分颜色映射 */
.score-strong-bullish { background: linear-gradient(135deg, #00C853, #64DD17); }
.score-bullish { background: linear-gradient(135deg, #69F0AE, #00C853); }
.score-mild-bullish { background: linear-gradient(135deg, #B2FF59, #69F0AE); }
.score-neutral { background: linear-gradient(135deg, #FFD54F, #FFC107); }
.score-mild-bearish { background: linear-gradient(135deg, #FF8A65, #FF5722); }
.score-bearish { background: linear-gradient(135deg, #FF5252, #F44336); }
.score-strong-bearish { background: linear-gradient(135deg, #D32F2F, #B71C1C); }
```

#### 3.2.2 雷达图 (Radar Chart)

**配置参数：**
```javascript
const radarConfig = {
    dimensions: ['基本面', '宏观面', '情绪面', '技术面', '地缘风险'],
    maxValue: 100,
    minValue: 0,
    colors: ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'],
    fillOpacity: 0.3,
    strokeWidth: 2,
    animation: true
};
```

**多品种对比雷达图：**
```javascript
// 使用 ECharts 配置
const radarOption = {
    radar: {
        indicator: [
            { name: '基本面', max: 100 },
            { name: '宏观面', max: 100 },
            { name: '情绪面', max: 100 },
            { name: '技术面', max: 100 },
            { name: '地缘风险', max: 100 }
        ],
        shape: 'polygon',
        splitNumber: 5,
        axisName: {
            color: '#333',
            fontSize: 12
        }
    },
    series: [{
        type: 'radar',
        data: [
            {
                value: [75, 60, 70, 65, 45],
                name: 'WTI',
                areaStyle: { opacity: 0.3 }
            },
            {
                value: [70, 55, 65, 70, 40],
                name: 'Brent',
                areaStyle: { opacity: 0.3 }
            }
        ]
    }]
};
```

#### 3.2.3 评分趋势时间序列图

**配置参数：**
```javascript
const trendChartConfig = {
    chartType: 'line',
    timeRanges: ['1D', '3D', '1W', '2W', '1M', '3M'],
    defaultRange: '1W',
    showVolume: true,
    indicators: ['composite', 'fundamental', 'sentiment'],
    annotations: true  // 显示事件标注
};
```

**实现代码：**
```javascript
const trendOption = {
    title: { text: '评分趋势分析' },
    tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' }
    },
    legend: {
        data: ['综合评分', '基本面', '情绪面', '技术面']
    },
    xAxis: {
        type: 'time',
        boundaryGap: false
    },
    yAxis: {
        type: 'value',
        min: 0,
        max: 100,
        splitLine: {
            lineStyle: {
                type: 'dashed'
            }
        }
    },
    series: [
        {
            name: '综合评分',
            type: 'line',
            smooth: true,
            data: compositeData,
            lineStyle: { width: 3 },
            areaStyle: {
                opacity: 0.2
            }
        },
        {
            name: '基本面',
            type: 'line',
            smooth: true,
            data: fundamentalData,
            lineStyle: { width: 2, type: 'dashed' }
        },
        {
            name: '情绪面',
            type: 'line',
            smooth: true,
            data: sentimentData,
            lineStyle: { width: 2, type: 'dashed' }
        }
    ],
    // 事件标注
    markLine: {
        data: eventAnnotations.map(e => ({
            xAxis: e.timestamp,
            label: { formatter: e.name }
        }))
    }
};
```

#### 3.2.4 热力图 (Heatmap)

**品种×维度热力图：**
```javascript
const heatmapOption = {
    tooltip: {
        position: 'top',
        formatter: function(params) {
            return `${params.name}<br/>${params.seriesName}: ${params.value[2]}`;
        }
    },
    grid: {
        height: '70%',
        top: '10%'
    },
    xAxis: {
        type: 'category',
        data: ['基本面', '宏观面', '情绪面', '技术面', '地缘风险'],
        splitArea: { show: true }
    },
    yAxis: {
        type: 'category',
        data: ['WTI', 'Brent', 'HH', 'JKM', 'TTF', 'PG', 'CP'],
        splitArea: { show: true }
    },
    visualMap: {
        min: 0,
        max: 100,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: '5%',
        inRange: {
            color: ['#313695', '#4575b4', '#74add1', '#abd9e9', 
                    '#e0f3f8', '#fee090', '#fdae61', '#f46d43', '#d73027']
        }
    },
    series: [{
        name: '评分热力图',
        type: 'heatmap',
        data: heatmapData,
        label: {
            show: true,
            formatter: '{c}'
        },
        emphasis: {
            itemStyle: {
                shadowBlur: 10,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
        }
    }]
};
```

#### 3.2.5 风险仪表盘 (Risk Gauge)

**地缘风险仪表盘设计：**
```javascript
const gaugeOption = {
    series: [{
        type: 'gauge',
        startAngle: 180,
        endAngle: 0,
        min: 0,
        max: 15,
        splitNumber: 5,
        itemStyle: {
            color: '#FF6B6B'
        },
        progress: {
            show: true,
            width: 20
        },
        pointer: {
            show: true,
            length: '60%',
            width: 6
        },
        axisLine: {
            lineStyle: {
                width: 20,
                color: [
                    [0.33, '#67e8f9'],  // 低风险
                    [0.66, '#fbbf24'],  // 中风险
                    [1, '#f87171']      // 高风险
                ]
            }
        },
        axisTick: {
            distance: -25,
            splitNumber: 5,
            lineStyle: { width: 2 }
        },
        splitLine: {
            distance: -32,
            length: 10,
            lineStyle: { width: 3 }
        },
        axisLabel: {
            distance: -15,
            formatter: function(value) {
                if (value <= 5) return '低';
                if (value <= 10) return '中';
                return '高';
            }
        },
        detail: {
            valueAnimation: true,
            formatter: '{value}',
            color: 'auto',
            fontSize: 30,
            offsetCenter: [0, '30%']
        },
        data: [{ value: 12.5, name: '地缘风险' }]
    }]
};
```

### 3.3 品种对比展示

**品种对比矩阵：**
```
┌─────────────────────────────────────────────────────────────────────────┐
│                        品种综合对比矩阵                                   │
├──────────┬────────┬────────┬────────┬────────┬────────┬─────────────────┤
│   品种   │ 综合分 │ 趋势   │ 预测   │ 波动率 │ 相关性 │    主要驱动     │
├──────────┼────────┼────────┼────────┼────────┼────────┼─────────────────┤
│ WTI      │  72.5  │  ↑    │  看涨  │  中   │ 基准  │ 库存下降+地缘   │
│ Brent    │  68.3  │  ↑    │ 偏看涨 │  中   │ 0.95  │ 供应担忧        │
│ HH       │  55.2  │  →    │  中性  │  高   │ 0.32  │ 天气+库存       │
│ JKM      │  61.7  │  ↑    │ 偏看涨 │  高   │ 0.45  │ 亚洲需求        │
│ TTF      │  58.9  │  →    │  中性  │  高   │ 0.48  │ 欧洲供应        │
│ PG       │  48.9  │  ↓    │ 偏看跌 │  中   │ 0.67  │ 化工需求疲软    │
│ CP       │  52.1  │  →    │  中性  │  低   │ 0.71  │ CP定价机制      │
└──────────┴────────┴────────┴────────┴────────┴────────┴─────────────────┘
```

**相关性热力图：**
```javascript
const correlationHeatmap = {
    series: [{
        type: 'heatmap',
        data: correlationData,
        label: {
            show: true,
            formatter: function(params) {
                return params.value[2].toFixed(2);
            }
        },
        itemStyle: {
            borderWidth: 1,
            borderColor: '#fff'
        }
    }],
    visualMap: {
        min: -1,
        max: 1,
        inRange: {
            color: ['#d73027', '#f46d43', '#fdae61', '#fee08b', 
                    '#e6f598', '#abdda4', '#66c2a5', '#3288bd']
        }
    }
};
```

### 3.4 时间维度展示

**多时间维度切换：**

| 时间维度 | 展示内容 | 更新频率 | 图表类型 |
|----------|----------|----------|----------|
| 实时 | 最新评分、预警 | 5分钟 | 卡片+仪表盘 |
| 日内 | 小时级评分变化 | 1小时 | 折线图 |
| 日线 | 日评分趋势 | 日 | K线+折线 |
| 周线 | 周评分统计 | 周 | 柱状图+折线 |
| 月线 | 月度评分分布 | 月 | 箱线图 |

**时间轴控制器：**
```javascript
const timeController = {
    ranges: [
        { label: '1H', value: 1, unit: 'hour' },
        { label: '6H', value: 6, unit: 'hour' },
        { label: '1D', value: 1, unit: 'day' },
        { label: '3D', value: 3, unit: 'day' },
        { label: '1W', value: 7, unit: 'day' },
        { label: '2W', value: 14, unit: 'day' },
        { label: '1M', value: 30, unit: 'day' },
        { label: '3M', value: 90, unit: 'day' }
    ],
    defaultRange: '1W',
    comparisonMode: true,  // 支持多时间段对比
    autoRefresh: true,
    refreshInterval: 300000  // 5分钟
};
```

---

## 4. 报告输出格式

### 4.1 实时分析报告

**实时分析卡片模板：**
```json
{
    "report_type": "realtime_analysis",
    "timestamp": "2024-01-15T14:30:00Z",
    "product": "WTI",
    "analysis": {
        "composite_score": 72.5,
        "rating": "看涨",
        "change_1h": 2.3,
        "change_24h": 5.8,
        "dimensions": {
            "fundamental": { "score": 75, "change": 3.2, "trend": "up" },
            "macro": { "score": 60, "change": -1.5, "trend": "down" },
            "sentiment": { "score": 70, "change": 4.1, "trend": "up" },
            "technical": { "score": 65, "change": 1.8, "trend": "up" }
        },
        "geo_risk": {
            "score": 8.5,
            "level": "中",
            "events": [
                {
                    "type": "supply_disruption",
                    "description": "中东某油田维护",
                    "impact": "短期供应收紧"
                }
            ]
        }
    },
    "key_drivers": [
        "EIA库存超预期下降",
        "地缘风险溢价上升",
        "技术突破关键阻力位"
    ],
    "prediction": {
        "direction": "up",
        "probability": 0.65,
        "target_range": [75.5, 78.0],
        "confidence": "medium"
    }
}
```

### 4.2 日报模板

**日报结构：**
```markdown
# 能源化工市场日报
**报告日期**: 2024年01月15日  
**报告时间**: 18:00 (北京时间)

---

## 一、市场概览

### 1.1 综合评分排名
| 排名 | 品种 | 综合评分 | 评级 | 日涨跌 | 主要驱动 |
|------|------|----------|------|--------|----------|
| 1 | WTI | 72.5 | 看涨 | +2.3% | 库存下降 |
| 2 | JKM | 61.7 | 偏看涨 | +1.8% | 需求预期 |
| 3 | Brent | 68.3 | 偏看涨 | +1.5% | 供应担忧 |
| 4 | TTF | 58.9 | 中性 | +0.5% | 震荡整理 |
| 5 | CP | 52.1 | 中性 | -0.2% | 定价机制 |
| 6 | HH | 55.2 | 中性 | -0.8% | 天气温和 |
| 7 | PG | 48.9 | 偏看跌 | -1.5% | 需求疲软 |

### 1.2 市场情绪分布
- 看涨: 3个品种 (43%)
- 中性: 3个品种 (43%)
- 看跌: 1个品种 (14%)

---

## 二、重点品种分析

### 2.1 原油 (WTI/Brent)

#### 基本面分析
- **库存数据**: EIA周报显示原油库存减少500万桶，超预期
- **产量动态**: 美国产量维持1310万桶/日
- **炼厂开工**: 炼厂开工率上升至92.5%

#### 技术面分析
- **趋势**: 突破78美元阻力位
- **支撑/阻力**: 支撑75美元 / 阻力80美元
- **动量**: RSI 65，动能偏强

#### 预测
- **短期(1-3天)**: 偏看涨，目标78-80美元
- **中期(1-2周)**: 看涨，目标80-83美元

---

## 三、风险预警

### 3.1 当日预警汇总
| 时间 | 品种 | 等级 | 类型 | 描述 |
|------|------|------|------|------|
| 14:30 | WTI | 橙色 | 基本面 | 评分显著上升 |
| 10:15 | Brent | 黄色 | 技术面 | 突破关键阻力 |

### 3.2 潜在风险提示
1. 美联储政策会议临近，宏观面不确定性增加
2. 中东地缘局势持续紧张
3. 中国需求数据待公布

---

## 四、明日关注

### 4.1 重要数据/事件
| 时间 | 事件 | 影响品种 | 预期影响 |
|------|------|----------|----------|
| 20:30 | 美国初请失业金 | 原油 | 中 |
| 23:00 | EIA天然气库存 | HH | 高 |
| -- | OPEC月报 | 原油 | 高 |

### 4.2 操作建议
- **WTI**: 关注78美元突破有效性
- **HH**: 等待EIA数据指引
- **PG**: 偏空思路，关注化工需求

---

*报告生成时间: 2024-01-15 18:00*  
*数据来源: 综合各专业机构*  
*免责声明: 本报告仅供参考，不构成投资建议*
```

### 4.3 周报模板

**周报结构：**
```markdown
# 能源化工市场周报
**报告周期**: 2024年01月08日 - 01月14日  
**报告日期**: 2024年01月14日

---

## 一、本周市场回顾

### 1.1 价格表现
| 品种 | 周初 | 周末 | 涨跌 | 涨跌幅 | 波动率 |
|------|------|------|------|--------|--------|
| WTI | 73.5 | 75.2 | +1.7 | +2.3% | 18.5% |
| Brent | 78.2 | 79.8 | +1.6 | +2.0% | 16.2% |
| ... | ... | ... | ... | ... | ... |

### 1.2 评分变化
| 品种 | 周初评分 | 周末评分 | 变化 | 评级变化 |
|------|----------|----------|------|----------|
| WTI | 65.2 | 72.5 | +7.3 | 中性→看涨 |
| ... | ... | ... | ... | ... |

---

## 二、维度分析

### 2.1 基本面周度总结
- **原油**: 库存连续下降，基本面改善
- **天然气**: 天气温和，需求疲软
- **液化气**: 化工需求偏弱

### 2.2 宏观面周度总结
- 美元指数震荡，对油价影响中性
- 通胀数据符合预期

### 2.3 情绪面周度总结
- 市场情绪整体偏乐观
- 持仓数据显示净多增加

---

## 三、下周展望

### 3.1 趋势预测
| 品种 | 方向 | 概率 | 目标区间 | 关键价位 |
|------|------|------|----------|----------|
| WTI | 上涨 | 65% | 77-82 | 支撑75/阻力80 |
| ... | ... | ... | ... | ... |

### 3.2 重点关注
1. 美联储会议纪要
2. OPEC+产量政策
3. 中国宏观经济数据

---

## 四、附录

### 4.1 本周预警记录
### 4.2 数据源说明
### 4.3 模型参数更新
```

### 4.4 预警通知格式

**即时预警通知：**
```json
{
    "alert_id": "ALT-20240115-001",
    "timestamp": "2024-01-15T14:30:00Z",
    "level": "orange",
    "product": "WTI",
    "alert_type": "composite_significant_change",
    "title": "WTI综合评分显著变化",
    "content": {
        "before": 60.2,
        "after": 72.5,
        "change": 12.3,
        "change_percent": "+20.4%",
        "trigger_factors": [
            "EIA库存超预期下降500万桶",
            "地缘风险溢价上升"
        ]
    },
    "recommendation": "关注78美元阻力位突破情况",
    "action_required": false,
    "channels": ["web", "app", "email"]
}
```

**预警通知模板（邮件/推送）：**
```
🔔 能化市场预警通知

━━━━━━━━━━━━━━━━━━━━━━━━━━
预警等级: 🟠 橙色预警
预警时间: 2024-01-15 14:30
━━━━━━━━━━━━━━━━━━━━━━━━━━

【品种】WTI原油
【类型】综合评分显著变化
【变化】60.2 → 72.5 (+12.3分 / +20.4%)
【当前评级】看涨

【触发因素】
• EIA库存超预期下降500万桶
• 地缘风险溢价上升

【市场影响】
• 短期看涨概率提升至65%
• 关注78美元阻力位突破情况

【建议操作】
• 多头持仓可继续持有
• 关注晚间美国初请数据

━━━━━━━━━━━━━━━━━━━━━━━━━━
点击查看详细分析 → [链接]
━━━━━━━━━━━━━━━━━━━━━━━━━━

本预警由能源化工新闻分析系统自动生成
```

---

## 5. 推荐技术栈

### 5.1 前端可视化技术栈

| 层级 | 技术选型 | 用途 | 优势 |
|------|----------|------|------|
| **图表库** | Apache ECharts | 主要图表组件 | 功能丰富、性能优秀、文档完善 |
| **辅助图表** | D3.js | 自定义可视化 | 灵活性高、可定制性强 |
| **地图组件** | ECharts-GL / Leaflet | 地缘风险地图 | 3D效果、交互性强 |
| **UI框架** | React + Ant Design | 界面组件 | 组件丰富、生态完善 |
| **状态管理** | Redux / Zustand | 数据状态管理 | 可预测、易调试 |
| **实时通信** | WebSocket | 实时数据推送 | 低延迟、双向通信 |

**ECharts 核心图表主题配置：**
```javascript
const chartTheme = {
    color: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272'],
    backgroundColor: 'transparent',
    textStyle: {
        fontFamily: 'Microsoft YaHei, Arial, sans-serif'
    },
    title: {
        textStyle: { fontSize: 16, fontWeight: 'bold' }
    },
    legend: {
        bottom: 0,
        textStyle: { fontSize: 12 }
    },
    tooltip: {
        backgroundColor: 'rgba(50, 50, 50, 0.9)',
        borderColor: '#333',
        textStyle: { color: '#fff' }
    }
};
```

### 5.2 后端技术栈

| 层级 | 技术选型 | 用途 | 优势 |
|------|----------|------|------|
| **API框架** | FastAPI (Python) | RESTful API | 高性能、自动文档、异步支持 |
| **计算引擎** | Python + NumPy/Pandas | 量化计算 | 科学计算生态完善 |
| **NLP处理** | spaCy / Transformers | 新闻情感分析 | 准确率高、支持中文 |
| **任务调度** | Celery + Redis | 定时任务 | 分布式、可靠 |
| **数据库** | PostgreSQL + TimescaleDB | 时序数据存储 | 时序优化、性能优秀 |
| **缓存** | Redis | 热点数据缓存 | 高性能、数据结构丰富 |
| **消息队列** | RabbitMQ / Kafka | 异步消息处理 | 高吞吐、可靠 |

**评分计算服务架构：**
```python
# FastAPI 评分计算服务示例
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import asyncio

app = FastAPI(title="能化评分计算服务")

class ScoringRequest(BaseModel):
    product: str
    news_items: list
    market_data: dict
    technical_data: dict

@app.post("/api/v1/score/calculate")
async def calculate_score(request: ScoringRequest):
    """计算综合评分"""
    model = CompositeScoringModel(request.product)
    
    # 并行计算各维度
    tasks = [
        calculate_fundamental_score(request.market_data),
        calculate_macro_score(request.market_data),
        calculate_sentiment_score(request.news_items),
        calculate_technical_score(request.technical_data),
        calculate_geopolitical_risk(request.news_items)
    ]
    
    results = await asyncio.gather(*tasks)
    
    dimension_scores = {
        'fundamental': results[0],
        'macro': results[1],
        'sentiment': results[2],
        'technical': results[3]
    }
    
    geo_risk = results[4]
    
    # 计算综合评分
    final_result = model.calculate_composite_score(dimension_scores, geo_risk)
    
    return final_result
```

### 5.3 数据流架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           数据流架构图                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │   新闻源      │    │   市场数据    │    │   宏观数据    │                  │
│  │  (RSS/API)   │    │  (API/WS)    │    │  (API/DB)    │                  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                  │
│         │                   │                   │                          │
│         └───────────────────┼───────────────────┘                          │
│                             ▼                                              │
│                    ┌─────────────────┐                                     │
│                    │   数据采集层     │                                     │
│                    │  (Celery Tasks) │                                     │
│                    └────────┬────────┘                                     │
│                             │                                              │
│                             ▼                                              │
│                    ┌─────────────────┐                                     │
│                    │   数据处理层     │                                     │
│                    │  (NLP/清洗/标准化)│                                    │
│                    └────────┬────────┘                                     │
│                             │                                              │
│              ┌──────────────┼──────────────┐                              │
│              ▼              ▼              ▼                              │
│       ┌──────────┐  ┌──────────┐  ┌──────────┐                           │
│       │ PostgreSQL│  │  Redis   │  │  Kafka   │                           │
│       │ (时序数据)│  │  (缓存)  │  │ (消息队列)│                           │
│       └────┬─────┘  └────┬─────┘  └────┬─────┘                           │
│            │             │             │                                  │
│            └─────────────┴─────────────┘                                  │
│                          │                                                │
│                          ▼                                                │
│                 ┌─────────────────┐                                       │
│                 │   评分计算引擎   │                                       │
│                 │  (FastAPI服务)  │                                       │
│                 └────────┬────────┘                                       │
│                          │                                                │
│              ┌───────────┴───────────┐                                   │
│              ▼                       ▼                                   │
│       ┌──────────┐           ┌──────────┐                                │
│       │ Web前端  │           │ 预警系统  │                                │
│       │(React+   │           │ (通知推送)│                                │
│       │ ECharts) │           │          │                                │
│       └──────────┘           └──────────┘                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.4 部署架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           部署架构图                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Nginx (负载均衡/反向代理)                      │   │
│  └───────────────────────────────┬─────────────────────────────────────┘   │
│                                  │                                         │
│              ┌───────────────────┼───────────────────┐                     │
│              ▼                   ▼                   ▼                     │
│       ┌──────────┐       ┌──────────┐       ┌──────────┐                  │
│       │ Web App  │       │ Web App  │       │ Web App  │                  │
│       │  (Pod 1) │       │  (Pod 2) │       │  (Pod N) │                  │
│       └────┬─────┘       └────┬─────┘       └────┬─────┘                  │
│            │                  │                  │                        │
│            └──────────────────┼──────────────────┘                        │
│                               │                                           │
│                    ┌──────────┴──────────┐                                │
│                    ▼                     ▼                                │
│             ┌──────────┐         ┌──────────┐                             │
│             │ API服务  │         │ API服务  │                             │
│             │ (Pod 1)  │         │ (Pod 2)  │                             │
│             └────┬─────┘         └────┬─────┘                             │
│                  │                    │                                   │
│                  └────────┬───────────┘                                   │
│                           │                                               │
│            ┌──────────────┼──────────────┐                               │
│            ▼              ▼              ▼                               │
│     ┌──────────┐  ┌──────────┐  ┌──────────┐                            │
│     │ PostgreSQL│  │  Redis   │  │ RabbitMQ │                            │
│     │ (主从集群)│  │ (Sentinel)│  │ (集群)   │                            │
│     └──────────┘  └──────────┘  └──────────┘                            │
│                                                                             │
│  技术栈: Kubernetes + Docker + Helm                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.5 性能指标要求

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 页面加载时间 | < 2s | 首屏加载 |
| 图表渲染时间 | < 500ms | 单图表 |
| 数据更新延迟 | < 5min | 从数据采集到展示 |
| API响应时间 | < 200ms | P95 |
| 并发用户数 | > 1000 | 同时在线 |
| 系统可用性 | 99.9% | 年度 |

---

## 附录

### A. 评分颜色映射表

| 评分区间 | 评级 | 颜色代码 | 说明 |
|----------|------|----------|------|
| 80-100 | 强烈看涨 | #00C853 | 积极做多 |
| 65-80 | 看涨 | #69F0AE | 偏多思路 |
| 55-65 | 偏看涨 | #B2FF59 | 谨慎偏多 |
| 45-55 | 中性 | #FFD54F | 观望为主 |
| 35-45 | 偏看跌 | #FF8A65 | 谨慎偏空 |
| 20-35 | 看跌 | #FF5252 | 偏空思路 |
| 0-20 | 强烈看跌 | #D32F2F | 积极做空 |

### B. 品种代码对照表

| 代码 | 品种 | 交易所/基准 |
|------|------|-------------|
| WTI | 西德克萨斯原油 | NYMEX |
| Brent | 布伦特原油 | ICE |
| HH | 亨利港天然气 | NYMEX |
| JKM | 日韩基准LNG | Platts |
| TTF | 荷兰天然气 | ICE |
| PG | 丙烷 | 国内市场 |
| PP | 聚丙烯 | 国内市场 |
| MB | 蒙特贝尔维尤丙烷 | OPIS |
| FEI | 远东指数丙烷 | CP/FEI |
| CP | 沙特合同价格 | Saudi Aramco |

### C. 数据源列表

| 数据类型 | 推荐数据源 | 更新频率 |
|----------|------------|----------|
| 价格数据 | Bloomberg, Refinitiv | 实时 |
| 库存数据 | EIA, API, IEA | 周度 |
| 新闻数据 | Reuters, Bloomberg, 财新 | 实时 |
| 持仓数据 | CFTC COT报告 | 周度 |
| 宏观数据 | Wind, 彭博 | 按发布日程 |

---

*文档版本: v1.0*  
*最后更新: 2024年1月*  
*作者: 量化分析与数据可视化专家组*
