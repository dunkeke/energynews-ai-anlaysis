"""
Pydantic模型定义 - 数据验证和序列化
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class Dimension(str, Enum):
    FUNDAMENTAL = "fundamental"
    MACRO = "macro"
    SENTIMENT = "sentiment"
    TECHNICAL = "technical"
    GEOPOLITICAL = "geopolitical"

class Rating(str, Enum):
    STRONG_BULLISH = "强烈看涨"
    BULLISH = "看涨"
    MILD_BULLISH = "轻度看涨"
    NEUTRAL = "中性"
    MILD_BEARISH = "轻度看跌"
    BEARISH = "看跌"
    STRONG_BEARISH = "强烈看跌"

class Signal(str, Enum):
    BUY = "买入"
    HOLD = "持有"
    SELL = "卖出"
    STRONG_BUY = "强烈买入"
    STRONG_SELL = "强烈卖出"

# ========== 新闻相关模型 ==========

class NewsItem(BaseModel):
    id: str
    title: str
    content: str
    source: str
    source_url: Optional[str] = None
    publish_time: Optional[datetime] = None
    crawl_time: datetime = Field(default_factory=datetime.now)
    commodity_tags: List[str] = []
    sentiment: Optional[Sentiment] = None
    sentiment_score: Optional[float] = None
    keywords: List[str] = []
    entities: List[Dict[str, Any]] = []
    dimensions: Dict[str, float] = {}
    importance_score: Optional[float] = None
    is_analyzed: bool = False
    
    class Config:
        from_attributes = True

class ImportRequest(BaseModel):
    import_type: str = Field(..., description="导入类型: url, text, pdf")
    content: Optional[str] = None
    source: str = "user_import"
    commodities: Optional[List[str]] = None

# ========== 分析相关模型 ==========

class DimensionScore(BaseModel):
    dimension: Dimension
    score: float = Field(..., ge=0, le=100)
    weight: float
    confidence: float
    keywords: List[str] = []
    factors: List[str] = []

class AnalysisResult(BaseModel):
    commodity: str
    timestamp: datetime
    dimensions: Dict[str, DimensionScore]
    composite_score: float = Field(..., ge=0, le=100)
    rating: Rating
    signal: Signal
    confidence: float
    key_factors: List[str]
    news_count: int
    analysis_period: str
    
    class Config:
        from_attributes = True

class AnalysisRequest(BaseModel):
    dimensions: List[Dimension] = [
        Dimension.FUNDAMENTAL,
        Dimension.MACRO,
        Dimension.SENTIMENT,
        Dimension.TECHNICAL,
        Dimension.GEOPOLITICAL
    ]
    lookback_days: int = 7
    include_history: bool = True

# ========== 量化评分模型 ==========

class QuantScore(BaseModel):
    commodity: str
    timestamp: datetime
    composite_score: float = Field(..., ge=0, le=100)
    base_score: float
    geo_adjustment: float
    rating: Rating
    signal: Signal
    confidence: float
    dimension_breakdown: Dict[str, float]
    weights: Dict[str, float]
    historical_scores: Optional[List[Dict[str, Any]]] = None
    trend_direction: Optional[str] = None
    trend_strength: Optional[float] = None
    
    class Config:
        from_attributes = True

class TrendPrediction(BaseModel):
    horizon_days: int
    direction: str
    probability: float
    confidence: str
    target_range: Optional[Dict[str, float]] = None

# ========== 预警模型 ==========

class AlertLevel(str, Enum):
    RED = "red"
    ORANGE = "orange"
    YELLOW = "yellow"
    BLUE = "blue"

class AlertItem(BaseModel):
    id: str
    level: AlertLevel
    type: str
    commodity: Optional[str]
    message: str
    details: Dict[str, Any] = {}
    timestamp: datetime
    is_read: bool = False
    related_news: List[str] = []
    
    class Config:
        from_attributes = True

# ========== 可视化模型 ==========

class ScoreCard(BaseModel):
    commodity: str
    score: float
    rating: Rating
    signal: Signal
    change_24h: Optional[float] = None
    trend: Optional[str] = None

class RadarData(BaseModel):
    dimensions: List[str]
    series: List[Dict[str, Any]]

class TrendPoint(BaseModel):
    timestamp: datetime
    composite_score: float
    dimensions: Dict[str, float]
    events: Optional[List[Dict[str, Any]]] = None

class HeatmapData(BaseModel):
    commodities: List[str]
    dimensions: List[str]
    data: List[List[float]]

class DashboardData(BaseModel):
    timestamp: datetime
    score_cards: List[ScoreCard]
    recent_alerts: List[AlertItem]
    top_news: List[NewsItem]
    market_overview: Dict[str, Any]
    
    class Config:
        from_attributes = True

# ========== NLP分析模型 ==========

class Entity(BaseModel):
    text: str
    type: str
    start: int
    end: int
    confidence: float

class SentimentResult(BaseModel):
    overall: Sentiment
    intensity: float = Field(..., ge=0, le=100)
    confidence: float
    by_product: Dict[str, Dict[str, Any]] = {}

class EventInfo(BaseModel):
    type: str
    subtype: Optional[str]
    importance: float = Field(..., ge=0, le=100)
    sentiment: Sentiment
    related_products: List[str]

class NLPAnalysisResult(BaseModel):
    news_id: str
    entities: List[Entity]
    keywords: List[Dict[str, Any]]
    sentiment: SentimentResult
    events: List[EventInfo]
    dimensions: Dict[str, Dict[str, Any]]
    dimension_weights: Dict[str, float]
    overall_score: float
    trading_signal: Optional[str] = None
    processing_time: float
    
    class Config:
        from_attributes = True

# ========== 配置模型 ==========

class CommodityConfig(BaseModel):
    code: str
    name: str
    name_en: str
    category: str
    weights: Dict[str, float]
    key_indicators: List[str]
    data_sources: List[str]
    is_active: bool = True
