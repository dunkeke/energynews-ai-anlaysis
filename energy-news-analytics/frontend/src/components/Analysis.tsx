import React, { useState, useEffect } from 'react';
import { 
  Card, Select, Button, Tabs, Table, Tag, Spin, 
  Row, Col, Statistic, Alert, DatePicker, Radio 
} from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined, BarChartOutlined } from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import axios from 'axios';
import moment from 'moment';

const { Option } = Select;
const { TabPane } = Tabs;
const { RangePicker } = DatePicker;

interface AnalysisResult {
  commodity: string;
  timestamp: string;
  composite_score: number;
  rating: string;
  signal: string;
  confidence: number;
  dimensions: any;
  key_factors: string[];
}

const Analysis: React.FC = () => {
  const [selectedCommodity, setSelectedCommodity] = useState<string>('WTI');
  const [timeRange, setTimeRange] = useState<string>('7d');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [trendData, setTrendData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const commodities = [
    { code: 'WTI', name: 'WTI原油' },
    { code: 'Brent', name: '布伦特原油' },
    { code: 'HH', name: '亨利港天然气' },
    { code: 'TTF', name: 'TTF天然气' },
    { code: 'JKM', name: 'JKM天然气' },
    { code: 'PG', name: '丙烷' },
    { code: 'CP', name: '沙特CP' },
    { code: 'FEI', name: '远东指数' },
  ];

  useEffect(() => {
    fetchAnalysis();
  }, [selectedCommodity, timeRange]);

  const fetchAnalysis = async () => {
    try {
      setLoading(true);
      
      // 并行请求分析结果和趋势数据
      const [analysisRes, trendRes] = await Promise.all([
        axios.post(`/api/v1/analysis/${selectedCommodity}`, {
          lookback_days: parseInt(timeRange),
          dimensions: ['fundamental', 'macro', 'sentiment', 'technical', 'geopolitical']
        }),
        axios.get(`/api/v1/visualization/trend/${selectedCommodity}`, {
          params: { days: parseInt(timeRange) }
        })
      ]);
      
      setResult(analysisRes.data);
      setTrendData(trendRes.data);
      setError(null);
    } catch (err) {
      console.error('获取分析数据失败:', err);
      setError('获取分析数据失败');
      // 使用模拟数据
      loadMockData();
    } finally {
      setLoading(false);
    }
  };

  const loadMockData = () => {
    setResult({
      commodity: selectedCommodity,
      timestamp: new Date().toISOString(),
      composite_score: 72.5,
      rating: '看涨',
      signal: '买入',
      confidence: 0.85,
      dimensions: {
        fundamental: { score: 75, weight: 0.30, confidence: 0.9, keywords: ['库存下降', '产量减少'] },
        macro: { score: 60, weight: 0.15, confidence: 0.8, keywords: ['美元走弱'] },
        sentiment: { score: 70, weight: 0.20, confidence: 0.85, keywords: ['持仓增加', '情绪乐观'] },
        technical: { score: 65, weight: 0.20, confidence: 0.75, keywords: ['突破阻力'] },
        geopolitical: { score: 45, weight: 0.15, confidence: 0.7, keywords: ['中东紧张'] }
      },
      key_factors: ['OPEC减产', '库存下降', '美元走弱', '地缘紧张']
    });

    setTrendData({
      commodity: selectedCommodity,
      days: parseInt(timeRange),
      data: Array.from({ length: 10 }, (_, i) => ({
        timestamp: moment().subtract(10 - i, 'days').toISOString(),
        composite_score: 60 + Math.random() * 20,
        dimensions: {
          fundamental: 60 + Math.random() * 20,
          macro: 60 + Math.random() * 20,
          sentiment: 60 + Math.random() * 20,
          technical: 60 + Math.random() * 20,
          geopolitical: 60 + Math.random() * 20
        }
      }))
    });
  };

  const getScoreColor = (score: number) => {
    if (score >= 70) return '#52c41a';
    if (score >= 60) return '#95de64';
    if (score >= 45) return '#faad14';
    if (score >= 30) return '#ff7a45';
    return '#ff4d4f';
  };

  const getRadarOption = () => {
    if (!result) return {};
    
    const dimensions = result.dimensions;
    return {
      tooltip: {},
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
        data: [{
          value: [
            dimensions.fundamental?.score || 50,
            dimensions.macro?.score || 50,
            dimensions.sentiment?.score || 50,
            dimensions.technical?.score || 50,
            dimensions.geopolitical?.score || 50
          ],
          name: selectedCommodity,
          areaStyle: { opacity: 0.3 }
        }]
      }]
    };
  };

  const getTrendOption = () => {
    if (!trendData) return {};
    
    return {
      tooltip: { trigger: 'axis' },
      legend: {
        data: ['综合评分', '基本面', '情绪面', '技术面']
      },
      xAxis: {
        type: 'category',
        data: trendData.data.map((d: any) => moment(d.timestamp).format('MM-DD'))
      },
      yAxis: {
        type: 'value',
        min: 0,
        max: 100
      },
      series: [
        {
          name: '综合评分',
          type: 'line',
          data: trendData.data.map((d: any) => d.composite_score.toFixed(1)),
          smooth: true,
          lineStyle: { width: 3 },
          areaStyle: { opacity: 0.2 }
        },
        {
          name: '基本面',
          type: 'line',
          data: trendData.data.map((d: any) => d.dimensions.fundamental.toFixed(1)),
          smooth: true,
          lineStyle: { width: 2, type: 'dashed' }
        },
        {
          name: '情绪面',
          type: 'line',
          data: trendData.data.map((d: any) => d.dimensions.sentiment.toFixed(1)),
          smooth: true,
          lineStyle: { width: 2, type: 'dashed' }
        },
        {
          name: '技术面',
          type: 'line',
          data: trendData.data.map((d: any) => d.dimensions.technical.toFixed(1)),
          smooth: true,
          lineStyle: { width: 2, type: 'dashed' }
        }
      ]
    };
  };

  const dimensionColumns = [
    {
      title: '维度',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => <strong>{text}</strong>
    },
    {
      title: '评分',
      dataIndex: 'score',
      key: 'score',
      render: (score: number) => (
        <span style={{ 
          color: getScoreColor(score),
          fontWeight: 'bold',
          fontSize: '16px'
        }}>
          {score.toFixed(1)}
        </span>
      )
    },
    {
      title: '权重',
      dataIndex: 'weight',
      key: 'weight',
      render: (weight: number) => `${(weight * 100).toFixed(0)}%`
    },
    {
      title: '置信度',
      dataIndex: 'confidence',
      key: 'confidence',
      render: (confidence: number) => (
        <Tag color={confidence >= 0.8 ? 'green' : confidence >= 0.6 ? 'orange' : 'red'}>
          {(confidence * 100).toFixed(0)}%
        </Tag>
      )
    },
    {
      title: '关键词',
      dataIndex: 'keywords',
      key: 'keywords',
      render: (keywords: string[]) => (
        <span>
          {keywords.map((kw, i) => (
            <Tag key={i} size="small">{kw}</Tag>
          ))}
        </span>
      )
    }
  ];

  const getDimensionData = () => {
    if (!result) return [];
    
    const dimNames: {[key: string]: string} = {
      fundamental: '基本面',
      macro: '宏观面',
      sentiment: '情绪面',
      technical: '技术面',
      geopolitical: '地缘风险'
    };
    
    return Object.entries(result.dimensions).map(([key, value]: [string, any]) => ({
      key,
      name: dimNames[key] || key,
      score: value.score || 0,
      weight: value.weight || 0,
      confidence: value.confidence || 0,
      keywords: value.keywords || []
    }));
  };

  return (
    <div>
      <Card style={{ marginBottom: 24 }}>
        <Row gutter={16} align="middle">
          <Col span={6}>
            <label>选择品种：</label>
            <Select
              value={selectedCommodity}
              onChange={setSelectedCommodity}
              style={{ width: '100%' }}
            >
              {commodities.map(c => (
                <Option key={c.code} value={c.code}>{c.name}</Option>
              ))}
            </Select>
          </Col>
          <Col span={6}>
            <label>时间范围：</label>
            <Radio.Group 
              value={timeRange} 
              onChange={(e) => setTimeRange(e.target.value)}
            >
              <Radio.Button value="1d">1天</Radio.Button>
              <Radio.Button value="7d">7天</Radio.Button>
              <Radio.Button value="30d">30天</Radio.Button>
              <Radio.Button value="90d">90天</Radio.Button>
            </Radio.Group>
          </Col>
          <Col span={6}>
            <Button 
              type="primary" 
              icon={<BarChartOutlined />}
              onClick={fetchAnalysis}
              loading={loading}
            >
              重新分析
            </Button>
          </Col>
        </Row>
      </Card>

      {error && (
        <Alert
          message="错误"
          description={error}
          type="error"
          closable
          style={{ marginBottom: 24 }}
        />
      )}

      {result && (
        <>
          {/* 综合评分卡片 */}
          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col span={6}>
              <Card style={{ textAlign: 'center', borderTop: `4px solid ${getScoreColor(result.composite_score)}` }}>
                <h3>综合评分</h3>
                <div style={{ 
                  fontSize: '48px', 
                  fontWeight: 'bold',
                  color: getScoreColor(result.composite_score)
                }}>
                  {result.composite_score.toFixed(1)}
                </div>
                <Tag color={getScoreColor(result.composite_score)} style={{ fontSize: '14px' }}>
                  {result.rating}
                </Tag>
              </Card>
            </Col>
            <Col span={6}>
              <Card style={{ textAlign: 'center', borderTop: '4px solid #1890ff' }}>
                <h3>交易信号</h3>
                <div style={{ fontSize: '24px', fontWeight: 'bold', marginTop: '16px' }}>
                  {result.signal}
                </div>
                <div style={{ marginTop: '8px', color: '#666' }}>
                  置信度: {(result.confidence * 100).toFixed(0)}%
                </div>
              </Card>
            </Col>
            <Col span={12}>
              <Card title="关键因子">
                <div>
                  {result.key_factors.map((factor, i) => (
                    <Tag key={i} color="blue" style={{ fontSize: '14px', margin: '4px' }}>
                      {factor}
                    </Tag>
                  ))}
                </div>
              </Card>
            </Col>
          </Row>

          {/* 图表和表格 */}
          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col span={12}>
              <Card title="多维度评分">
                <ReactECharts option={getRadarOption()} style={{ height: 350 }} />
              </Card>
            </Col>
            <Col span={12}>
              <Card title="评分趋势">
                <ReactECharts option={getTrendOption()} style={{ height: 350 }} />
              </Card>
            </Col>
          </Row>

          <Card title="维度详情">
            <Table 
              columns={dimensionColumns}
              dataSource={getDimensionData()}
              pagination={false}
            />
          </Card>
        </>
      )}
    </div>
  );
};

export default Analysis;
