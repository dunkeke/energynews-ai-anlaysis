# 能源化工新闻分析软件 - 数据工程方案

## 目录
1. [数据采集模块设计](#1-数据采集模块设计)
2. [用户输入处理模块](#2-用户输入处理模块)
3. [数据清洗和预处理流程](#3-数据清洗和预处理流程)
4. [数据存储方案](#4-数据存储方案)
5. [数据更新和版本管理](#5-数据更新和版本管理)

---

## 1. 数据采集模块设计

### 1.1 数据源列表

#### 1.1.1 国际权威财经媒体

| 数据源名称 | 网址 | 内容类型 | 更新频率 | 采集方式 | 优先级 |
|-----------|------|---------|---------|---------|--------|
| Bloomberg | bloomberg.com | 实时新闻、市场分析 | 实时 | API/爬虫 | 高 |
| Reuters | reuters.com | 新闻、分析报告 | 实时 | API | 高 |
| Financial Times | ft.com | 深度分析、评论 | 每日 | 爬虫 | 高 |
| Wall Street Journal | wsj.com | 市场新闻 | 实时 | API | 中 |
| CNBC | cnbc.com | 市场快讯 | 实时 | API | 中 |

#### 1.1.2 能源行业专业媒体

| 数据源名称 | 网址 | 内容类型 | 更新频率 | 采集方式 | 优先级 |
|-----------|------|---------|---------|---------|--------|
| Platts (S&P Global) | spglobal.com/platts | 价格评估、市场分析 | 每日 | API | 高 |
| Argus Media | argusmedia.com | 价格报告、新闻 | 每日 | API | 高 |
| Energy Intelligence | energyintel.com | 行业分析 | 每日 | API | 高 |
| Oil Price | oilprice.com | 新闻、分析 | 每日 | RSS/API | 中 |
| Rigzone | rigzone.com | 行业新闻 | 每日 | 爬虫 | 中 |
| World Oil | worldoil.com | 行业动态 | 每日 | 爬虫 | 中 |
| Natural Gas Intelligence | naturalgasintel.com | 天然气专项 | 每日 | 爬虫 | 高 |
| LNG World News | lngworldnews.com | LNG专项 | 每日 | RSS | 中 |

#### 1.1.3 交易所与官方数据源

| 数据源名称 | 网址 | 内容类型 | 更新频率 | 采集方式 | 优先级 |
|-----------|------|---------|---------|---------|--------|
| CME Group | cmegroup.com | 期货数据、公告 | 实时 | API | 高 |
| ICE (洲际交易所) | theice.com | 期货数据、公告 | 实时 | API | 高 |
| NYMEX | nymex.com | 原油期货数据 | 实时 | API | 高 |
| EIA (美国能源信息署) | eia.gov | 官方数据、报告 | 每周/月 | API | 高 |
| IEA (国际能源署) | iea.org | 市场报告 | 月度 | API/爬虫 | 高 |
| OPEC | opec.org | 月度报告 | 月度 | 爬虫 | 高 |

#### 1.1.4 国内财经媒体

| 数据源名称 | 网址 | 内容类型 | 更新频率 | 采集方式 | 优先级 |
|-----------|------|---------|---------|---------|--------|
| 新浪财经 | finance.sina.com.cn | 综合财经新闻 | 实时 | API/爬虫 | 高 |
| 东方财富 | eastmoney.com | 市场分析 | 实时 | API | 高 |
| 财新网 | caixin.com | 深度报道 | 每日 | 爬虫 | 高 |
| 第一财经 | yicai.com | 财经新闻 | 实时 | API | 高 |
| 华尔街见闻 | wallstreetcn.com | 快讯、分析 | 实时 | API | 高 |
| 期货日报 | qhrb.com.cn | 期货专项 | 每日 | 爬虫 | 高 |

#### 1.1.5 国内能源行业网站

| 数据源名称 | 网址 | 内容类型 | 更新频率 | 采集方式 | 优先级 |
|-----------|------|---------|---------|---------|--------|
| 金联创 | 315i.com | 石化行业分析 | 每日 | API | 高 |
| 隆众资讯 | oilchem.net | 石化数据、分析 | 每日 | API | 高 |
| 卓创资讯 | sci99.com | 大宗商品分析 | 每日 | API | 高 |
| 百川盈孚 | baichuan365.com | 行业数据 | 每日 | API | 中 |
| 中国石油新闻中心 | news.cnpc.com.cn | 行业新闻 | 每日 | 爬虫 | 中 |
| 中国石化新闻网 | sinopecnews.com.cn | 行业新闻 | 每日 | 爬虫 | 中 |

### 1.2 爬虫/API采集策略

#### 1.2.1 架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                    数据采集调度中心                               │
│                    (Scheduler/Celery Beat)                       │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   API采集器    │    │   爬虫引擎    │    │  RSS采集器    │
│   (RESTful)   │    │  (Scrapy)    │    │  (Feedparser) │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │   消息队列         │
                    │  (Redis/RabbitMQ) │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │   数据处理器       │
                    │  (Celery Workers) │
                    └────────────────────┘
```

#### 1.2.2 API采集策略

```python
# API采集器基类设计
class BaseAPIFetcher:
    """API数据采集基类"""
    
    def __init__(self, source_config):
        self.source_name = source_config['name']
        self.base_url = source_config['base_url']
        self.api_key = source_config.get('api_key')
        self.rate_limit = source_config.get('rate_limit', 1)  # 请求/秒
        self.retry_count = source_config.get('retry_count', 3)
        
    async def fetch(self, endpoint, params=None):
        """执行API请求"""
        headers = self._build_headers()
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.retry_count):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, params=params) as resp:
                        if resp.status == 200:
                            return await resp.json()
                        elif resp.status == 429:  # Rate limited
                            await asyncio.sleep(2 ** attempt)
                        else:
                            resp.raise_for_status()
            except Exception as e:
                logger.error(f"API fetch error: {e}")
                if attempt == self.retry_count - 1:
                    raise
                    
    def _build_headers(self):
        return {
            'Authorization': f'Bearer {self.api_key}' if self.api_key else '',
            'User-Agent': 'EnergyNewsBot/1.0',
            'Accept': 'application/json'
        }
```

#### 1.2.3 爬虫策略

```python
# Scrapy爬虫配置
class EnergyNewsSpider(scrapy.Spider):
    """能源新闻爬虫"""
    
    name = 'energy_news'
    
    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 2,  # 2秒延迟
        'CONCURRENT_REQUESTS': 4,
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429],
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        },
        'ITEM_PIPELINES': {
            'pipelines.NewsValidationPipeline': 100,
            'pipelines.DuplicateFilterPipeline': 200,
            'pipelines.DataStoragePipeline': 300,
        }
    }
    
    def parse(self, response):
        """解析新闻列表页"""
        articles = response.css('article.news-item')
        for article in articles:
            yield {
                'title': article.css('h2.title::text').get(),
                'url': article.css('a::attr(href)').get(),
                'publish_time': article.css('time::attr(datetime)').get(),
                'summary': article.css('p.summary::text').get(),
            }
