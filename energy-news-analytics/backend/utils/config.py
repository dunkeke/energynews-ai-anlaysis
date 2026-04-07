"""
配置管理
"""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    APP_NAME: str = "能源化工新闻分析系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://energy_user:energy_password@localhost:5432/energy_news"
    MONGODB_URL: str = "mongodb://admin:password@localhost:27017/energy_news?authSource=admin"
    REDIS_URL: str = "redis://localhost:6379"
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API配置
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["*"]
    
    # 采集配置
    CRAWL_INTERVAL_MINUTES: int = 15
    MAX_CRAWL_WORKERS: int = 5
    
    # NLP配置
    NLP_MODEL_PATH: str = "./nlp-models"
    SENTIMENT_MODEL: str = "uer/roberta-base-finetuned-jd-binary-chinese"
    
    # 量化配置
    SCORE_CALCULATION_INTERVAL: int = 5  # 分钟
    HISTORICAL_DATA_DAYS: int = 90
    
    # 预警配置
    ALERT_CHECK_INTERVAL: int = 1  # 分钟
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """获取配置实例"""
    return Settings()

# 全局配置实例
settings = get_settings()
