# 能源化工新闻分析软件 - 完整方案文档

> GitHub Pages 入口已改为 `index.html` 并默认跳转到可交互 HTML App：`energy-news-analytics/html_version/index.html`。

## 文档清单

本目录包含能源化工新闻分析软件的完整技术方案文档，由多个专家组协作完成。

---

## 1. 量化分析与可视化方案 (本组输出)

### 主要文档

| 文件名 | 说明 | 大小 |
|--------|------|------|
| `energy_chemical_quant_visualization_scheme.md` | **量化分析与可视化方案主文档** | 64KB |
| `scoring_model_implementation.py` | 评分模型Python实现代码 | 29KB |
| `visualization_config.js` | 前端可视化配置文件 | 15KB |
| `report_templates.py` | 报告模板生成器 | 24KB |

### 文档内容概要

#### `energy_chemical_quant_visualization_scheme.md`
包含以下核心内容：

1. **量化分析模型设计**
   - 多维度评分体系架构（基本面/宏观面/情绪面/技术面/地缘风险）
   - 各维度评分模型详解
   - 综合评分算法
   - 趋势预测模型
   - 风险预警指标体系

2. **评分权重体系**
   - 基础权重配置
   - 品种差异化权重（原油/天然气/液化气/成品油）
   - 动态权重调整机制

3. **可视化展示方案**
   - 仪表盘整体布局设计
   - 图表类型详细设计（雷达图/趋势图/热力图/仪表盘）
   - 品种对比展示
   - 时间维度展示

4. **报告输出格式**
   - 实时分析报告模板
   - 日报/周报模板
   - 预警通知格式

5. **推荐技术栈**
   - 前端可视化技术栈
   - 后端技术栈
   - 数据流架构
   - 部署架构
   - 性能指标要求

#### `scoring_model_implementation.py`
完整的Python实现代码，包含：
- `FundamentalScorer` - 基本面评分器
- `MacroScorer` - 宏观面评分器
- `SentimentScorer` - 情绪面评分器
- `TechnicalScorer` - 技术面评分器
- `GeopoliticalRiskScorer` - 地缘风险评分器
- `CompositeScoringModel` - 综合评分模型
- `DynamicWeightAdjuster` - 动态权重调整器
- `RiskAlertSystem` - 风险预警系统
- `TrendPredictionModel` - 趋势预测模型

#### `visualization_config.js`
前端可视化配置文件，包含：
- ECharts主题配置
- 评分颜色映射
- 雷达图/趋势图/热力图/仪表盘配置
- 预警等级配置
- 品种配置
- 图表选项生成器函数

#### `report_templates.py`
报告模板生成器，包含：
- `RealtimeReportGenerator` - 实时分析报告
- `DailyReportGenerator` - 日报生成器
- `WeeklyReportGenerator` - 周报生成器
- `AlertNotificationGenerator` - 预警通知生成器
- 支持JSON/Markdown/HTML多种格式输出

---

## 2. 其他相关文档

| 文件名 | 说明 | 来源 |
|--------|------|------|
| `energy_chemical_nlp_scheme.md` | NLP情感分析方案 | NLP专家组 |
| `energy_news_analytics_architecture.md` | 系统架构设计 | 架构专家组 |
| `energy_news_data_engineering_scheme.md` | 数据工程方案 | 数据工程专家组 |
| `architecture_diagrams.md` | 架构图详细说明 | 架构专家组 |
| `technology_comparison.md` | 技术选型对比 | 架构专家组 |
| `能源化工市场分析框架_v1.0.md` | 市场分析框架 | 业务专家组 |

---

## 快速开始

### 运行评分模型演示

```bash
cd /mnt/okcomputer/output
python scoring_model_implementation.py
```

### 运行报告模板演示

```bash
python report_templates.py
```

---

## 核心概念

### 评分体系

```
综合评分 = 基本面×权重 + 宏观面×权重 + 情绪面×权重 + 技术面×权重 + 地缘风险调整
```

### 评级区间

| 评分区间 | 评级 | 颜色 |
|----------|------|------|
| 80-100 | 强烈看涨 | #00C853 |
| 65-80 | 看涨 | #69F0AE |
| 55-65 | 偏看涨 | #B2FF59 |
| 45-55 | 中性 | #FFD54F |
| 35-45 | 偏看跌 | #FF8A65 |
| 20-35 | 看跌 | #FF5252 |
| 0-20 | 强烈看跌 | #D32F2F |

### 预警等级

| 等级 | 触发条件 | 响应时间 |
|------|----------|----------|
| 红色 | 综合评分突变±20分或地缘风险>10 | 即时 |
| 橙色 | 单维度评分突变±15分或综合评分±15分 | 15分钟内 |
| 黄色 | 连续3个周期评分同向变化>10分 | 1小时内 |
| 蓝色 | 评分趋势与价格背离 | 日报中提示 |

---

## 技术栈

### 前端
- **图表库**: Apache ECharts
- **UI框架**: React + Ant Design
- **状态管理**: Redux / Zustand
- **实时通信**: WebSocket

### 后端
- **API框架**: FastAPI (Python)
- **计算引擎**: Python + NumPy/Pandas
- **NLP处理**: spaCy / Transformers
- **数据库**: PostgreSQL + TimescaleDB
- **缓存**: Redis
- **消息队列**: RabbitMQ / Kafka

---

## 作者

量化分析与数据可视化专家组

---

*文档版本: v1.0*  
*最后更新: 2024年1月*