```

#### 1.2.4 反爬虫应对策略

| 策略 | 实现方式 | 适用场景 |
|------|---------|---------|
| 请求频率控制 | 随机延迟1-5秒 | 所有爬虫 |
| User-Agent轮换 | 使用fake-useragent库 | 所有爬虫 |
| IP代理池 | 自建/购买代理服务 | 高频采集 |
| Cookie管理 | 维护登录会话 | 需要认证 |
| 验证码识别 | 第三方OCR服务 | 触发验证时 |
| 浏览器模拟 | Playwright/Selenium | 动态渲染页面 |

### 1.3 采集频率和增量更新机制

#### 1.3.1 采集频率矩阵

| 数据源类型 | 采集频率 | 说明 |
|-----------|---------|------|
| 实时新闻API | 5分钟 | 高频市场快讯 |
| 财经新闻网站 | 15分钟 | 重要新闻更新 |
| 行业分析报告 | 1小时 | 深度分析文章 |
| 交易所公告 | 10分钟 | 市场公告 |
| 官方数据发布 | 每日/每周 | EIA/IEA报告 |
| 价格数据 | 实时 | 期货价格 |

#### 1.3.2 增量更新机制

```python
# 增量更新管理器
class IncrementalUpdateManager:
    """管理增量更新状态"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.last_update_key = "last_update:{source}"
        
    def get_last_update_time(self, source_name):
        """获取上次更新时间"""
        key = self.last_update_key.format(source=source_name)
        timestamp = self.redis.get(key)
        return datetime.fromisoformat(timestamp) if timestamp else None
        
    def set_last_update_time(self, source_name, timestamp=None):
        """设置更新时间"""
        key = self.last_update_key.format(source=source_name)
        timestamp = timestamp or datetime.utcnow()
        self.redis.set(key, timestamp.isoformat())
        
    def should_update(self, source_name, interval_minutes):
        """判断是否需要更新"""
        last_update = self.get_last_update_time(source_name)
        if not last_update:
            return True
        return datetime.utcnow() - last_update >= timedelta(minutes=interval_minutes)
```

#### 1.3.3 去重策略

```python
# 内容去重管理器
class DeduplicationManager:
    """管理内容去重"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.url_set = "dedup:urls"
        self.content_hash_set = "dedup:content_hash"
        
    def is_duplicate_url(self, url):
        """检查URL是否已存在"""
        return self.redis.sismember(self.url_set, self._normalize_url(url))
        
    def is_duplicate_content(self, content):
        """基于内容相似度检查"""
        content_hash = self._compute_simhash(content)
        # 检查相似度
        similar_hashes = self.redis.smembers(self.content_hash_set)
        for existing_hash in similar_hashes:
            if self._hamming_distance(content_hash, existing_hash) < 3:
                return True
        return False
        
    def add_url(self, url):
        """添加URL到去重集合"""
        self.redis.sadd(self.url_set, self._normalize_url(url))
        # 设置过期时间（保留30天）
        self.redis.expire(self.url_set, 30 * 24 * 3600)
        
    def _compute_simhash(self, content):
        """计算SimHash值"""
        # 使用jieba分词 + simhash算法
        words = jieba.lcut(content)
        return SimHash(words).value
```

---

## 2. 用户输入处理模块

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     用户输入处理中心                              │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   URL处理器   │    │   文本处理器  │    │   PDF处理器   │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │   统一内容提取器   │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │   数据标准化       │
                    └────────────────────┘
```

### 2.2 URL内容提取方案

#### 2.2.1 提取流程

```python
class URLContentExtractor:
    """URL内容提取器"""
    
    def __init__(self):
        self.extractors = {
            'article': ArticleExtractor(),
            'video': VideoExtractor(),
            'pdf': PDFLinkExtractor(),
        }
        
    async def extract(self, url):
        """提取URL内容"""
        # 1. 获取页面内容
        html = await self._fetch_page(url)
        
        # 2. 识别内容类型
        content_type = self._detect_content_type(html)
        
        # 3. 使用对应提取器
        extractor = self.extractors.get(content_type, self.extractors['article'])
        content = extractor.extract(html, url)
        
        # 4. 元数据提取
        metadata = self._extract_metadata(html, url)
        
        return {
            'url': url,
            'title': content.get('title'),
            'content': content.get('content'),
            'publish_time': content.get('publish_time'),
            'author': content.get('author'),
            'images': content.get('images', []),
            'metadata': metadata,
            'extracted_at': datetime.utcnow()
        }
        
    async def _fetch_page(self, url, retries=3):
        """获取页面内容"""
        headers = {
            'User-Agent': UserAgent().random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        
        for attempt in range(retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, timeout=30) as resp:
                        if resp.status == 200:
                            return await resp.text()
            except Exception as e:
                logger.warning(f"Fetch attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(2 ** attempt)
                
        raise Exception(f"Failed to fetch {url} after {retries} attempts")
```

