"""
能源化工新闻分析软件 - FastAPI主应用
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
import uvicorn
from loguru import logger

# 导入服务
from services.news_collector import NewsCollectorService
from services.nlp_analyzer import NLPAnalyzerService
from services.quant_scorer import QuantScorerService
from services.visualization import VisualizationService
from services.alert_system import AlertSystem
from models.database import init_db, get_db
from models.schemas import (
    NewsItem, AnalysisResult, QuantScore, AlertItem,
    ImportRequest, AnalysisRequest, DashboardData
)
from utils.config import get_settings

settings = get_settings()
security = HTTPBearer()

# 服务实例
news_collector = NewsCollectorService()
nlp_analyzer = NLPAnalyzerService()
quant_scorer = QuantScorerService()
visualization = VisualizationService()
alert_system = AlertSystem()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("启动能源化工新闻分析系统...")
    await init_db()
    await news_collector.initialize()
    await nlp_analyzer.initialize()
    await quant_scorer.initialize()
    await alert_system.initialize()
    logger.info("系统初始化完成")
    yield
    logger.info("关闭系统...")
    await news_collector.close()
    await nlp_analyzer.close()
    await quant_scorer.close()
    await alert_system.close()

app = FastAPI(
    title="能源化工新闻分析系统",
    description="综合各专业和主流媒体进行能化品种新闻分析",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# ========== 数据采集接口 ==========

@app.post("/api/v1/news/import", response_model=Dict[str, Any])
async def import_news(
    background_tasks: BackgroundTasks,
    import_type: str = Form(..., description="导入类型: url, text, pdf"),
    content: Optional[str] = Form(None, description="文本内容或URL"),
    file: Optional[UploadFile] = File(None, description="上传文件(PDF/文本)"),
    source: str = Form("user_import", description="来源标识"),
    commodities: Optional[List[str]] = Form(None, description="关联品种")
):
    """
    手工导入新闻内容
    支持URL、文本、PDF文件
    """
    try:
        result = await news_collector.import_content(
            import_type=import_type,
            content=content,
            file=file,
            source=source,
            commodities=commodities
        )
        
        # 后台触发分析
        background_tasks.add_task(
            analyze_news_background,
            result["news_id"]
        )
        
        return {
            "success": True,
            "news_id": result["news_id"],
            "status": "processing",
            "message": "内容已接收，正在分析中"
        }
    except Exception as e:
        logger.error(f"导入失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/news", response_model=List[NewsItem])
async def get_news_list(
    commodity: Optional[str] = None,
    source: Optional[str] = None,
    sentiment: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 20,
    offset: int = 0
):
    """获取新闻列表"""
    try:
        news = await news_collector.get_news(
            commodity=commodity,
            source=source,
            sentiment=sentiment,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )
        return news
    except Exception as e:
        logger.error(f"获取新闻列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========== 分析接口 ==========

@app.post("/api/v1/analysis/{commodity}", response_model=AnalysisResult)
async def analyze_commodity(
    commodity: str,
    request: AnalysisRequest
):
    """
    对指定品种进行多维度分析
    """
    try:
        # 获取相关新闻
        news_items = await news_collector.get_news(
            commodity=commodity,
            start_date=datetime.now() - timedelta(days=request.lookback_days),
            limit=100
        )
        
        # NLP分析
        nlp_results = await nlp_analyzer.analyze_batch(news_items)
        
        # 量化评分
        quant_result = await quant_scorer.calculate_score(
            commodity=commodity,
            nlp_results=nlp_results,
            dimensions=request.dimensions
        )
        
        # 生成分析报告
        analysis_result = AnalysisResult(
            commodity=commodity,
            timestamp=datetime.now(),
            dimensions=quant_result["dimensions"],
            composite_score=quant_result["composite_score"],
            rating=quant_result["rating"],
            signal=quant_result["signal"],
            confidence=quant_result["confidence"],
            key_factors=quant_result["key_factors"],
            news_count=len(news_items),
            analysis_period=f"{request.lookback_days}天"
        )
        
        return analysis_result
    except Exception as e:
        logger.error(f"分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analysis/{commodity}/realtime", response_model=Dict[str, Any])
async def get_realtime_analysis(commodity: str):
    """获取实时分析结果"""
    try:
        result = await quant_scorer.get_realtime_score(commodity)
        return result
    except Exception as e:
        logger.error(f"获取实时分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========== 量化评分接口 ==========

@app.get("/api/v1/quant/{commodity}/score", response_model=QuantScore)
async def get_quant_score(
    commodity: str,
    include_history: bool = True
):
    """
    获取品种量化评分
    """
    try:
        score = await quant_scorer.get_current_score(
            commodity=commodity,
            include_history=include_history
        )
        return score
    except Exception as e:
        logger.error(f"获取评分失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/quant/compare", response_model=Dict[str, Any])
async def compare_commodities(
    commodities: List[str],
    dimension: Optional[str] = None
):
    """
    多品种对比分析
    """
    try:
        comparison = await quant_scorer.compare_commodities(
            commodities=commodities,
            dimension=dimension
        )
        return comparison
    except Exception as e:
        logger.error(f"对比分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========== 可视化接口 ==========

@app.get("/api/v1/visualization/dashboard", response_model=DashboardData)
async def get_dashboard_data():
    """
    获取仪表盘数据
    """
    try:
        dashboard = await visualization.get_dashboard_data()
        return dashboard
    except Exception as e:
        logger.error(f"获取仪表盘数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/visualization/trend/{commodity}")
async def get_trend_data(
    commodity: str,
    days: int = 30,
    dimensions: Optional[List[str]] = None
):
    """
    获取评分趋势数据
    """
    try:
        trend_data = await visualization.get_trend_data(
            commodity=commodity,
            days=days,
            dimensions=dimensions
        )
        return trend_data
    except Exception as e:
        logger.error(f"获取趋势数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/visualization/radar/{commodity}")
async def get_radar_data(commodity: str):
    """
    获取雷达图数据
    """
    try:
        radar_data = await visualization.get_radar_data(commodity)
        return radar_data
    except Exception as e:
        logger.error(f"获取雷达图数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========== 预警接口 ==========

@app.get("/api/v1/alerts", response_model=List[AlertItem])
async def get_alerts(
    level: Optional[str] = None,
    commodity: Optional[str] = None,
    unread_only: bool = False,
    limit: int = 50
):
    """
    获取预警列表
    """
    try:
        alerts = await alert_system.get_alerts(
            level=level,
            commodity=commodity,
            unread_only=unread_only,
            limit=limit
        )
        return alerts
    except Exception as e:
        logger.error(f"获取预警失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/alerts/{alert_id}/read")
async def mark_alert_read(alert_id: str):
    """标记预警为已读"""
    try:
        await alert_system.mark_read(alert_id)
        return {"success": True}
    except Exception as e:
        logger.error(f"标记预警失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========== 后台任务 ==========

async def analyze_news_background(news_id: str):
    """后台分析新闻"""
    try:
        # 获取新闻内容
        news = await news_collector.get_news_by_id(news_id)
        if not news:
            logger.warning(f"新闻不存在: {news_id}")
            return
        
        # NLP分析
        nlp_result = await nlp_analyzer.analyze(news)
        
        # 更新新闻分析结果
        await news_collector.update_analysis_result(news_id, nlp_result)
        
        # 检查预警
        await alert_system.check_news_alert(news, nlp_result)
        
        logger.info(f"新闻分析完成: {news_id}")
    except Exception as e:
        logger.error(f"后台分析失败: {e}")

# ========== 健康检查 ==========

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
