"""
数据库模型定义 - SQLAlchemy + MongoDB
"""
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    create_engine, Column, String, Integer, Float, DateTime, 
    Boolean, Text, ForeignKey, Table, JSON, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import redis.asyncio as redis
from loguru import logger

# 获取配置 - 支持SQLite和PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./energy_news.db")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/energy_news")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# 判断是否使用SQLite
IS_SQLITE = DATABASE_URL.startswith("sqlite")

# SQLAlchemy配置
Base = declarative_base()

# 创建引擎（支持SQLite和PostgreSQL）
if IS_SQLITE:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# MongoDB客户端（可选）
try:
    mongo_client = AsyncIOMotorClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
    mongodb = mongo_client.get_default_database()
    logger.info("MongoDB连接成功")
except Exception as e:
    logger.warning(f"MongoDB连接失败（可选）: {e}")
    mongo_client = None
    mongodb = None

# Redis客户端（可选）
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    logger.info("Redis连接成功")
except Exception as e:
    logger.warning(f"Redis连接失败（可选）: {e}")
    redis_client = None

# ========== PostgreSQL模型 ==========

class Article(Base):
    """文章主表"""
    __tablename__ = "articles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    uuid = Column(String, unique=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False)
    source_name = Column(String(100), nullable=False)
    source_url = Column(String(500))
    original_url = Column(String(500), unique=True)
    content_hash = Column(String(64), unique=True)
    
    # 时间字段
    publish_time = Column(DateTime(timezone=True))
    crawl_time = Column(DateTime(timezone=True), default=datetime.utcnow)
    update_time = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 内容元数据
    content_type = Column(String(20), default='news')
    language = Column(String(10), default='zh')
    word_count = Column(Integer)
    
    # 质量评分
    quality_score = Column(Float)
    is_valid = Column(Boolean, default=True)
    
    # 用户输入标记
    is_user_input = Column(Boolean, default=False)
    user_id = Column(String)
    
    # 软删除
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True))
    
    # 分析状态
    is_analyzed = Column(Boolean, default=False)
    analysis_time = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # 关系
    contents = relationship("ArticleContent", back_populates="article", uselist=False)
    commodity_tags = relationship("CommodityTag", back_populates="article")
    analysis_dimensions = relationship("AnalysisDimension", back_populates="article")

class ArticleContent(Base):
    """文章内容表（大字段分离）"""
    __tablename__ = "article_contents"
    
    article_id = Column(String, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True)
    content = Column(Text)
    summary = Column(Text)
    cleaned_content = Column(Text)
    metadata = Column(JSONB)
    
    article = relationship("Article", back_populates="contents")

class CommodityTag(Base):
    """品种标签表"""
    __tablename__ = "commodity_tags"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(String, ForeignKey("articles.id", ondelete="CASCADE"))
    commodity_type = Column(String(50), nullable=False)
    sub_type = Column(String(50))
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    article = relationship("Article", back_populates="commodity_tags")

class AnalysisDimension(Base):
    """分析维度表"""
    __tablename__ = "analysis_dimensions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(String, ForeignKey("articles.id", ondelete="CASCADE"))
    dimension_type = Column(String(50), nullable=False)
    relevance_score = Column(Float)
    extracted_keywords = Column(JSONB)
    sentiment_score = Column(Float)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    article = relationship("Article", back_populates="analysis_dimensions")

class DataSource(Base):
    """数据源配置表"""
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(200))
    source_type = Column(String(50))
    base_url = Column(String(500))
    config = Column(JSONB)
    
    # 采集状态
    is_active = Column(Boolean, default=True)
    last_crawl_time = Column(DateTime(timezone=True))
    crawl_interval_minutes = Column(Integer, default=60)
    
    # 统计信息
    total_crawled = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    fail_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class QuantScoreHistory(Base):
    """量化评分历史表"""
    __tablename__ = "quant_score_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    commodity = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    
    # 各维度评分
    fundamental_score = Column(Float)
    macro_score = Column(Float)
    sentiment_score = Column(Float)
    technical_score = Column(Float)
    geopolitical_score = Column(Float)
    
    # 综合评分
    composite_score = Column(Float, nullable=False)
    base_score = Column(Float)
    geo_adjustment = Column(Float)
    
    # 评级和信号
    rating = Column(String(20))
    signal = Column(String(20))
    confidence = Column(Float)
    
    # 权重配置
    weights = Column(JSONB)
    
    # 关键因子
    key_factors = Column(ARRAY(String))
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class Alert(Base):
    """预警表"""
    __tablename__ = "alerts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    level = Column(String(20), nullable=False, index=True)
    type = Column(String(50), nullable=False)
    commodity = Column(String(50), index=True)
    message = Column(String(500), nullable=False)
    details = Column(JSONB)
    
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    is_read = Column(Boolean, default=False)
    read_time = Column(DateTime(timezone=True))
    
    related_news = Column(ARRAY(String))
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class CommodityConfig(Base):
    """品种配置表"""
    __tablename__ = "commodity_configs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    name_en = Column(String(100))
    category = Column(String(50))
    
    # 权重配置
    fundamental_weight = Column(Float, default=0.30)
    macro_weight = Column(Float, default=0.20)
    sentiment_weight = Column(Float, default=0.20)
    technical_weight = Column(Float, default=0.20)
    geopolitical_weight = Column(Float, default=0.10)
    
    # 关键指标和数据源
    key_indicators = Column(ARRAY(String))
    data_sources = Column(ARRAY(String))
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

# ========== MongoDB集合 ==========

class MongoCollections:
    """MongoDB集合管理"""
    NEWS_CONTENT = "news_contents"
    NLP_RESULTS = "nlp_results"
    RAW_CRAWL_DATA = "raw_crawl_data"
    USER_UPLOADS = "user_uploads"
    ANALYTICS_CACHE = "analytics_cache"

