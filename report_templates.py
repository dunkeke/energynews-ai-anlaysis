"""
能源化工新闻分析软件 - 报告模板
================================================
本模块包含各类报告的生成模板
"""

from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
import json


@dataclass
class ReportConfig:
    """报告配置"""
    report_type: str
    title: str
    timestamp: datetime
    author: str = "系统自动生成"


class RealtimeReportGenerator:
    """实时分析报告生成器"""
    
    @staticmethod
    def generate(analysis_result: Dict) -> Dict:
        """生成实时分析报告"""
        return {
            "report_type": "realtime_analysis",
            "timestamp": datetime.now().isoformat(),
            "product": analysis_result.get('product', 'Unknown'),
            "analysis": {
                "composite_score": analysis_result.get('composite_score', 50),
                "rating": analysis_result.get('rating', '中性'),
                "rating_color": analysis_result.get('rating_color', '#FFD54F'),
                "change_1h": analysis_result.get('change_1h', 0),
                "change_24h": analysis_result.get('change_24h', 0),
                "dimensions": analysis_result.get('dimension_breakdown', {}),
                "geo_risk": {
                    "score": analysis_result.get('geo_adjustment', 0),
                    "events": analysis_result.get('geo_risk_events', [])
                }
            },
            "key_drivers": analysis_result.get('key_drivers', []),
            "prediction": analysis_result.get('prediction', {}),
            "alerts": analysis_result.get('alerts', [])
        }
    
    @staticmethod
    def to_html(report: Dict) -> str:
        """转换为HTML格式"""
        score = report['analysis']['composite_score']
        rating = report['analysis']['rating']
        color = report['analysis']['rating_color']
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                .report-card {{
                    font-family: 'Microsoft YaHei', Arial, sans-serif;
                    max-width: 400px;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                }}
                .header {{
                    background: linear-gradient(135deg, {color}, {color}dd);
                    color: white;
                    padding: 20px;
                    text-align: center;
                }}
                .score {{
                    font-size: 48px;
                    font-weight: bold;
                    margin: 10px 0;
                }}
                .rating {{
                    font-size: 18px;
                    opacity: 0.9;
                }}
                .body {{
                    background: white;
                    padding: 20px;
                }}
                .section {{
                    margin-bottom: 15px;
                }}
                .section-title {{
                    font-size: 14px;
                    color: #666;
                    margin-bottom: 8px;
                }}
                .dimension-grid {{
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 10px;
                }}
                .dimension-item {{
                    background: #f5f5f5;
                    padding: 10px;
                    border-radius: 6px;
                }}
                .dimension-name {{
                    font-size: 12px;
                    color: #666;
                }}
                .dimension-score {{
                    font-size: 18px;
                    font-weight: bold;
                    color: #333;
                }}
                .drivers {{
                    list-style: none;
                    padding: 0;
                }}
                .drivers li {{
                    padding: 8px 0;
                    border-bottom: 1px solid #eee;
                    font-size: 13px;
                }}
                .drivers li:before {{
                    content: "▸ ";
                    color: {color};
                }}
                .prediction {{
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 8px;
                }}
                .prediction-item {{
                    display: flex;
                    justify-content: space-between;
                    margin: 5px 0;
                }}
                .footer {{
                    background: #f5f5f5;
                    padding: 10px 20px;
                    font-size: 11px;
                    color: #999;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="report-card">
                <div class="header">
                    <div style="font-size: 14px; opacity: 0.8;">{report['product']} 实时分析</div>
                    <div class="score">{score}</div>
                    <div class="rating">{rating}</div>
                </div>
                <div class="body">
                    <div class="section">
                        <div class="section-title">各维度评分</div>
                        <div class="dimension-grid">
        """
        
        for dim, score in report['analysis']['dimensions'].items():
            html += f"""
                            <div class="dimension-item">
                                <div class="dimension-name">{dim}</div>
                                <div class="dimension-score">{score:.1f}</div>
                            </div>
            """
        
        html += """
                        </div>
                    </div>
                    <div class="section">
                        <div class="section-title">主要驱动因素</div>
                        <ul class="drivers">
        """
        
        for driver in report.get('key_drivers', []):
            html += f"<li>{driver}</li>"
        
        html += """
                        </ul>
                    </div>
        """
        
        if report.get('prediction'):
            html += """
                    <div class="section">
                        <div class="section-title">趋势预测</div>
                        <div class="prediction">
            """
            for horizon, pred in report['prediction'].items():
                direction_icon = "📈" if pred['direction'] == 'up' else "📉" if pred['direction'] == 'down' else "➡️"
                html += f"""
                            <div class="prediction-item">
                                <span>{horizon}</span>
                                <span>{direction_icon} {pred['probability']*100:.0f}%</span>
                            </div>
                """
            html += """
                        </div>
                    </div>
            """
        
        html += f"""
                </div>
                <div class="footer">
                    生成时间: {report['timestamp']}
                </div>
            </div>
        </body>
        </html>
        """
        
        return html


class DailyReportGenerator:
    """日报生成器"""
    
    @staticmethod
    def generate(product_scores: List[Dict], alerts: List[Dict], date: str = None) -> Dict:
        """生成日报"""
        if date is None:
            date = datetime.now().strftime('%Y年%m月%d日')
        
        # 按评分排序
        sorted_products = sorted(product_scores, key=lambda x: x['composite_score'], reverse=True)
        
        # 统计情绪分布
        bullish_count = sum(1 for p in product_scores if p['rating'] in ['强烈看涨', '看涨', '偏看涨'])
        bearish_count = sum(1 for p in product_scores if p['rating'] in ['强烈看跌', '看跌', '偏看跌'])
        neutral_count = len(product_scores) - bullish_count - bearish_count
        
        return {
            "report_type": "daily",
            "date": date,
            "generated_at": datetime.now().isoformat(),
            "market_overview": {
                "total_products": len(product_scores),
                "sentiment_distribution": {
                    "bullish": bullish_count,
                    "neutral": neutral_count,
                    "bearish": bearish_count
                }
            },
            "ranking": [
                {
                    "rank": i + 1,
                    "product": p['product'],
                    "score": p['composite_score'],
                    "rating": p['rating'],
                    "change_24h": p.get('change_24h', 0),
                    "key_driver": p.get('key_driver', '')
                }
                for i, p in enumerate(sorted_products)
            ],
            "alerts": alerts,
            "top_movers": sorted_products[:3],
            "bottom_movers": sorted_products[-3:]
        }
    
    @staticmethod
    def to_markdown(report: Dict) -> str:
        """转换为Markdown格式"""
        md = f"""# 能源化工市场日报
**报告日期**: {report['date']}  
**报告时间**: {datetime.now().strftime('%H:%M')} (北京时间)

---

## 一、市场概览

### 1.1 综合评分排名
| 排名 | 品种 | 综合评分 | 评级 | 日涨跌 | 主要驱动 |
|------|------|----------|------|--------|----------|
"""
        
        for item in report['ranking']:
            change_str = f"{item['change_24h']:+.1f}%" if item['change_24h'] != 0 else "-"
            md += f"| {item['rank']} | {item['product']} | {item['score']:.1f} | {item['rating']} | {change_str} | {item['key_driver']} |\n"
        
        md += f"""
### 1.2 市场情绪分布
- 看涨: {report['market_overview']['sentiment_distribution']['bullish']}个品种 ({report['market_overview']['sentiment_distribution']['bullish']/report['market_overview']['total_products']*100:.0f}%)
- 中性: {report['market_overview']['sentiment_distribution']['neutral']}个品种 ({report['market_overview']['sentiment_distribution']['neutral']/report['market_overview']['total_products']*100:.0f}%)
- 看跌: {report['market_overview']['sentiment_distribution']['bearish']}个品种 ({report['market_overview']['sentiment_distribution']['bearish']/report['market_overview']['total_products']*100:.0f}%)

---

## 二、风险预警

### 2.1 当日预警汇总
"""
        
        if report['alerts']:
            md += "| 时间 | 品种 | 等级 | 类型 | 描述 |\n"
            md += "|------|------|------|------|------|\n"
            for alert in report['alerts']:
                level_icon = {"red": "🔴", "orange": "🟠", "yellow": "🟡", "blue": "🔵"}.get(alert['level'], "⚪")
                md += f"| {alert.get('time', '--')} | {alert.get('product', '--')} | {level_icon} {alert['level']} | {alert['type']} | {alert['message']} |\n"
        else:
            md += "当日暂无预警\n"
        
        md += f"""
---

*报告生成时间: {report['generated_at']}*  
*数据来源: 综合各专业机构*  
*免责声明: 本报告仅供参考，不构成投资建议*
"""
        
        return md


class WeeklyReportGenerator:
    """周报生成器"""
    
    @staticmethod
    def generate(weekly_data: Dict) -> Dict:
        """生成周报"""
        return {
            "report_type": "weekly",
            "period": weekly_data['period'],
            "generated_at": datetime.now().isoformat(),
            "price_performance": weekly_data.get('price_performance', []),
            "score_changes": weekly_data.get('score_changes', []),
            "dimension_summary": weekly_data.get('dimension_summary', {}),
            "predictions": weekly_data.get('predictions', []),
            "key_events": weekly_data.get('key_events', [])
        }
    
    @staticmethod
    def to_markdown(report: Dict) -> str:
        """转换为Markdown格式"""
        md = f"""# 能源化工市场周报
**报告周期**: {report['period']}  
**报告日期**: {datetime.now().strftime('%Y年%m月%d日')}

---

## 一、本周市场回顾

### 1.1 价格表现
| 品种 | 周初 | 周末 | 涨跌 | 涨跌幅 | 波动率 |
|------|------|------|------|--------|--------|
"""
        
        for perf in report.get('price_performance', []):
            md += f"| {perf['product']} | {perf['open']:.2f} | {perf['close']:.2f} | {perf['change']:+.2f} | {perf['change_pct']:+.2f}% | {perf['volatility']:.1f}% |\n"
        
        md += """
### 1.2 评分变化
| 品种 | 周初评分 | 周末评分 | 变化 | 评级变化 |
|------|----------|----------|------|----------|
"""
        
        for change in report.get('score_changes', []):
            rating_change = change.get('rating_change', '-')
            md += f"| {change['product']} | {change['start_score']:.1f} | {change['end_score']:.1f} | {change['change']:+.1f} | {rating_change} |\n"
        
        md += """
---

## 二、维度分析

### 2.1 基本面周度总结
"""
        
        summary = report.get('dimension_summary', {})
        md += summary.get('fundamental', '本周基本面整体平稳。\n')
        
        md += """
### 2.2 宏观面周度总结
"""
        md += summary.get('macro', '本周宏观面影响中性。\n')
        
        md += """
### 2.3 情绪面周度总结
"""
        md += summary.get('sentiment', '本周市场情绪整体稳定。\n')
        
        md += """
---

## 三、下周展望

### 3.1 趋势预测
| 品种 | 方向 | 概率 | 目标区间 | 关键价位 |
|------|------|------|----------|----------|
"""
        
        for pred in report.get('predictions', []):
            direction_icon = "📈" if pred['direction'] == 'up' else "📉" if pred['direction'] == 'down' else "➡️"
            md += f"| {pred['product']} | {direction_icon} {pred['direction_label']} | {pred['probability']*100:.0f}% | {pred['target_range']} | {pred['key_levels']} |\n"
        
        md += """
### 3.2 重点关注
"""
        
        for i, event in enumerate(report.get('key_events', []), 1):
            md += f"{i}. {event}\n"
        
        md += f"""
---

*报告生成时间: {report['generated_at']}*  
*数据来源: 综合各专业机构*
"""
        
        return md


class AlertNotificationGenerator:
    """预警通知生成器"""
    
    LEVEL_ICONS = {
        'red': '🔴',
        'orange': '🟠',
        'yellow': '🟡',
        'blue': '🔵'
    }
    
    LEVEL_LABELS = {
        'red': '红色预警',
        'orange': '橙色预警',
        'yellow': '黄色预警',
        'blue': '蓝色预警'
    }
    
    @staticmethod
    def generate(alert: Dict) -> Dict:
        """生成预警通知"""
        return {
            "alert_id": alert.get('id', f"ALT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"),
            "timestamp": datetime.now().isoformat(),
            "level": alert['level'],
            "level_label": AlertNotificationGenerator.LEVEL_LABELS.get(alert['level'], '预警'),
            "level_icon": AlertNotificationGenerator.LEVEL_ICONS.get(alert['level'], '⚪'),
            "product": alert.get('product', 'Unknown'),
            "alert_type": alert['type'],
            "title": alert.get('title', alert['message']),
            "message": alert['message'],
            "content": alert.get('content', {}),
            "recommendation": alert.get('recommendation', ''),
            "channels": alert.get('channels', ['web'])
        }
    
    @staticmethod
    def to_text(notification: Dict) -> str:
        """转换为纯文本格式"""
        text = f"""
{notification['level_icon']} 能化市场预警通知

{'=' * 30}
预警等级: {notification['level_icon']} {notification['level_label']}
预警时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
{'=' * 30}

【品种】{notification['product']}
【类型】{notification['title']}
"""
        
        content = notification.get('content', {})
        if 'before' in content and 'after' in content:
            text += f"【变化】{content['before']:.1f} → {content['after']:.1f}"
            if 'change_percent' in content:
                text += f" ({content['change_percent']})"
            text += "\n"
        
        if 'trigger_factors' in content:
            text += "\n【触发因素】\n"
            for factor in content['trigger_factors']:
                text += f"• {factor}\n"
        
        if notification.get('recommendation'):
            text += f"\n【建议操作】\n{notification['recommendation']}\n"
        
        text += f"""
{'=' * 30}
点击查看详细分析 → [链接]
{'=' * 30}

本预警由能源化工新闻分析系统自动生成
"""
        return text
    
    @staticmethod
    def to_html(notification: Dict) -> str:
        """转换为HTML格式"""
        level_colors = {
            'red': '#f44336',
            'orange': '#ff9800',
            'yellow': '#ffc107',
            'blue': '#2196f3'
        }
        color = level_colors.get(notification['level'], '#999')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
                .alert-card {{ max-width: 500px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
                .header {{ background: {color}; color: white; padding: 20px; text-align: center; }}
                .level-icon {{ font-size: 36px; margin-bottom: 10px; }}
                .level-text {{ font-size: 20px; font-weight: bold; }}
                .time {{ font-size: 12px; opacity: 0.8; margin-top: 5px; }}
                .body {{ padding: 20px; }}
                .section {{ margin-bottom: 15px; }}
                .section-title {{ font-size: 12px; color: #666; margin-bottom: 5px; }}
                .section-content {{ font-size: 14px; color: #333; }}
                .highlight {{ background: #fff3cd; padding: 10px; border-radius: 6px; border-left: 4px solid {color}; }}
                .footer {{ background: #f5f5f5; padding: 15px; text-align: center; font-size: 12px; color: #999; }}
                .btn {{ display: inline-block; background: {color}; color: white; padding: 10px 30px; border-radius: 20px; text-decoration: none; margin-top: 10px; }}
            </style>
        </head>
        <body>
            <div class="alert-card">
                <div class="header">
                    <div class="level-icon">{notification['level_icon']}</div>
                    <div class="level-text">{notification['level_label']}</div>
                    <div class="time">{datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
                </div>
                <div class="body">
                    <div class="section">
                        <div class="section-title">品种</div>
                        <div class="section-content" style="font-size: 18px; font-weight: bold;">{notification['product']}</div>
                    </div>
                    <div class="section">
                        <div class="section-title">预警内容</div>
                        <div class="highlight">{notification['title']}</div>
                    </div>
        """
        
        content = notification.get('content', {})
        if 'before' in content and 'after' in content:
            html += f"""
                    <div class="section">
                        <div class="section-title">评分变化</div>
                        <div class="section-content" style="font-size: 24px; font-weight: bold; color: {color};">
                            {content['before']:.1f} → {content['after']:.1f}
                        </div>
                    </div>
            """
        
        if notification.get('recommendation'):
            html += f"""
                    <div class="section">
                        <div class="section-title">建议操作</div>
                        <div class="section-content">{notification['recommendation']}</div>
                    </div>
            """
        
        html += """
                    <a href="#" class="btn">查看详细分析</a>
                </div>
                <div class="footer">
                    本预警由能源化工新闻分析系统自动生成
                </div>
            </div>
        </body>
        </html>
        """
        
        return html


# ==================== 使用示例 ====================

def demo():
    """演示报告生成"""
    
    # 1. 实时报告
    print("=" * 60)
    print("实时分析报告示例")
    print("=" * 60)
    
    analysis_result = {
        'product': 'WTI原油',
        'composite_score': 72.5,
        'rating': '看涨',
        'rating_color': '#69F0AE',
        'change_1h': 2.3,
        'change_24h': 5.8,
        'dimension_breakdown': {
            'fundamental': 75.0,
            'macro': 60.0,
            'sentiment': 70.0,
            'technical': 65.0
        },
        'geo_adjustment': 8.5,
        'geo_risk_events': [
            {'type': 'conflict', 'description': '中东局势紧张', 'severity': 4}
        ],
        'key_drivers': [
            'EIA库存超预期下降',
            '地缘风险溢价上升',
            '技术突破关键阻力位'
        ],
        'prediction': {
            '1d': {'direction': 'up', 'probability': 0.65, 'confidence': 'medium'},
            '3d': {'direction': 'up', 'probability': 0.70, 'confidence': 'high'}
        }
    }
    
    realtime_report = RealtimeReportGenerator.generate(analysis_result)
    print(json.dumps(realtime_report, indent=2, ensure_ascii=False))
    
    # 2. 日报
    print("\n" + "=" * 60)
    print("日报示例")
    print("=" * 60)
    
    product_scores = [
        {'product': 'WTI', 'composite_score': 72.5, 'rating': '看涨', 'change_24h': 2.3, 'key_driver': '库存下降'},
        {'product': 'Brent', 'composite_score': 68.3, 'rating': '偏看涨', 'change_24h': 1.5, 'key_driver': '供应担忧'},
        {'product': 'JKM', 'composite_score': 61.7, 'rating': '偏看涨', 'change_24h': 1.8, 'key_driver': '需求预期'},
        {'product': 'HH', 'composite_score': 55.2, 'rating': '中性', 'change_24h': -0.8, 'key_driver': '天气温和'},
        {'product': 'PG', 'composite_score': 48.9, 'rating': '偏看跌', 'change_24h': -1.5, 'key_driver': '需求疲软'}
    ]
    
    alerts = [
        {'level': 'orange', 'type': 'composite_change', 'product': 'WTI', 'message': '评分显著上升', 'time': '14:30'},
        {'level': 'yellow', 'type': 'technical_breakout', 'product': 'Brent', 'message': '突破关键阻力', 'time': '10:15'}
    ]
    
    daily_report = DailyReportGenerator.generate(product_scores, alerts)
    print(DailyReportGenerator.to_markdown(daily_report))
    
    # 3. 预警通知
    print("\n" + "=" * 60)
    print("预警通知示例")
    print("=" * 60)
    
    alert = {
        'id': 'ALT-20240115-001',
        'level': 'orange',
        'product': 'WTI原油',
        'type': 'composite_significant_change',
        'title': '综合评分显著变化',
        'message': 'WTI综合评分从60.2上升至72.5',
        'content': {
            'before': 60.2,
            'after': 72.5,
            'change_percent': '+20.4%',
            'trigger_factors': [
                'EIA库存超预期下降500万桶',
                '地缘风险溢价上升'
            ]
        },
        'recommendation': '关注78美元阻力位突破情况',
        'channels': ['web', 'app', 'email']
    }
    
    notification = AlertNotificationGenerator.generate(alert)
    print(AlertNotificationGenerator.to_text(notification))


if __name__ == '__main__':
    demo()
