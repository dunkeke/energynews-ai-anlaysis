"""
预警系统 - 风险监控和预警生成
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
from loguru import logger

from models.schemas import AlertItem, AlertLevel, NewsItem
from models.database import get_mongodb, MongoCollections

class AlertSystem:
    """预警系统"""
    
    # 预警阈值配置
    ALERT_THRESHOLDS = {
        "composite_change": {
            "red": 20,
            "orange": 15,
            "yellow": 10
        },
        "dimension_change": {
            "red": 20,
            "orange": 15,
            "yellow": 10
        },
        "geo_risk": {
            "red": 10,
            "orange": 7,
            "yellow": 5
        },
        "consecutive_periods": 3,
        "consecutive_change": 10
    }
    
    def __init__(self):
        self.mongodb = None
        self.initialized = False
        self.alert_history = []
    
    async def initialize(self):
        """初始化预警系统"""
        try:
            self.mongodb = await get_mongodb()
            self.initialized = True
            logger.info("预警系统初始化完成")
        except Exception as e:
            logger.error(f"预警系统初始化失败: {e}")
            raise
    
    async def check_news_alert(self, news: Dict[str, Any], nlp_result: Any):
        """检查新闻是否触发预警"""
        try:
            alerts = []
            
            # 1. 检查地缘风险
            if hasattr(nlp_result, 'events'):
                for event in nlp_result.events:
                    if hasattr(event, 'type') and self._is_geopolitical_event(event.type):
                        importance = getattr(event, 'importance', 50)
                        if importance >= 80:
                            alerts.append(await self._create_alert(
                                level=AlertLevel.RED,
                                alert_type="geopolitical_risk",
                                commodity=self._get_related_commodity(event),
                                message=f"地缘风险事件: {getattr(event, 'subtype', '未知')}",
                                details={
                                    "event_type": event.type,
                                    "importance": importance,
                                    "news_id": news.get("_id")
                                }
                            ))
            
            # 2. 检查情感极值
            if hasattr(nlp_result, 'sentiment'):
                sentiment = nlp_result.sentiment
                if hasattr(sentiment, 'intensity') and sentiment.intensity >= 80:
                    alerts.append(await self._create_alert(
                        level=AlertLevel.ORANGE,
                        alert_type="extreme_sentiment",
                        commodity=None,
                        message=f"极端市场情绪 detected",
                        details={
                            "sentiment": getattr(sentiment, 'overall', 'unknown'),
                            "intensity": sentiment.intensity,
                            "news_id": news.get("_id")
                        }
                    ))
            
            # 3. 检查重要数据发布
            if hasattr(nlp_result, 'keywords'):
                keywords = [kw.get("word", "") for kw in nlp_result.keywords]
                if any(kw in ["EIA", "API", "OPEC", "IEA"] for kw in keywords):
                    if any(kw in ["库存", "产量", "报告"] for kw in keywords):
                        alerts.append(await self._create_alert(
                            level=AlertLevel.YELLOW,
                            alert_type="data_release",
                            commodity=None,
                            message="重要数据发布",
                            details={
                                "keywords": keywords,
                                "news_id": news.get("_id")
                            }
                        ))
            
            # 保存预警
            for alert in alerts:
                await self._save_alert(alert)
            
            return alerts
        except Exception as e:
            logger.error(f"检查新闻预警失败: {e}")
            return []
    
    async def check_score_alert(
        self,
        commodity: str,
        current_score: float,
        previous_score: Optional[float],
        dimension_scores: Dict[str, float],
        previous_dimension_scores: Optional[Dict[str, float]]
    ) -> List[AlertItem]:
        """检查评分变化是否触发预警"""
        try:
            alerts = []
            
            # 1. 综合评分突变预警
            if previous_score is not None:
                score_change = abs(current_score - previous_score)
                
                if score_change >= self.ALERT_THRESHOLDS["composite_change"]["red"]:
                    alerts.append(await self._create_alert(
                        level=AlertLevel.RED,
                        alert_type="composite_shock",
                        commodity=commodity,
                        message=f"{commodity}综合评分剧烈变化: {previous_score:.1f} → {current_score:.1f}",
                        details={
                            "previous_score": previous_score,
                            "current_score": current_score,
                            "change": score_change
                        }
                    ))
                elif score_change >= self.ALERT_THRESHOLDS["composite_change"]["orange"]:
                    alerts.append(await self._create_alert(
                        level=AlertLevel.ORANGE,
                        alert_type="composite_significant_change",
                        commodity=commodity,
                        message=f"{commodity}综合评分显著变化: {previous_score:.1f} → {current_score:.1f}",
                        details={
                            "previous_score": previous_score,
                            "current_score": current_score,
                            "change": score_change
                        }
                    ))
            
            # 2. 单维度突变预警
            if previous_dimension_scores:
                for dim_name, current_dim_score in dimension_scores.items():
                    prev_dim_score = previous_dimension_scores.get(dim_name)
                    if prev_dim_score is not None:
                        dim_change = abs(current_dim_score - prev_dim_score)
                        
                        if dim_change >= self.ALERT_THRESHOLDS["dimension_change"]["orange"]:
                            alerts.append(await self._create_alert(
                                level=AlertLevel.ORANGE,
                                alert_type=f"{dim_name}_significant_change",
                                commodity=commodity,
                                message=f"{commodity}{dim_name}评分显著变化: {prev_dim_score:.1f} → {current_dim_score:.1f}",
                                details={
                                    "dimension": dim_name,
                                    "previous_score": prev_dim_score,
                                    "current_score": current_dim_score,
                                    "change": dim_change
                                }
                            ))
            
            # 3. 连续趋势预警
            # 这里需要查询历史数据，简化处理
            
            # 保存预警
            for alert in alerts:
                await self._save_alert(alert)
            
            return alerts
        except Exception as e:
            logger.error(f"检查评分预警失败: {e}")
            return []
    
    async def get_alerts(
        self,
        level: Optional[str] = None,
        commodity: Optional[str] = None,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[AlertItem]:
        """获取预警列表"""
        try:
            # 构建查询条件
            query = {}
            
            if level:
                query["level"] = level
            
            if commodity:
                query["commodity"] = commodity
            
            if unread_only:
                query["is_read"] = False
            
            # 查询数据库
            cursor = self.mongodb[MongoCollections.ANALYTICS_CACHE].find(query)
            cursor = cursor.sort("timestamp", -1).limit(limit)
            
            alerts = []
            async for doc in cursor:
                alerts.append(AlertItem(
                    id=str(doc.get("_id")),
                    level=doc.get("level"),
                    type=doc.get("type"),
                    commodity=doc.get("commodity"),
                    message=doc.get("message"),
                    details=doc.get("details", {}),
                    timestamp=doc.get("timestamp"),
                    is_read=doc.get("is_read", False)
                ))
            
            return alerts
        except Exception as e:
            logger.error(f"获取预警列表失败: {e}")
            return []
    
    async def mark_read(self, alert_id: str):
        """标记预警为已读"""
        try:
            await self.mongodb[MongoCollections.ANALYTICS_CACHE].update_one(
                {"_id": alert_id},
                {"$set": {"is_read": True, "read_time": datetime.now()}}
            )
            logger.info(f"预警已标记为已读: {alert_id}")
        except Exception as e:
            logger.error(f"标记预警已读失败: {e}")
            raise
    
    async def _create_alert(
        self,
        level: AlertLevel,
        alert_type: str,
        commodity: Optional[str],
        message: str,
        details: Dict[str, Any]
    ) -> AlertItem:
        """创建预警对象"""
        return AlertItem(
            id=f"alert_{datetime.now().timestamp()}",
            level=level,
            type=alert_type,
            commodity=commodity,
            message=message,
            details=details,
            timestamp=datetime.now(),
            is_read=False
        )
    
    async def _save_alert(self, alert: AlertItem):
        """保存预警到数据库"""
        try:
            doc = {
                "_id": alert.id,
                "level": alert.level,
                "type": alert.type,
                "commodity": alert.commodity,
                "message": alert.message,
                "details": alert.details,
                "timestamp": alert.timestamp,
                "is_read": alert.is_read
            }
            
            await self.mongodb[MongoCollections.ANALYTICS_CACHE].insert_one(doc)
            logger.info(f"预警已保存: {alert.id}")
        except Exception as e:
            logger.error(f"保存预警失败: {e}")
    
    def _is_geopolitical_event(self, event_type: str) -> bool:
        """判断是否为地缘事件"""
        geo_keywords = ["地缘", "冲突", "战争", "制裁", "中东", "伊朗", "俄罗斯", "以色列"]
        return any(keyword in event_type for keyword in geo_keywords)
    
    def _get_related_commodity(self, event: Any) -> Optional[str]:
        """获取事件相关产品"""
        if hasattr(event, 'related_products') and event.related_products:
            return event.related_products[0]
        return None
    
    async def close(self):
        """关闭服务"""
        logger.info("预警系统已关闭")