#### 2.2.2 文章内容提取

```python
class ArticleExtractor:
    """文章提取器 - 基于readability-lxml和trafilatura"""
    
    def extract(self, html, url):
        """提取文章内容"""
        # 使用trafilatura提取
        result = trafilatura.extract(
            html,
            url=url,
            include_comments=False,
            include_tables=True,
            include_images=True,
            output_format='json'
        )
        
        if result:
            data = json.loads(result)
            return {
                'title': data.get('title'),
                'content': data.get('text'),
                'publish_time': self._parse_date(data.get('date')),
                'author': data.get('author'),
                'images': data.get('images', []),
            }
            
        # 备用方案：readability
        doc = Document(html)
        return {
            'title': doc.title(),
            'content': doc.summary(),
            'publish_time': None,
            'author': None,
            'images': [],
        }
```

#### 2.2.3 特殊网站适配

```python
class SiteSpecificExtractor:
    """特定网站适配器"""
    
    SITE_RULES = {
        'weixin.qq.com': {
            'title_selector': 'h2.rich_media_title',
            'content_selector': 'div.rich_media_content',
            'date_selector': 'em#publish_time',
        },
        'zhihu.com': {
            'title_selector': 'h1.Post-Title',
            'content_selector': 'div.Post-RichTextContainer',
            'date_selector': 'div.ContentItem-time',
        },
        'xueqiu.com': {
            'title_selector': 'h1.article__title',
            'content_selector': 'div.article__content',
            'date_selector': 'span.article__time',
        },
    }
    
    def extract(self, html, url):
        """根据网站使用特定规则提取"""
        domain = self._extract_domain(url)
        rules = self.SITE_RULES.get(domain)
        
        if rules:
            soup = BeautifulSoup(html, 'lxml')
            return {
                'title': self._safe_select(soup, rules['title_selector']),
                'content': self._safe_select(soup, rules['content_selector']),
                'publish_time': self._safe_select(soup, rules['date_selector']),
            }
        return None
```

### 2.3 文本文件处理方案

```python
class TextFileProcessor:
    """文本文件处理器"""
    
    SUPPORTED_FORMATS = ['.txt', '.md', '.doc', '.docx', '.rtf']
    
    def process(self, file_path):
        """处理文本文件"""
        ext = Path(file_path).suffix.lower()
        
        if ext == '.txt' or ext == '.md':
            return self._process_plain_text(file_path)
        elif ext in ['.doc', '.docx']:
            return self._process_word(file_path)
        elif ext == '.rtf':
            return self._process_rtf(file_path)
        else:
            raise ValueError(f"Unsupported format: {ext}")
            
    def _process_plain_text(self, file_path):
        """处理纯文本"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return {
            'title': Path(file_path).stem,
            'content': content,
            'file_type': 'text',
            'word_count': len(content),
            'processed_at': datetime.utcnow()
        }
        
    def _process_word(self, file_path):
        """处理Word文档"""
        doc = docx.Document(file_path)
        
        # 提取文本
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        
        # 提取表格
        tables = []
        for table in doc.tables:
            table_data = []
            for row in table.rows:
                row_data = [cell.text for cell in row.cells]
                table_data.append(row_data)
            tables.append(table_data)
            
        # 提取元数据
        metadata = {
            'author': doc.core_properties.author,
            'created': doc.core_properties.created,
            'modified': doc.core_properties.modified,
        }
        
        return {
            'title': doc.core_properties.title or Path(file_path).stem,
            'content': '\n'.join(paragraphs),
            'tables': tables,
            'metadata': metadata,
            'file_type': 'word',
            'processed_at': datetime.utcnow()
        }
```

### 2.4 PDF解析方案

```python
class PDFProcessor:
    """PDF文档处理器"""
    
    def __init__(self):
        self.ocr_enabled = True
        self.ocr_engine = PaddleOCR(use_angle_cls=True, lang='ch')
        
    def process(self, file_path, extract_images=True, ocr_fallback=True):
        """处理PDF文件"""
        results = {
            'file_path': file_path,
            'file_name': Path(file_path).name,
            'pages': [],
            'metadata': {},
            'tables': [],
            'images': [],
        }
        
        # 1. 提取元数据
        results['metadata'] = self._extract_metadata(file_path)
        
        # 2. 逐页处理
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_data = self._process_page(page, page_num, extract_images)
                results['pages'].append(page_data)
                
        # 3. 合并内容
        results['full_text'] = '\n'.join([p['text'] for p in results['pages']])
        results['word_count'] = len(results['full_text'])
        
        return results
        
    def _process_page(self, page, page_num, extract_images):
        """处理单页"""
        page_data = {
            'page_number': page_num,
            'text': '',
            'tables': [],
            'images': [],
        }
        
        # 提取文本
        text = page.extract_text()
        
        # 如果文本为空或太少，尝试OCR
        if not text or len(text.strip()) < 50:
            text = self._ocr_page(page)
            
        page_data['text'] = text
        
        # 提取表格
        tables = page.extract_tables()
        if tables:
            page_data['tables'] = tables
            
        # 提取图片
        if extract_images:
            images = self._extract_images(page)
            page_data['images'] = images
            
        return page_data
        
    def _ocr_page(self, page):
        """使用OCR识别页面"""
        # 将页面转为图片
        pil_image = page.to_image(resolution=150).original
        
        # OCR识别
        result = self.ocr_engine.ocr(np.array(pil_image), cls=True)
        
        # 提取文本
        texts = []
        if result:
            for line in result[0]:
                if line:
                    texts.append(line[1][0])  # 提取文本内容
                    
        return '\n'.join(texts)
```

