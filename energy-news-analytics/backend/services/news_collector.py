"""
新闻采集服务 - 自动采集 + 手工导入
"""
import os
import re
import hashlib
import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
from loguru import logger

# 文档处理库
try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import trafilatura
    TRAFILATURA_AVAILABLE = True
except ImportError:
    TRAFILATURA_AVAILABLE = False

from models.database import get_mongodb, MongoCollections
from models.schemas import NewsItem

class NewsCollectorService:
    """新闻采集服务"""
    
    # 数据源配置
    DATA_SOURCES = {
        "bloomberg": {
            "name": "Bloomberg",
            "type": "api",
            "base_url": "https://api.bloomberg.com",
            "priority": "high"
        },
        "reuters": {
            "name": "Reuters",
            "type": "api",
            "base_url": "https://api.reuters.com",
            "priority": "high"
        },
        "platts": {
            "name": "Platts",
            "type": "api",
            "base_url": "https://api.platts.com",
            "priority": "high"
        },
        "eia": {
            "name": "EIA",
            "type": "api",
            "base_url": "https://api.eia.gov",
            "priority": "high"
        },
        "sina_finance": {
            "name": "新浪财经",
            "type": "rss",
            "base_url": "https://finance.sina.com.cn",
            "priority": "high"
        },
        "eastmoney": {
            "name": "东方财富",
            "type": "api",
            "base_url": "https://api.eastmoney.com",
            "priority": "high"
        },
        "wallstreetcn": {
            "name": "华尔街见闻",
            "type": "api",
            "base_url": "https://api.wallstreetcn.com",
            "priority": "high"
        }
    }
    
    def __init__(self):
        self.mongodb = None
        self.session = None
        self.initialized = False
    
    async def initialize(self):
        """初始化采集服务"""
        try:
            self.mongodb = await get_mongodb()
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
            self.initialized = True
            logger.info("新闻采集服务初始化完成")
        except Exception as e:
            logger.error(f"新闻采集服务初始化失败: {e}")
            raise
    
    async def import_content(
        self,
        import_type: str,
        content: Optional[str] = None,
        file: Optional[Any] = None,
        source: str = "user_import",
        commodities: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        导入内容（URL/文本/PDF）
        """
        try:
            if import_type == "url":
                return await self._import_from_url(content, source, commodities)
            elif import_type == "text":
                return await self._import_from_text(content, source, commodities)
            elif import_type == "pdf":
                return await self._import_from_pdf(file, source, commodities)
            else:
                raise ValueError(f"不支持的导入类型: {import_type}")
        except Exception as e:
            logger.error(f"导入内容失败: {e}")
            raise
    
    async def _import_from_url(
        self,
        url: str,
        source: str,
        commodities: Optional[List[str]]
    ) -> Dict[str, Any]:
        """从URL导入"""
        try:
            # 获取页面内容
            async with self.session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"获取页面失败: {response.status}")
                
                html = await response.text()
            
            # 提取文章内容
            article = await self._extract_from_html(html, url)
            
            # 保存到数据库
            news_id = await self._save_article(article, source, commodities)
            
            return {
                "news_id": news_id,
                "title": article.get("title"),
                "source": source,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"从URL导入失败: {e}")
            raise
    
    async def _import_from_text(
        self,
        text: str,
        source: str,
        commodities: Optional[List[str]]
    ) -> Dict[str, Any]:
        """从文本导入"""
        try:
            # 生成标题（前50字符）
            title = text[:50] + "..." if len(text) > 50 else text
            
            article = {
                "title": title,
                "content": text,
                "source_url": None,
                "publish_time": datetime.now()
            }
            
            # 保存到数据库
            news_id = await self._save_article(article, source, commodities)
            
            return {
                "news_id": news_id,
                "title": title,
                "source": source,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"从文本导入失败: {e}")
            raise
    
    async def _import_from_pdf(
        self,
        file: Any,
        source: str,
        commodities: Optional[List[str]]
    ) -> Dict[str, Any]:
        """从PDF导入"""
        try:
            if not PDF_AVAILABLE:
                raise Exception("PDF处理库不可用")
            
            # 读取PDF文件
            contents = await file.read()
            
            # 保存临时文件
            temp_path = f"/tmp/{file.filename}"
            with open(temp_path, "wb") as f:
                f.write(contents)
            
            # 提取文本
            text_content = ""
            with pdfplumber.open(temp_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content += text + "\n"
            
            # 删除临时文件
            os.remove(temp_path)
            
            # 生成标题
            title = file.filename.replace(".pdf", "")
            
            article = {
                "title": title,
                "content": text_content,
                "source_url": None,
                "publish_time": datetime.now()
            }
            
            # 保存到数据库
            news_id = await self._save_article(article, source, commodities)
            
            return {
                "news_id": news_id,
                "title": title,
                "source": source,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"从PDF导入失败: {e}")
            raise
    
    async def _extract_from_html(self, html: str, url: str) -> Dict[str, Any]:
        """从HTML提取文章内容"""
        try:
            if TRAFILATURA_AVAILABLE:
                # 使用trafilatura提取
                result = trafilatura.extract(
                    html,
                    url=url,
                    include_comments=False,
                    include_tables=True,
                    output_format="json"
                )
                
                if result:
                    import json
                    data = json.loads(result)
                    return {
                        "title": data.get("title", ""),
                        "content": data.get("text", ""),
                        "source_url": url,
                        "publish_time": self._parse_date(data.get("date")),
                        "author": data.get("author")
                    }
            
            # 备用方案：简单提取
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'lxml')
            
            title = soup.title.string if soup.title else ""
            
            # 尝试找到正文
            content = ""
            for tag in ['article', 'main', '.content', '.article', '#content']:
                element = soup.select_one(tag)
                if element:
                    content = element.get_text()
                    break
            
            if not content:
                content = soup.get_text()
            
            return {
                "title": title,
                "content": content,
                "source_url": url,
                "publish_time": None
            }
        except Exception as e:
            logger.error(f"HTML提取失败: {e}")
            raise
    
    async def _save_article(
        self,
        article: Dict[str, Any],
        source: str,
        commodities: Optional[List[str]]
    ) -> str:
        """保存文章到数据库"""
        try:
            # 生成唯一ID
            news_id = hashlib.md5(
                f"{article['title']}{article['source_url']}{datetime.now()}".encode()
            ).hexdigest()
            
            # 准备文档
            doc = {
                "_id": news_id,
                "title": article.get("title", ""),
                "content": article.get("content", ""),
                "source": source,
                "source_url": article.get("source_url"),
                "publish_time": article.get("publish_time"),
                "crawl_time": datetime.now(),
                "commodity_tags": commodities or [],
                "is_analyzed": False,
                "is_user_input": True
            }
            
            # 保存到MongoDB
            await self.mongodb[MongoCollections.NEWS_CONTENT].insert_one(doc)
            
            logger.info(f"文章已保存: {news_id}")
            return news_id
        except Exception as e:
            logger.error(f"保存文章失败: {e}")
            raise
    
    async def get_news(
        self,
        commodity: Optional[str] = None,
        source: Optional[str] = None,
        sentiment: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[NewsItem]:
        """获取新闻列表"""
        try:
            # 构建查询条件
            query = {}
            
            if commodity:
                query["commodity_tags"] = commodity
            
            if source:
                query["source"] = source
            
            if start_date or end_date:
                query["crawl_time"] = {}
                if start_date:
                    query["crawl_time"]["$gte"] = start_date
                if end_date:
                    query["crawl_time"]["$lte"] = end_date
            
            # 查询MongoDB
            cursor = self.mongodb[MongoCollections.NEWS_CONTENT].find(query)
            cursor = cursor.sort("crawl_time", -1).skip(offset).limit(limit)
            
            news_list = []
            async for doc in cursor:
                news_list.append(NewsItem(
                    id=str(doc.get("_id")),
                    title=doc.get("title", ""),
                    content=doc.get("content", "")[:500],  # 截断内容
                    source=doc.get("source", ""),
                    source_url=doc.get("source_url"),
                    publish_time=doc.get("publish_time"),
                    crawl_time=doc.get("crawl_time"),
                    commodity_tags=doc.get("commodity_tags", []),
                    is_analyzed=doc.get("is_analyzed", False)
                ))
            
            return news_list
        except Exception as e:
            logger.error(f"获取新闻列表失败: {e}")
            raise
    
    async def get_news_by_id(self, news_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取新闻"""
        try:
            doc = await self.mongodb[MongoCollections.NEWS_CONTENT].find_one({"_id": news_id})
            return doc
        except Exception as e:
            logger.error(f"获取新闻失败: {e}")
            return None
    
    async def update_analysis_result(self, news_id: str, nlp_result: Any):
        """更新新闻分析结果"""
        try:
            update_data = {
                "is_analyzed": True,
                "analysis_time": datetime.now(),
                "nlp_result": {
                    "sentiment": nlp_result.sentiment.overall.value if hasattr(nlp_result.sentiment, 'overall') else None,
                    "sentiment_score": nlp_result.sentiment.intensity if hasattr(nlp_result.sentiment, 'intensity') else None,
                    "keywords": [kw.get("word") for kw in nlp_result.keywords] if hasattr(nlp_result, 'keywords') else [],
                    "entities": [{"text": e.text, "type": e.type} for e in nlp_result.entities] if hasattr(nlp_result, 'entities') else [],
                    "dimensions": nlp_result.dimensions if hasattr(nlp_result, 'dimensions') else {},
                    "overall_score": nlp_result.overall_score if hasattr(nlp_result, 'overall_score') else None
                }
            }
            
            await self.mongodb[MongoCollections.NEWS_CONTENT].update_one(
                {"_id": news_id},
                {"$set": update_data}
            )
            
            logger.info(f"新闻分析结果已更新: {news_id}")
        except Exception as e:
            logger.error(f"更新分析结果失败: {e}")
            raise
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """解析日期字符串"""
        if not date_str:
            return None
        
        formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%Y年%m月%d日"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        
        return None
    
    async def close(self):
        """关闭服务"""
        if self.session:
            await self.session.close()
        logger.info("新闻采集服务已关闭")