async def get_mongodb():
    """获取MongoDB数据库实例"""
    if mongodb is None:
        raise Exception("MongoDB未连接")
    return mongodb

async def get_redis():
    """获取Redis客户端"""
    return redis_client

def get_db() -> Session:
    """获取PostgreSQL会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """初始化数据库"""
    try:
        # 创建SQL表
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建完成")
        
        # 如果配置了MongoDB，创建索引
        if MONGODB_URL:
            try:
                await mongodb[MongoCollections.NEWS_CONTENT].create_index("news_id", unique=True)
                await mongodb[MongoCollections.NLP_RESULTS].create_index("news_id", unique=True)
                await mongodb[MongoCollections.NLP_RESULTS].create_index("commodity")
                await mongodb[MongoCollections.NLP_RESULTS].create_index("timestamp")
                logger.info("MongoDB索引创建完成")
            except Exception as e:
                logger.warning(f"MongoDB连接失败（可选）: {e}")
        
        # 初始化品种配置
        await init_commodity_configs()
        
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise

def init_commodity_configs_sync():
    """同步初始化品种配置"""
    configs = [
        {
            "code": "WTI",
            "name": "WTI原油",
            "name_en": "WTI Crude Oil",
            "category": "crude_oil",
            "fundamental_weight": 0.30,
            "macro_weight": 0.15,
            "sentiment_weight": 0.20,
            "technical_weight": 0.20,
            "geopolitical_weight": 0.15,
            "key_indicators": ["EIA库存", "OPEC产量", "炼厂开工率", "库欣库存"],
            "data_sources": ["EIA", "CME", "Platts"]
        },
        {
            "code": "Brent",
            "name": "布伦特原油",
            "name_en": "Brent Crude Oil",
            "category": "crude_oil",
            "fundamental_weight": 0.30,
            "macro_weight": 0.15,
            "sentiment_weight": 0.20,
            "technical_weight": 0.20,
            "geopolitical_weight": 0.15,
            "key_indicators": ["IEA库存", "OPEC产量", "Brent-Dubai价差"],
            "data_sources": ["ICE", "IEA", "Platts"]
        },
        {
            "code": "HH",
            "name": "亨利港天然气",
            "name_en": "Henry Hub Natural Gas",
            "category": "natural_gas",
            "fundamental_weight": 0.35,
            "macro_weight": 0.10,
            "sentiment_weight": 0.20,
            "technical_weight": 0.25,
            "geopolitical_weight": 0.10,
            "key_indicators": ["EIA天然气库存", "产量", "HDD/CDD", "LNG出口"],
            "data_sources": ["EIA", "CME", "NOAA"]
        },
        {
            "code": "TTF",
            "name": "TTF天然气",
            "name_en": "TTF Natural Gas",
            "category": "natural_gas",
            "fundamental_weight": 0.35,
            "macro_weight": 0.10,
            "sentiment_weight": 0.25,
            "technical_weight": 0.20,
            "geopolitical_weight": 0.10,
            "key_indicators": ["欧洲库存", "俄管道气", "LNG进口", "气温"],
            "data_sources": ["ICE", "AGSI", "Platts"]
        },
        {
            "code": "JKM",
            "name": "JKM天然气",
            "name_en": "JKM LNG",
            "category": "natural_gas",
            "fundamental_weight": 0.35,
            "macro_weight": 0.10,
            "sentiment_weight": 0.25,
            "technical_weight": 0.20,
            "geopolitical_weight": 0.10,
            "key_indicators": ["日韩库存", "中国需求", "全球LNG供应"],
            "data_sources": ["Platts", "METI", "Kpler"]
        },
        {
            "code": "PG",
            "name": "丙烷",
            "name_en": "Propane",
            "category": "lpg",
            "fundamental_weight": 0.30,
            "macro_weight": 0.15,
            "sentiment_weight": 0.25,
            "technical_weight": 0.20,
            "geopolitical_weight": 0.10,
            "key_indicators": ["EIA丙烷库存", "产量", "出口", "石化需求"],
            "data_sources": ["EIA", "Platts", "OPIS"]
        },
        {
            "code": "CP",
            "name": "沙特CP",
            "name_en": "Saudi CP",
            "category": "lpg",
            "fundamental_weight": 0.35,
            "macro_weight": 0.15,
            "sentiment_weight": 0.20,
            "technical_weight": 0.20,
            "geopolitical_weight": 0.10,
            "key_indicators": ["沙特合同价", "中国进口", "运费"],
            "data_sources": ["Platts", "沙特阿美", "Kpler"]
        },
        {
            "code": "FEI",
            "name": "远东指数",
            "name_en": "Far East Index",
            "category": "lpg",
            "fundamental_weight": 0.30,
            "macro_weight": 0.15,
            "sentiment_weight": 0.25,
            "technical_weight": 0.20,
            "geopolitical_weight": 0.10,
            "key_indicators": ["FEI价格", "中国进口", "日韩需求"],
            "data_sources": ["Platts", "Argus", "Kpler"]
        }
    ]
    
    db = SessionLocal()
    try:
        for config in configs:
            existing = db.query(CommodityConfig).filter(
                CommodityConfig.code == config["code"]
            ).first()
            
            if not existing:
                db_config = CommodityConfig(**config)
                db.add(db_config)
        
        db.commit()
        logger.info("品种配置初始化完成")
    except Exception as e:
        logger.error(f"品种配置初始化失败: {e}")
        db.rollback()
    finally:
        db.close()

async def init_commodity_configs():
    """异步包装"""
    init_commodity_configs_sync()