---

## 3. 数据清洗和预处理流程

### 3.1 清洗流程架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     原始数据输入                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  阶段1: 格式标准化                                                │
│  - 编码统一(UTF-8)                                               │
│  - HTML标签清理                                                   │
│  - 特殊字符处理                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  阶段2: 内容清洗                                                  │
│  - 广告/导航去除                                                  │
│  - 重复内容检测                                                   │
│  - 噪声文本过滤                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  阶段3: 内容增强                                                  │
│  - 实体识别(NER)                                                 │
│  - 关键词提取                                                     │
│  - 情感分析                                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  阶段4: 质量验证                                                  │
│  - 完整性检查                                                     │
│  - 准确性验证                                                     │
│  - 去重验证                                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     清洗后数据输出                                │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 清洗规则实现

```python
class DataCleaner:
    """数据清洗器"""
    
    def __init__(self):
        self.html_cleaner = HTMLCleaner()
        self.text_cleaner = TextCleaner()
        self.ner_pipeline = NERPipeline()
        
    def clean(self, raw_data):
        """执行完整清洗流程"""
        # 阶段1: 格式标准化
        data = self._normalize_format(raw_data)
        
        # 阶段2: 内容清洗
        data = self._clean_content(data)
        
        # 阶段3: 内容增强
        data = self._enrich_content(data)
        
        # 阶段4: 质量验证
        if not self._validate_quality(data):
            raise ValueError("Data quality validation failed")
            
        return data
        
    def _normalize_format(self, data):
        """格式标准化"""
        # 编码统一
        if isinstance(data.get('content'), bytes):
            data['content'] = data['content'].decode('utf-8', errors='ignore')
            
        # HTML清理
        if data.get('content_type') == 'html':
            data['content'] = self.html_cleaner.clean(data['content'])
            
        # 特殊字符处理
        data['content'] = self._normalize_whitespace(data['content'])
        
        return data
        
    def _clean_content(self, data):
        """内容清洗"""
        content = data.get('content', '')
        
        # 去除广告和导航
        content = self.text_cleaner.remove_ads(content)
        content = self.text_cleaner.remove_navigation(content)
        
        # 去除噪声文本
        content = self.text_cleaner.remove_noise(content)
        
        # 去除重复段落
        content = self.text_cleaner.remove_duplicate_paragraphs(content)
        
        data['content'] = content
        data['cleaned_at'] = datetime.utcnow()
        
        return data
        
    def _enrich_content(self, data):
        """内容增强"""
        content = data.get('content', '')
        
        # 命名实体识别
        entities = self.ner_pipeline.extract_entities(content)
        data['entities'] = entities
        
        # 品种标签提取
        data['commodity_tags'] = self._extract_commodity_tags(content, entities)
        
        # 关键词提取
        data['keywords'] = self._extract_keywords(content)
        
        # 情感分析
        data['sentiment'] = self._analyze_sentiment(content)
        
        return data
```

### 3.3 品种标签提取

```python
class CommodityTagExtractor:
    """能源化工品种标签提取器"""
    
    # 品种关键词映射
    COMMODITY_PATTERNS = {
        '原油': {
            'keywords': ['原油', '石油', 'oil', 'crude', 'petroleum'],
            'sub_types': {
                'WTI': ['WTI', '西德克萨斯', 'West Texas'],
                'Brent': ['Brent', '布伦特', '北海原油'],
            }
        },
        '天然气': {
            'keywords': ['天然气', 'natural gas', '燃气'],
            'sub_types': {
                'JKM': ['JKM', '日韩基准', 'Japan Korea Marker'],
                'HH': ['Henry Hub', 'HH', '亨利港'],
                'TTF': ['TTF', 'Title Transfer Facility'],
            }
        },
        '液化气': {
            'keywords': ['液化气', 'LPG', '液化石油气', 'liquefied petroleum'],
            'sub_types': {
                'PG': ['PG', 'Propane', '丙烷'],
                'PP': ['PP', '丙烯', 'Propylene'],
                'MB': ['MB', 'Mont Belvieu'],
                'FEI': ['FEI', 'Far East Index'],
                'CP': ['CP', 'Contract Price', '沙特合同价'],
            }
        },
        '成品油': {
            'keywords': ['成品油', '汽油', '柴油', '煤油', '燃料油', 'gasoline', 'diesel'],
            'sub_types': {
                '汽油': ['汽油', 'gasoline', 'petrol'],
                '柴油': ['柴油', 'diesel'],
                '燃料油': ['燃料油', 'fuel oil'],
            }
        },
    }
    
    def extract(self, content):
        """提取品种标签"""
        tags = []
        content_lower = content.lower()
        
        for commodity, config in self.COMMODITY_PATTERNS.items():
            # 检查主品种
            if any(kw.lower() in content_lower for kw in config['keywords']):
                tag = {'commodity': commodity, 'sub_types': []}
                
                # 检查子品种
                for sub_type, sub_keywords in config['sub_types'].items():
                    if any(sk.lower() in content_lower for sk in sub_keywords):
                        tag['sub_types'].append(sub_type)
                        
                tags.append(tag)
                
        return tags
```

### 3.4 数据质量验证

