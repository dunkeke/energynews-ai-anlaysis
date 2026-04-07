import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Badge, List, Tag, Spin, Alert } from 'antd';
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  WarningOutlined,
  FileTextOutlined,
  BarChartOutlined,
  GlobalOutlined
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import axios from 'axios';
import moment from 'moment';

interface ScoreCard {
  commodity: string;
  score: number;
  rating: string;
  signal: string;
  change_24h: number;
  trend: string;
}

interface AlertItem {
  id: string;
  level: string;
  message: string;
  timestamp: string;
  commodity?: string;
}

interface NewsItem {
  id: string;
  title: string;
  source: string;
  crawl_time: string;
  commodity_tags: string[];
  sentiment?: string;
}

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [scoreCards, setScoreCards] = useState<ScoreCard[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [topNews, setTopNews] = useState<NewsItem[]>([]);
  const [marketOverview, setMarketOverview] = useState<any>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 60000); // 每分钟刷新
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/v1/visualization/dashboard');
      const data = response.data;
      
      setScoreCards(data.score_cards || []);
      setAlerts(data.recent_alerts || []);
      setTopNews(data.top_news || []);
      setMarketOverview(data.market_overview || {});
      setError(null);
    } catch (err) {
      console.error('获取仪表盘数据失败:', err);
      setError('获取数据失败，请稍后重试');
      // 使用模拟数据
      loadMockData();
    } finally {
      setLoading(false);
    }
  };

  const loadMockData = () => {
    // 模拟评分卡片数据
    setScoreCards([
      { commodity: 'WTI', score: 72.5, rating: '看涨', signal: '买入', change_24h: 3.2, trend: 'up' },
      { commodity: 'Brent', score: 68.3, rating: '偏看涨', signal: '持有', change_24h: 1.8, trend: 'up' },
      { commodity: 'HH', score: 55.2, rating: '中性', signal: '持有', change_24h: -0.5, trend: 'stable' },
      { commodity: 'TTF', score: 61.7, rating: '偏看涨', signal: '持有', change_24h: 2.1, trend: 'up' },
      { commodity: 'JKM', score: 58.9, rating: '中性', signal: '持有', change_24h: 0.8, trend: 'stable' },
    ]);

    // 模拟预警数据
    setAlerts([
      { id: '1', level: 'red', message: 'WTI地缘风险急剧上升', timestamp: new Date().toISOString(), commodity: 'WTI' },
      { id: '2', level: 'orange', message: 'Brent基本面评分显著变化', timestamp: new Date().toISOString(), commodity: 'Brent' },
      { id: '3', level: 'yellow', message: 'HH综合评分连续下降', timestamp: new Date().toISOString(), commodity: 'HH' },
    ]);

    // 模拟新闻数据
    setTopNews([
      { id: '1', title: 'OPEC+同意延长减产协议至二季度', source: 'Reuters', crawl_time: new Date().toISOString(), commodity_tags: ['WTI', 'Brent'], sentiment: 'positive' },
      { id: '2', title: 'EIA原油库存超预期增加500万桶', source: 'EIA', crawl_time: new Date().toISOString(), commodity_tags: ['WTI'], sentiment: 'negative' },
      { id: '3', title: '欧洲天然气库存降至历史低位', source: 'Platts', crawl_time: new Date().toISOString(), commodity_tags: ['TTF'], sentiment: 'positive' },
      { id: '4', title: '美联储暗示可能暂停加息', source: 'Bloomberg', crawl_time: new Date().toISOString(), commodity_tags: ['WTI', 'Brent'], sentiment: 'positive' },
      { id: '5', title: '中国原油进口量同比增长8%', source: '新浪财经', crawl_time: new Date().toISOString(), commodity_tags: ['WTI', 'Brent'], sentiment: 'positive' },
    ]);

    setMarketOverview({
      total_news_24h: 156,
      analyzed_news_24h: 142,
      active_alerts: 8,
      avg_sentiment: 0.15,
      market_status: 'active'
    });
  };

  const getScoreColor = (score: number) => {
    if (score >= 70) return '#52c41a';
    if (score >= 60) return '#95de64';
    if (score >= 45) return '#faad14';
    if (score >= 30) return '#ff7a45';
    return '#ff4d4f';
  };

  const getAlertColor = (level: string) => {
    switch (level) {
      case 'red': return 'red';
      case 'orange': return 'orange';
      case 'yellow': return 'yellow';
      case 'blue': return 'blue';
      default: return 'default';
    }
  };

  const getRadarOption = () => {
    return {
      title: {
        text: '品种多维度评分对比'
      },
      tooltip: {},
      legend: {
        data: ['WTI', 'Brent', 'HH']
      },
      radar: {
        indicator: [
          { name: '基本面', max: 100 },
          { name: '宏观面', max: 100 },
          { name: '情绪面', max: 100 },
          { name: '技术面', max: 100 },
          { name: '地缘风险', max: 100 }
        ]
      },
      series: [{
        type: 'radar',
        data: [
          {
            value: [75, 60, 70, 65, 45],
            name: 'WTI',
            areaStyle: { opacity: 0.3 }
          },
          {
            value: [70, 55, 65, 70, 40],
            name: 'Brent',
            areaStyle: { opacity: 0.3 }
          },
          {
            value: [65, 50, 60, 55, 35],
            name: 'HH',
            areaStyle: { opacity: 0.3 }
          }
        ]
      }]
    };
  };

  const getTrendOption = () => {
    return {
      title: {
        text: 'WTI评分趋势'
      },
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: ['1d', '3d', '5d', '7d', '10d', '15d', '20d', '30d']
      },
      yAxis: {
        type: 'value',
        min: 0,
        max: 100
      },
      series: [{
        data: [55, 58, 62, 60, 65, 68, 70, 72],
        type: 'line',
        smooth: true,
        areaStyle: {
          opacity: 0.3
        },
        lineStyle: {
          width: 3
        }
      }]
    };
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <p>加载中...</p>
      </div>
    );
  }

  return (
    <div>
      {error && (
        <Alert
          message="错误"
          description={error}
          type="error"
          closable
          style={{ marginBottom: 24 }}
        />
      )}

      {/* 市场概览统计 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="24小时新闻数"
              value={marketOverview.total_news_24h || 0}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="已分析新闻"
              value={marketOverview.analyzed_news_24h || 0}
              prefix={<BarChartOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="活跃预警"
              value={marketOverview.active_alerts || 0}
              prefix={<WarningOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="市场情绪"
              value={marketOverview.avg_sentiment || 0}
              precision={2}
              prefix={<GlobalOutlined />}
              valueStyle={{ color: (marketOverview.avg_sentiment || 0) >= 0 ? '#3f8600' : '#cf1322' }}
              suffix={(marketOverview.avg_sentiment || 0) >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 评分卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        {scoreCards.map((card) => (
          <Col span={4} key={card.commodity}>
            <Card
              style={{
                borderTop: `4px solid ${getScoreColor(card.score)}`,
                textAlign: 'center'
              }}
            >
              <h3 style={{ margin: '0 0 8px 0' }}>{card.commodity}</h3>
              <div style={{ fontSize: '32px', fontWeight: 'bold', color: getScoreColor(card.score) }}>
                {card.score}
              </div>
              <div style={{ marginTop: 8 }}>
                <Tag color={getScoreColor(card.score)}>{card.rating}</Tag>
              </div>
              <div style={{ marginTop: 8, fontSize: '12px', color: '#666' }}>
                24h: 
                <span style={{ 
                  color: card.change_24h >= 0 ? '#52c41a' : '#ff4d4f',
                  marginLeft: 4
                }}>
                  {card.change_24h >= 0 ? '+' : ''}{card.change_24h}
                </span>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      {/* 图表区域 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={12}>
          <Card title="多维度评分对比">
            <ReactECharts option={getRadarOption()} style={{ height: 350 }} />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="WTI评分趋势">
            <ReactECharts option={getTrendOption()} style={{ height: 350 }} />
          </Card>
        </Col>
      </Row>

      {/* 预警和新闻 */}
      <Row gutter={16}>
        <Col span={12}>
          <Card 
            title="最近预警" 
            extra={<a href="#">查看全部</a>}
          >
            <List
              dataSource={alerts}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={<Badge color={getAlertColor(item.level)} />}
                    title={item.message}
                    description={
                      <span>
                        {item.commodity && <Tag size="small">{item.commodity}</Tag>}
                        {moment(item.timestamp).fromNow()}
                      </span>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card 
            title="热门新闻" 
            extra={<a href="#">查看全部</a>}
          >
            <List
              dataSource={topNews}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    title={item.title}
                    description={
                      <span>
                        <Tag size="small">{item.source}</Tag>
                        {item.commodity_tags.map(tag => (
                          <Tag key={tag} size="small" color="blue">{tag}</Tag>
                        ))}
                        {moment(item.crawl_time).fromNow()}
                      </span>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
