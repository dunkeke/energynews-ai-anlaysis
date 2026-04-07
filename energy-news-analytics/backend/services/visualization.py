"""
可视化服务 - 仪表盘数据生成
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from loguru import logger

from models.schemas import (
    DashboardData, ScoreCard, RadarData, TrendPoint,
    HeatmapData, AlertItem, NewsItem
)

class VisualizationService:
    """可视化服务"""
    
    # 关注的品种列表
    COMMODITIES = ["WTI", "Brent", "HH", "TTF", "JKM", "PG", "CP", "FEI"]
    
    def __init__(self):
        self.initialized = False
    
    async def initialize(self):
        """初始化可视化服务"""
        try:
            self.initialized = True
            logger.info("可视化服务初始化完成")
        except Exception as e:
            logger.error(f"可视化服务初始化失败: {e}")
            raise
    
    async def get_dashboard_data(self) -> DashboardData:
        """获取仪表盘数据"""
        try:
            # 生成评分卡片数据
            score_cards = await self._generate_score_cards()
            
            # 生成最近预警
            recent_alerts = await self._generate_recent_alerts()
            
            # 生成热门新闻
            top_news = await self._generate_top_news()
            
            # 生成市场概览
            market_overview = await self._generate_market_overview()
            
            return DashboardData(
                timestamp=datetime.now(),
                score_cards=score_cards,
                recent_alerts=recent_alerts,
                top_news=top_news,
                market_overview=market_overview
            )
        except Exception as e:
            logger.error(f"获取仪表盘数据失败: {e}")
            raise
    
    async def get_trend_data(
        self,
        commodity: str,
        days: int = 30,
        dimensions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """获取趋势数据"""
        try:
            # 生成模拟趋势数据
            trend_data = []
            base_score = 50
            
            for i in range(days):
                date = datetime.now() - timedelta(days=days-i-1)
                
                # 模拟分数变化
                import random
                change = random.uniform(-5, 5)
                score = base_score + change
                base_score = score  # 累积变化
                
                # 确保分数在有效范围
                score = max(0, min(100, score))
                
                point = {
                    "timestamp": date.isoformat(),
                    "composite_score": round(score, 2),
                    "dimensions": {
                        "fundamental": round(score + random.uniform(-10, 10), 2),
                        "macro": round(score + random.uniform(-10, 10), 2),
                        "sentiment": round(score + random.uniform(-10, 10), 2),
                        "technical": round(score + random.uniform(-10, 10), 2),
                        "geopolitical": round(score + random.uniform(-10, 10), 2)
                    }
                }
                trend_data.append(point)
            
            return {
                "commodity": commodity,
                "days": days,
                "data": trend_data
            }
        except Exception as e:
            logger.error(f"获取趋势数据失败: {e}")
            raise
    
    async def get_radar_data(self, commodity: str) -> Dict[str, Any]:
        """获取雷达图数据"""
        try:
            # 模拟雷达图数据
            import random
            
            dimensions = ["基本面", "宏观面", "情绪面", "技术面", "地缘风险"]
            
            data = {
                "commodity": commodity,
                "dimensions": dimensions,
                "series": [
                    {
                        "name": commodity,
                        "value": [
                            round(random.uniform(40, 80), 1),
                            round(random.uniform(40, 80), 1),
                            round(random.uniform(40, 80), 1),
                            round(random.uniform(40, 80), 1),
                            round(random.uniform(40, 80), 1)
                        ]
                    }
                ]
            }
            
            return data
        except Exception as e:
            logger.error(f"获取雷达图数据失败: {e}")
            raise
    
    async def get_heatmap_data(self) -> HeatmapData:
        """获取热力图数据"""
        try:
            import random
            
            commodities = self.COMMODITIES
            dimensions = ["基本面", "宏观面", "情绪面", "技术面", "地缘风险"]
            
            # 生成热力图数据
            data = []
            for i, commodity in enumerate(commodities):
                row = []
                for j, dim in enumerate(dimensions):
                    value = round(random.uniform(30, 80), 1)
                    row.append(value)
                data.append(row)
            
            return HeatmapData(
                commodities=commodities,
                dimensions=dimensions,
                data=data
            )
        except Exception as e:
            logger.error(f"获取热力图数据失败: {e}")
            raise
    
    async def get_comparison_data(self, commodities: List[str]) -> Dict[str, Any]:
        """获取品种对比数据"""
        try:
            import random
            
            series = []
            for commodity in commodities:
                series.append({
                    "name": commodity,
                    "data": [
                        round(random.uniform(40, 80), 1),
                        round(random.uniform(40, 80), 1),
                        round(random.uniform(40, 80), 1),
                        round(random.uniform(40, 80), 1),
                        round(random.uniform(40, 80), 1)
                    ]
                })
            
            return {
                "dimensions": ["基本面", "宏观面", "情绪面", "技术面", "地缘风险"],
                "series": series
            }
        except Exception as e:
            logger.error(f"获取对比数据失败: {e}")
            raise
    
    async def _generate_score_cards(self) -> List[ScoreCard]:
        """生成评分卡片"""
        try:
            import random
            
            cards = []
            for commodity in self.COMMODITIES[:5]:  # 只显示前5个
                score = round(random.uniform(35, 75), 1)
                
                # 确定评级和信号
                if score >= 70:
                    rating = "强烈看涨"
                    signal = "强烈买入"
                    trend = "up"
                elif score >= 60:
                    rating = "看涨"
                    signal = "买入"
                    trend = "up"
                elif score >= 45:
                    rating = "中性"
                    signal = "持有"
                    trend = "stable"
                elif score >= 30:
                    rating = "看跌"
                    signal = "卖出"
                    trend = "down"
                else:
                    rating = "强烈看跌"
                    signal = "强烈卖出"
                    trend = "down"
                
                cards.append(ScoreCard(
                    commodity=commodity,
                    score=score,
                    rating=rating,
                    signal=signal,
                    change_24h=round(random.uniform(-5, 5), 1),
                    trend=trend
                ))
            
            # 按分数排序
            cards.sort(key=lambda x: x.score, reverse=True)
            
            return cards
        except Exception as e:
            logger.error(f"生成评分卡片失败: {e}")
            return []
    
    async def _generate_recent_alerts(self) -> List[AlertItem]:
        """生成最近预警"""
        try:
            import random
            
            alerts = []
            alert_types = [
                ("red", "地缘风险急剧上升", "WTI"),
                ("orange", "基本面评分显著变化", "Brent"),
                ("yellow", "综合评分连续下降", "HH"),
                ("blue", "价格与评分背离", "PG")
            ]
            
            for i, (level, message, commodity) in enumerate(alert_types):
                alerts.append(AlertItem(
                    id=f"alert_{i}",
                    level=level,
                    type="system",
                    commodity=commodity,
                    message=message,
                    timestamp=datetime.now() - timedelta(minutes=random.randint(5, 120)),
                    is_read=False
                ))
            
            return alerts
        except Exception as e:
            logger.error(f"生成预警数据失败: {e}")
            return []
    
    async def _generate_top_news(self) -> List[NewsItem]:
        """生成热门新闻"""
        try:
            news_list = []
            
            news_data = [
                {
                    "title": "OPEC+同意延长减产协议至二季度",
                    "source": "Reuters",
                    "commodity_tags": ["WTI", "Brent"],
                    "sentiment": "positive"
                },
                {
                    "title": "EIA原油库存超预期增加500万桶",
                    "source": "EIA",
                    "commodity_tags": ["WTI"],
                    "sentiment": "negative"
                },
                {
                    "title": "欧洲天然气库存降至历史低位",
                    "source": "Platts",
                    "commodity_tags": ["TTF"],
                    "sentiment": "positive"
                },
                {
                    "title": "美联储暗示可能暂停加息",
                    "source": "Bloomberg",
                    "commodity_tags": ["WTI", "Brent", "HH"],
                    "sentiment": "positive"
                },
                {
                    "title": "中国原油进口量同比增长8%",
                    "source": "新浪财经",
                    "commodity_tags": ["WTI", "Brent"],
                    "sentiment": "positive"
                }
            ]
            
            for i, news in enumerate(news_data):
                news_list.append(NewsItem(
                    id=f"news_{i}",
                    title=news["title"],
                    content=news["title"],
                    source=news["source"],
                    crawl_time=datetime.now() - timedelta(minutes=i*30),
                    commodity_tags=news["commodity_tags"],
                    sentiment=news["sentiment"]
                ))
            
            return news_list
        except Exception as e:
            logger.error(f"生成新闻数据失败: {e}")
            return []
    
    async def _generate_market_overview(self) -> Dict[str, Any]:
        """生成市场概览"""
        try:
            import random
            
            return {
                "total_news_24h": random.randint(50, 200),
                "analyzed_news_24h": random.randint(40, 150),
                "active_alerts": random.randint(3, 15),
                "avg_sentiment": round(random.uniform(-0.3, 0.3), 2),
                "market_status": "active",
                "last_update": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"生成市场概览失败: {e}")
            return {}
    
    async def close(self):
        """关闭服务"""
        logger.info("可视化服务已关闭")
