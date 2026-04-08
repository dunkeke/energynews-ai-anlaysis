# 能源化工新闻分析系统

综合各专业和主流媒体进行能化品种新闻分析的智能软件系统。


## 当前迭代进度（2026-04-07）

- ✅ HTML版本已支持四种输入：URL、文本、PDF、自有渠道快讯
- ✅ 覆盖品种扩展到 WTI / Brent / HH / TTF / JKM / PG / PP / MB / FEI / CP
- ✅ 分析页已按五维因子（基本面/宏观/情绪/技术/地缘）生成量化综合分与置信度
- 🔜 下一阶段建议：将评分逻辑迁移到 Python 服务，接入数据库与任务队列

## 功能特性

- **多渠道数据采集**：自动采集30+专业/主流媒体 + 支持用户手工导入URL/文本/PDF
- **五维深度分析**：基本面、宏观面、情绪面、技术面、地缘风险全面覆盖
- **AI驱动NLP**：基于BERT的领域微调模型，实现实体识别、情感分析、事件提取
- **量化评分体系**：多因子模型生成-5到+5的量化评分和交易信号
- **动态可视化**：实时仪表盘、雷达图、热力图、趋势图等多维度展示
- **智能预警系统**：四级预警机制，及时捕捉市场异常
- **品种差异化**：针对不同能源品种定制分析权重和关键指标

## 关注品种

### 原油
- WTI（西德克萨斯中质原油）
- Brent（布伦特原油）

### 天然气
- JKM（日韩基准）
- HH（亨利港）
- TTF（荷兰天然气）

### 液化气
- PG（丙烷）
- PP（丙烯）
- MB（Mont Belvieu）
- FEI（远东指数）
- CP（沙特合同价）

### 成品油
- 汽油
- 柴油
- 航煤
- 燃料油

## 技术架构

### 后端技术栈
- **框架**：FastAPI (Python)
- **数据库**：PostgreSQL + MongoDB + Redis
- **搜索引擎**：Elasticsearch
- **消息队列**：Apache Kafka
- **AI/ML**：Hugging Face Transformers + FinBERT

### 前端技术栈
- **框架**：React 18 + TypeScript
- **UI组件**：Ant Design
- **图表库**：ECharts
- **状态管理**：React Hooks

### 基础设施
- **容器化**：Docker + Docker Compose
- **Web服务器**：Nginx
- **监控**：Prometheus + Grafana

## 快速开始

### 环境要求
- Docker 20.10+
- Docker Compose 2.0+
- 8GB+ RAM
- 50GB+ 磁盘空间

### 安装部署

1. 克隆代码仓库
```bash
git clone <repository-url>
cd energy-news-analytics
```

2. 启动服务
```bash
docker-compose up -d
```

3. 等待服务启动完成（约2-3分钟）

4. 访问系统
- 前端界面：http://localhost
- API文档：http://localhost:8000/docs
- 管理后台：http://localhost:8000/admin

### 开发环境

#### 后端开发
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### 轻量后端（建议先本地联调）
```bash
cd backend_simple
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

轻量后端新增接口：
- `GET /api/v1/news/auto-collect?commodity=WTI&limit=20`（自动采集可爬取 RSS 新闻）
- `GET /api/v1/quant/yfinance/{symbol}/volatility?period=1y&interval=1d&window=20`（历史数据+波动率量化）
- `GET /api/v1/ai/dynamic-weights?commodity=WTI&period=6mo&window=20&use_live_news=true`（AI动态权重：结合情绪与波动率）
- `POST /api/v1/ai/notebooklm/market-brief`（NotebookLM 市场简报：支持 notebooklm-py，未配置时自动回退 mock 输出）

NotebookLM 集成说明（轻量后端）：
```bash
cd backend_simple
pip install -r requirements.txt
uvicorn main:app --reload
```

示例请求：
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/ai/notebooklm/market-brief" \
  -H "Content-Type: application/json" \
  -d '{
    "commodity":"WTI",
    "use_live_news":true,
    "max_items":20,
    "style":"trader",
    "extra_context":"关注今晚库存数据与地缘扰动"
  }'
```


#### 前端开发
```bash
cd frontend
npm install
npm start
```

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        展示层 (Presentation)                     │
│              Web前端(React) | 移动端(Flutter) | 管理后台          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API网关层 (Nginx)                         │
│                     路由分发 | 认证授权 | 限流熔断                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      业务服务层 (FastAPI)                         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │ 基本面  │ │ 宏观面  │ │ 情绪面  │ │ 技术面  │ │ 地缘风险 │   │
│  │ 分析服务│ │ 分析服务│ │ 分析服务│ │ 分析服务│ │ 分析服务│   │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      数据存储层 (Data Storage)                    │
│  PostgreSQL | MongoDB | Redis | ClickHouse | Elasticsearch       │
└─────────────────────────────────────────────────────────────────┘
```

## API接口

### 新闻导入
```http
POST /api/v1/news/import
Content-Type: multipart/form-data

import_type: url | text | pdf
content: <url或文本内容>
file: <PDF文件>
commodities: ["WTI", "Brent"]
```

### 获取分析结果
```http
GET /api/v1/analysis/{commodity}?days=7
```

### 获取量化评分
```http
GET /api/v1/quant/{commodity}/score
```

### 获取仪表盘数据
```http
GET /api/v1/visualization/dashboard
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DATABASE_URL | PostgreSQL连接字符串 | postgresql://user:password@localhost/energy_news |
| MONGODB_URL | MongoDB连接字符串 | mongodb://localhost:27017/energy_news |
| REDIS_URL | Redis连接字符串 | redis://localhost:6379 |
| ELASTICSEARCH_URL | ES连接字符串 | http://localhost:9200 |
| DEBUG | 调试模式 | false |

### 评分权重配置

各品种默认权重配置位于 `backend/models/database.py` 中的 `init_commodity_configs` 函数。

## 数据流

1. **数据采集**：从多个数据源采集新闻和数据
2. **数据清洗**：清洗、去重、标准化处理
3. **NLP分析**：实体识别、情感分析、事件提取
4. **量化评分**：多维度评分计算
5. **可视化展示**：仪表盘、图表、报告生成
6. **预警通知**：异常检测和预警推送

## 贡献指南

1. Fork 代码仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目主页：https://github.com/yourusername/energy-news-analytics
- 问题反馈：https://github.com/yourusername/energy-news-analytics/issues
- 邮箱：support@energy-news-analytics.com

## 致谢

- 感谢所有开源项目的贡献
- 感谢能源化工行业的专家支持
- 感谢用户的反馈和建议