```python
class DataQualityValidator:
    """数据质量验证器"""
    
    VALIDATION_RULES = {
        'title': {
            'required': True,
            'min_length': 5,
            'max_length': 200,
        },
        'content': {
            'required': True,
            'min_length': 100,
            'max_length': 50000,
        },
        'publish_time': {
            'required': False,
            'max_age_days': 365,  # 最多1年前的文章
        },
    }
    
    def validate(self, data):
        """执行质量验证"""
        errors = []
        
        for field, rules in self.VALIDATION_RULES.items():
            value = data.get(field)
            
            # 必填检查
            if rules.get('required') and not value:
                errors.append(f"{field} is required")
                continue
                
            if not value:
                continue
                
            # 长度检查
            if 'min_length' in rules:
                if len(str(value)) < rules['min_length']:
                    errors.append(f"{field} is too short (min {rules['min_length']})")
                    
            if 'max_length' in rules:
                if len(str(value)) > rules['max_length']:
                    errors.append(f"{field} is too long (max {rules['max_length']})")
                    
        # 内容质量评分
        quality_score = self._calculate_quality_score(data)
        if quality_score < 0.5:
            errors.append(f"Content quality score too low: {quality_score}")
            
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'quality_score': quality_score,
        }
        
    def _calculate_quality_score(self, data):
        """计算内容质量评分"""
        score = 1.0
        content = data.get('content', '')
        
        # 检查内容完整性
        if len(content) < 500:
            score *= 0.8
            
        # 检查可读性
        sentences = content.split('。')
        avg_sentence_length = len(content) / max(len(sentences), 1)
        if avg_sentence_length > 100:  # 句子太长
            score *= 0.9
            
        # 检查信息密度
        if data.get('entities'):
            entity_density = len(data['entities']) / len(content) * 1000
            if entity_density < 1:  # 实体太少
                score *= 0.9
                
        return score
```

---

## 4. 数据存储方案

### 4.1 数据库选型

#### 4.1.1 技术栈选择

| 数据类型 | 存储方案 | 选型理由 |
|---------|---------|---------|
| 结构化数据 | PostgreSQL | 支持JSON、全文搜索、事务 |
| 文档内容 | MongoDB | 灵活Schema、适合非结构化内容 |
| 缓存数据 | Redis | 高性能、支持多种数据结构 |
| 搜索索引 | Elasticsearch | 全文搜索、聚合分析 |
| 时序数据 | InfluxDB/TimescaleDB | 价格数据时间序列存储 |
| 文件存储 | MinIO/S3 | 对象存储PDF/图片 |

#### 4.1.2 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        应用层                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   PostgreSQL  │    │   MongoDB     │    │ Elasticsearch │
│  (主数据库)   │    │  (文档存储)   │    │  (搜索引擎)   │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │      Redis         │
                    │    (缓存层)        │
                    └────────────────────┘
```

### 4.2 数据模型设计

#### 4.2.1 PostgreSQL - 核心数据模型

```sql
-- 文章表
CREATE TABLE articles (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID DEFAULT gen_random_uuid() UNIQUE,
    title VARCHAR(500) NOT NULL,
    source_name VARCHAR(100) NOT NULL,
    source_url VARCHAR(500),
    original_url VARCHAR(500) UNIQUE,
    content_hash VARCHAR(64) UNIQUE,
    
    -- 时间字段
    publish_time TIMESTAMP WITH TIME ZONE,
    crawl_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    update_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 内容元数据
    content_type VARCHAR(20) DEFAULT 'news',  -- news, analysis, report
    language VARCHAR(10) DEFAULT 'zh',
    word_count INTEGER,
    
    -- 质量评分
    quality_score DECIMAL(3,2),
    is_valid BOOLEAN DEFAULT TRUE,
    
    -- 用户输入标记
    is_user_input BOOLEAN DEFAULT FALSE,
    user_id BIGINT REFERENCES users(id),
    
    -- 软删除
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    -- 全文搜索向量
    search_vector tsvector,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 文章内容表(大字段分离)
CREATE TABLE article_contents (
    article_id BIGINT PRIMARY KEY REFERENCES articles(id) ON DELETE CASCADE,
    content TEXT,
    summary TEXT,
    cleaned_content TEXT,
    metadata JSONB
);

-- 品种标签表
CREATE TABLE commodity_tags (
    id SERIAL PRIMARY KEY,
    article_id BIGINT REFERENCES articles(id) ON DELETE CASCADE,
    commodity_type VARCHAR(50) NOT NULL,  -- 原油、天然气、液化气、成品油
    sub_type VARCHAR(50),  -- WTI, Brent, JKM等
    confidence DECIMAL(3,2) DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 分析维度表
CREATE TABLE analysis_dimensions (
    id SERIAL PRIMARY KEY,
    article_id BIGINT REFERENCES articles(id) ON DELETE CASCADE,
    dimension_type VARCHAR(50) NOT NULL,  -- fundamental, macro, sentiment, technical, geopolitical
    relevance_score DECIMAL(3,2),
    extracted_keywords JSONB,
    sentiment_score DECIMAL(3,2),  -- -1 到 1
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 数据源配置表
CREATE TABLE data_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(200),
    source_type VARCHAR(50),  -- api, rss, crawler
    base_url VARCHAR(500),
    config JSONB,  -- API密钥、采集参数等
    
    -- 采集状态
    is_active BOOLEAN DEFAULT TRUE,
    last_crawl_time TIMESTAMP WITH TIME ZONE,
    crawl_interval_minutes INTEGER DEFAULT 60,
    
    -- 统计信息
    total_articles INTEGER DEFAULT 0,
    success_rate DECIMAL(3,2) DEFAULT 1.0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 用户上传文件表
CREATE TABLE user_uploads (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    file_name VARCHAR(255),
    file_path VARCHAR(500),
    file_type VARCHAR(50),  -- url, text, pdf
    file_size BIGINT,
    
    -- 处理状态
    status VARCHAR(20) DEFAULT 'pending',  -- pending, processing, completed, failed
    processed_article_id BIGINT REFERENCES articles(id),
    error_message TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- 创建索引
CREATE INDEX idx_articles_source ON articles(source_name);
CREATE INDEX idx_articles_publish_time ON articles(publish_time DESC);
CREATE INDEX idx_articles_crawl_time ON articles(crawl_time DESC);
CREATE INDEX idx_articles_search_vector ON articles USING GIN(search_vector);
CREATE INDEX idx_commodity_tags_article ON commodity_tags(article_id);
CREATE INDEX idx_commodity_tags_type ON commodity_tags(commodity_type, sub_type);
CREATE INDEX idx_analysis_dimensions_article ON analysis_dimensions(article_id);

-- 全文搜索索引触发器
CREATE OR REPLACE FUNCTION update_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := 
        setweight(to_tsvector('chinese', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('chinese', COALESCE((SELECT summary FROM article_contents WHERE article_id = NEW.id), '')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER articles_search_vector_update
    BEFORE INSERT OR UPDATE ON articles
    FOR EACH ROW
    EXECUTE FUNCTION update_search_vector();
```

#### 4.2.2 MongoDB - 文档内容模型

```javascript
// 文章集合
{
    "_id": ObjectId("..."),
    "article_uuid": "uuid-from-postgres",
    
    // 原始内容
    "raw_content": "...",
    
    // 清洗后内容
    "cleaned_content": "...",
    
    // 结构化内容(段落、表格等)
    "structured_content": {
        "paragraphs": [
            {"index": 1, "text": "...", "type": "normal"},
            {"index": 2, "text": "...", "type": "quote"}
        ],
        "tables": [
            {
                "index": 1,
                "headers": ["..."],
                "rows": [["..."]]
            }
        ],
        "images": [
            {"url": "...", "caption": "...", "ocr_text": "..."}
        ]
    },
    
    // NER结果
    "entities": {
        "organizations": ["OPEC", "IEA", "EIA"],
        "locations": ["中东", "美国", "北海"],
        "commodities": ["原油", "天然气"],
        "persons": ["..."],
        "dates": ["2024年1月"]
    },
    
    // 分析结果
    "analysis": {
        "keywords": [
            {"word": "原油", "weight": 0.9},
            {"word": "供需", "weight": 0.8}
        ],
        "topics": ["supply_demand", "price_trend"],
        "sentiment": {
            "overall": 0.3,
            "by_dimension": {
                "fundamental": 0.2,
                "sentiment": 0.5
            }
        }
    },
    
    "created_at": ISODate("..."),
    "updated_at": ISODate("...")
}

// 价格数据集合
{
    "_id": ObjectId("..."),
    "commodity": "原油",
    "sub_type": "WTI",
    "price": 78.5,
    "currency": "USD",
    "unit": "barrel",
    "timestamp": ISODate("..."),
    "source": "CME",
    "metadata": {
        "contract_month": "2024-03",
        "settlement_type": "daily"
    }
}
```

#### 4.2.3 Elasticsearch - 搜索索引模型

```json
{
    "mappings": {
        "properties": {
            "article_uuid": {"type": "keyword"},
            "title": {
                "type": "text",
                "analyzer": "ik_max_word",
                "search_analyzer": "ik_smart"
            },
            "content": {
                "type": "text",
                "analyzer": "ik_max_word"
            },
            "summary": {
                "type": "text",
                "analyzer": "ik_max_word"
            },
            "source_name": {"type": "keyword"},
            "publish_time": {"type": "date"},
            "commodity_tags": {
                "type": "nested",
                "properties": {
                    "commodity": {"type": "keyword"},
                    "sub_type": {"type": "keyword"}
                }
            },
            "analysis_dimensions": {
                "type": "nested",
                "properties": {
                    "dimension_type": {"type": "keyword"},
                    "sentiment_score": {"type": "float"}
                }
            },
            "keywords": {
                "type": "object",
                "properties": {
                    "word": {"type": "keyword"},
                    "weight": {"type": "float"}
                }
            },
            "entities": {
                "properties": {
                    "organizations": {"type": "keyword"},
                    "locations": {"type": "keyword"},
                    "persons": {"type": "keyword"}
                }
            },
            "quality_score": {"type": "float"},
            "is_user_input": {"type": "boolean"}
        }
    },
    "settings": {
        "number_of_shards": 3,
        "number_of_replicas": 1,
        "analysis": {
            "analyzer": {
                "ik_custom": {
                    "type": "custom",
                    "tokenizer": "ik_max_word",
                    "filter": ["lowercase", "synonym_filter"]
                }
            },
            "filter": {
                "synonym_filter": {
                    "type": "synonym",
                    "synonyms": [
                        "原油,石油,oil,crude",
                        "天然气,natural gas,gas",
                        "液化气,LPG,液化石油气"
                    ]
                }
            }
        }
    }
}
```

### 4.3 缓存策略

```python
class CacheManager:
    """缓存管理器"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        
        # 缓存键前缀
        self.KEY_PREFIX = {
            'article': 'article:',
            'article_list': 'articles:list:',
            'search_result': 'search:',
            'commodity_stats': 'stats:commodity:',
            'user_session': 'session:user:',
        }
        
        # 缓存过期时间(秒)
        self.TTL = {
            'article': 3600,  # 1小时
            'article_list': 300,  # 5分钟
            'search_result': 180,  # 3分钟
            'commodity_stats': 600,  # 10分钟
            'user_session': 86400,  # 1天
        }
        
    async def get_article(self, article_uuid):
        """获取文章缓存"""
        key = f"{self.KEY_PREFIX['article']}{article_uuid}"
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None
        
    async def set_article(self, article_uuid, data):
        """设置文章缓存"""
        key = f"{self.KEY_PREFIX['article']}{article_uuid}"
        await self.redis.setex(
            key,
            self.TTL['article'],
            json.dumps(data, default=str)
        )
        
    async def invalidate_article(self, article_uuid):
        """使文章缓存失效"""
        key = f"{self.KEY_PREFIX['article']}{article_uuid}"
        await self.redis.delete(key)
        
    async def get_search_results(self, query_hash):
        """获取搜索结果缓存"""
        key = f"{self.KEY_PREFIX['search_result']}{query_hash}"
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None
        
    async def cache_search_results(self, query_hash, results, ttl=None):
        """缓存搜索结果"""
        key = f"{self.KEY_PREFIX['search_result']}{query_hash}"
        ttl = ttl or self.TTL['search_result']
        await self.redis.setex(
            key,
            ttl,
            json.dumps(results, default=str)
        )
        
    async def get_commodity_stats(self, commodity, sub_type=None):
        """获取品种统计缓存"""
        key = f"{self.KEY_PREFIX['commodity_stats']}{commodity}"
        if sub_type:
            key += f":{sub_type}"
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None
```

---

## 5. 数据更新和版本管理

### 5.1 数据更新机制

#### 5.1.1 增量更新流程

```
┌─────────────────────────────────────────────────────────────────┐
│                     增量更新调度器                                │
│                    (Celery Beat Schedule)                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. 检查数据源状态                                                │
│     - 获取上次更新时间                                            │
│     - 判断是否达到更新间隔                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. 执行增量采集                                                  │
│     - 使用API的since参数                                          │
│     - 或使用爬虫的增量模式                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. 数据去重与合并                                                │
│     - URL去重检查                                                 │
│     - 内容相似度检查                                              │
│     - 更新已有文章                                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. 索引更新                                                      │
│     - 更新PostgreSQL                                              │
│     - 更新MongoDB                                                 │
│     - 更新Elasticsearch                                           │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.1.2 更新调度配置

```python
# Celery Beat 调度配置
beat_schedule = {
    # 实时新闻源 - 每5分钟
    'fetch-realtime-news': {
        'task': 'tasks.fetch_news',
        'schedule': crontab(minute='*/5'),
        'args': ('realtime_sources',),
    },
    
    # 财经新闻 - 每15分钟
    'fetch-finance-news': {
        'task': 'tasks.fetch_news',
        'schedule': crontab(minute='*/15'),
        'args': ('finance_sources',),
    },
    
    # 行业分析 - 每小时
    'fetch-industry-analysis': {
        'task': 'tasks.fetch_news',
        'schedule': crontab(minute=0),  # 每小时整点
        'args': ('industry_sources',),
    },
    
    # 官方数据 - 每日
    'fetch-official-data': {
        'task': 'tasks.fetch_official_data',
        'schedule': crontab(hour=9, minute=0),  # 每天9点
    },
    
    # 数据清理任务 - 每日凌晨
    'cleanup-old-data': {
        'task': 'tasks.cleanup_old_data',
        'schedule': crontab(hour=2, minute=0),
        'args': (30,),  # 保留30天
    },
    
    # 统计更新 - 每小时
    'update-statistics': {
        'task': 'tasks.update_statistics',
        'schedule': crontab(minute=30),
    },
}
```

### 5.2 版本管理

#### 5.2.1 文章版本控制

```python
class ArticleVersionManager:
    """文章版本管理器"""
    
    def __init__(self, db_session):
        self.db = db_session
        
    def create_version(self, article_id, change_reason=None):
        """创建文章版本快照"""
        article = self.db.query(Article).get(article_id)
        
        version = ArticleVersion(
            article_id=article_id,
            version_number=self._get_next_version(article_id),
            title=article.title,
            content=article.content,
            metadata=article.metadata,
            change_reason=change_reason,
            created_by=article.updated_by,
            created_at=datetime.utcnow()
        )
        
        self.db.add(version)
        self.db.commit()
        
        return version
        
    def get_version(self, article_id, version_number):
        """获取特定版本"""
        return self.db.query(ArticleVersion).filter_by(
            article_id=article_id,
            version_number=version_number
        ).first()
        
    def compare_versions(self, article_id, version_a, version_b):
        """比较两个版本差异"""
        v_a = self.get_version(article_id, version_a)
        v_b = self.get_version(article_id, version_b)
        
        diff = {
            'title_changed': v_a.title != v_b.title,
            'content_diff': self._compute_diff(v_a.content, v_b.content),
            'metadata_changes': self._compare_metadata(v_a.metadata, v_b.metadata),
        }
        
        return diff
        
    def rollback_to_version(self, article_id, version_number):
        """回滚到指定版本"""
        version = self.get_version(article_id, version_number)
        if not version:
            raise ValueError(f"Version {version_number} not found")
            
        article = self.db.query(Article).get(article_id)
        
        # 创建当前版本快照
        self.create_version(article_id, change_reason=f"Rollback to version {version_number}")
        
        # 回滚数据
        article.title = version.title
        article.content = version.content
        article.metadata = version.metadata
        article.update_time = datetime.utcnow()
        
        self.db.commit()
        
        return article
```

#### 5.2.2 数据库版本迁移

```python
# Alembic迁移脚本示例
"""
数据库迁移管理

初始化:
    alembic init alembic

创建迁移:
    alembic revision --autogenerate -m "create articles table"

执行迁移:
    alembic upgrade head

回滚:
    alembic downgrade -1
"""

# 示例迁移脚本
revision = '001_create_articles_table'
down_revision = None

def upgrade():
    # 创建文章表
    op.create_table(
        'articles',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('uuid', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('source_name', sa.String(length=100), nullable=False),
        sa.Column('source_url', sa.String(length=500), nullable=True),
        sa.Column('original_url', sa.String(length=500), nullable=True),
        sa.Column('content_hash', sa.String(length=64), nullable=True),
        sa.Column('publish_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('crawl_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('update_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('content_type', sa.String(length=20), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=True),
        sa.Column('word_count', sa.Integer(), nullable=True),
        sa.Column('quality_score', sa.Numeric(3, 2), nullable=True),
        sa.Column('is_valid', sa.Boolean(), nullable=True),
        sa.Column('is_user_input', sa.Boolean(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('content_hash'),
        sa.UniqueConstraint('original_url'),
        sa.UniqueConstraint('uuid')
    )
    
    # 创建索引
    op.create_index('idx_articles_source', 'articles', ['source_name'])
    op.create_index('idx_articles_publish_time', 'articles', ['publish_time'])
    op.create_index('idx_articles_crawl_time', 'articles', ['crawl_time'])

def downgrade():
    op.drop_index('idx_articles_crawl_time', table_name='articles')
    op.drop_index('idx_articles_publish_time', table_name='articles')
    op.drop_index('idx_articles_source', table_name='articles')
    op.drop_table('articles')
```

### 5.3 数据归档策略

```python
class DataArchiver:
    """数据归档管理器"""
    
    def __init__(self, db_session, storage_client):
        self.db = db_session
        self.storage = storage_client
        
    def archive_old_articles(self, days=90):
        """归档旧文章"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # 获取需要归档的文章
        old_articles = self.db.query(Article).filter(
            Article.publish_time < cutoff_date,
            Article.is_archived == False
        ).all()
        
        for article in old_articles:
            self._archive_article(article)
            
        logger.info(f"Archived {len(old_articles)} articles")
        
    def _archive_article(self, article):
        """归档单篇文章"""
        # 1. 导出到归档存储
        archive_data = {
            'article': article.to_dict(),
            'content': article.content.to_dict() if article.content else None,
            'tags': [t.to_dict() for t in article.commodity_tags],
            'analysis': [a.to_dict() for a in article.analysis_dimensions],
        }
        
        # 2. 存储到对象存储
        archive_path = f"archives/{article.publish_time.year}/{article.publish_time.month}/{article.uuid}.json.gz"
        self.storage.upload_json_gz(archive_path, archive_data)
        
        # 3. 标记为已归档
        article.is_archived = True
        article.archive_path = archive_path
        
        # 4. 清理活跃存储中的大字段
        if article.content:
            article.content.content = None  # 保留元数据，删除正文
            
        self.db.commit()
        
    def restore_article(self, article_uuid):
        """从归档恢复文章"""
        article = self.db.query(Article).filter_by(uuid=article_uuid).first()
        if not article or not article.is_archived:
            raise ValueError("Article not found or not archived")
            
        # 从对象存储恢复
        archive_data = self.storage.download_json_gz(article.archive_path)
        
        # 恢复内容
        if archive_data.get('content'):
            article.content.content = archive_data['content']['content']
            
        article.is_archived = False
        article.archive_path = None
        
        self.db.commit()
        
        return article
```

---

## 6. 系统监控与运维

### 6.1 监控指标

| 指标类别 | 具体指标 | 告警阈值 |
|---------|---------|---------|
| 采集监控 | 采集成功率 | < 95% |
| 采集监控 | 采集延迟 | > 30分钟 |
| 数据质量 | 清洗成功率 | < 98% |
| 数据质量 | 平均质量评分 | < 0.7 |
| 系统性能 | API响应时间 | > 500ms |
| 系统性能 | 数据库连接数 | > 80% |
| 存储监控 | 磁盘使用率 | > 80% |
| 存储监控 | 内存使用率 | > 85% |

### 6.2 日志管理

```python
# 日志配置
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'json': {
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'INFO'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'formatter': 'json',
            'level': 'INFO'
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/error.log',
            'maxBytes': 10485760,
            'backupCount': 10,
            'formatter': 'json',
            'level': 'ERROR'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': True
        },
        'crawler': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False
        },
        'data_processor': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False
        }
    }
}
```

---

## 附录

### A. 技术栈清单

| 组件 | 技术选型 | 版本 |
|------|---------|------|
| 爬虫框架 | Scrapy + Playwright | 2.11+ |
| 任务队列 | Celery + Redis | 5.3+ |
| 数据库 | PostgreSQL | 15+ |
| 文档存储 | MongoDB | 6.0+ |
| 搜索引擎 | Elasticsearch | 8.0+ |
| 缓存 | Redis | 7.0+ |
| ORM | SQLAlchemy | 2.0+ |
| PDF处理 | pdfplumber + PaddleOCR | - |
| NLP处理 | Jieba + Transformers | - |

### B. 数据源API参考

```yaml
# 示例：Platts API配置
platts_api:
  base_url: "https://api.platts.com"
  endpoints:
    news: "/v1/news"
    prices: "/v1/assessments"
  auth_type: "api_key"
  rate_limit: 1000  # 每小时
  
# 示例：EIA API配置
eia_api:
  base_url: "https://api.eia.gov/v2"
  endpoints:
    petroleum: "/petroleum/pnp/sum/data"
    natural_gas: "/natural-gas/sum/data"
  auth_type: "api_key"
  rate_limit: 100  # 每小时
```

---

*文档版本: 1.0*
*最后更新: 2024年*
