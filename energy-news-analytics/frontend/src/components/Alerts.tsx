import React, { useState, useEffect } from 'react';
import { 
  Card, Table, Tag, Button, Badge, Select, DatePicker, 
  Alert, Spin, Empty, Modal 
} from 'antd';
import { CheckOutlined, WarningOutlined, InfoCircleOutlined } from '@ant-design/icons';
import axios from 'axios';
import moment from 'moment';

const { Option } = Select;
const { RangePicker } = DatePicker;

interface AlertItem {
  id: string;
  level: string;
  type: string;
  commodity?: string;
  message: string;
  details: any;
  timestamp: string;
  is_read: boolean;
}

const Alerts: React.FC = () => {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({
    level: undefined,
    commodity: undefined,
    unread_only: false
  });
  const [selectedAlert, setSelectedAlert] = useState<AlertItem | null>(null);
  const [detailVisible, setDetailVisible] = useState(false);

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 30000); // 每30秒刷新
    return () => clearInterval(interval);
  }, [filter]);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      
      const params: any = {};
      if (filter.level) params.level = filter.level;
      if (filter.commodity) params.commodity = filter.commodity;
      if (filter.unread_only) params.unread_only = true;
      
      const response = await axios.get('/api/v1/alerts', { params });
      setAlerts(response.data);
    } catch (err) {
      console.error('获取预警列表失败:', err);
      // 使用模拟数据
      loadMockAlerts();
    } finally {
      setLoading(false);
    }
  };

  const loadMockAlerts = () => {
    setAlerts([
      {
        id: '1',
        level: 'red',
        type: 'geopolitical_risk',
        commodity: 'WTI',
        message: 'WTI地缘风险急剧上升 (+12.5)',
        details: { event_type: '中东冲突', importance: 95 },
        timestamp: new Date(Date.now() - 5 * 60000).toISOString(),
        is_read: false
      },
      {
        id: '2',
        level: 'orange',
        type: 'composite_significant_change',
        commodity: 'Brent',
        message: 'Brent基本面评分显著变化 (45→62)',
        details: { previous_score: 45, current_score: 62, change: 17 },
        timestamp: new Date(Date.now() - 15 * 60000).toISOString(),
        is_read: false
      },
      {
        id: '3',
        level: 'yellow',
        type: 'consecutive_down_trend',
        commodity: 'HH',
        message: 'HH综合评分连续下降3周期',
        details: { periods: 3, total_change: -15 },
        timestamp: new Date(Date.now() - 60 * 60000).toISOString(),
        is_read: true
      },
      {
        id: '4',
        level: 'blue',
        type: 'price_score_divergence',
        commodity: 'PG',
        message: 'PG价格与评分出现背离',
        details: { price_trend: 'up', score_trend: 'down' },
        timestamp: new Date(Date.now() - 120 * 60000).toISOString(),
        is_read: true
      },
      {
        id: '5',
        level: 'red',
        type: 'geopolitical_risk',
        commodity: 'TTF',
        message: 'TTF地缘风险事件：俄乌冲突升级',
        details: { event_type: '地缘冲突', severity: 'high' },
        timestamp: new Date(Date.now() - 180 * 60000).toISOString(),
        is_read: false
      }
    ]);
  };

  const markAsRead = async (alertId: string) => {
    try {
      await axios.post(`/api/v1/alerts/${alertId}/read`);
      // 更新本地状态
      setAlerts(alerts.map(alert => 
        alert.id === alertId ? { ...alert, is_read: true } : alert
      ));
    } catch (err) {
      console.error('标记已读失败:', err);
    }
  };

  const markAllAsRead = async () => {
    try {
      const unreadAlerts = alerts.filter(a => !a.is_read);
      await Promise.all(unreadAlerts.map(a => axios.post(`/api/v1/alerts/${a.id}/read`)));
      setAlerts(alerts.map(alert => ({ ...alert, is_read: true })));
    } catch (err) {
      console.error('标记全部已读失败:', err);
    }
  };

  const showDetail = (alert: AlertItem) => {
    setSelectedAlert(alert);
    setDetailVisible(true);
    if (!alert.is_read) {
      markAsRead(alert.id);
    }
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'red': return 'red';
      case 'orange': return 'orange';
      case 'yellow': return 'yellow';
      case 'blue': return 'blue';
      default: return 'default';
    }
  };

  const getLevelText = (level: string) => {
    switch (level) {
      case 'red': return '红色';
      case 'orange': return '橙色';
      case 'yellow': return '黄色';
      case 'blue': return '蓝色';
      default: return level;
    }
  };

  const getLevelIcon = (level: string) => {
    switch (level) {
      case 'red': return <WarningOutlined style={{ color: '#ff4d4f' }} />;
      case 'orange': return <WarningOutlined style={{ color: '#faad14' }} />;
      case 'yellow': return <InfoCircleOutlined style={{ color: '#fadb14' }} />;
      case 'blue': return <InfoCircleOutlined style={{ color: '#1890ff' }} />;
      default: return <InfoCircleOutlined />;
    }
  };

  const columns = [
    {
      title: '级别',
      dataIndex: 'level',
      key: 'level',
      width: 80,
      render: (level: string) => (
        <Tag color={getLevelColor(level)}>{getLevelText(level)}</Tag>
      )
    },
    {
      title: '品种',
      dataIndex: 'commodity',
      key: 'commodity',
      width: 100,
      render: (commodity: string) => commodity || '-'
    },
    {
      title: '预警内容',
      dataIndex: 'message',
      key: 'message',
      render: (message: string, record: AlertItem) => (
        <span 
          style={{ 
            cursor: 'pointer',
            fontWeight: record.is_read ? 'normal' : 'bold'
          }}
          onClick={() => showDetail(record)}
        >
          {!record.is_read && <Badge status="processing" style={{ marginRight: 8 }} />}
          {message}
        </span>
      )
    },
    {
      title: '时间',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 150,
      render: (timestamp: string) => moment(timestamp).fromNow()
    },
    {
      title: '状态',
      dataIndex: 'is_read',
      key: 'is_read',
      width: 100,
      render: (is_read: boolean, record: AlertItem) => (
        is_read ? (
          <Tag icon={<CheckOutlined />} color="success">已读</Tag>
        ) : (
          <Button 
            type="link" 
            size="small"
            onClick={() => markAsRead(record.id)}
          >
            标记已读
          </Button>
        )
      )
    }
  ];

  const unreadCount = alerts.filter(a => !a.is_read).length;

  return (
    <div>
      <h2>预警中心</h2>
      <p>监控系统异常和重要事件，及时获取风险提醒</p>
      
      <Card style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <div>
            <span style={{ marginRight: 16 }}>
              未读预警: <Badge count={unreadCount} style={{ backgroundColor: '#ff4d4f' }} />
            </span>
            <Button 
              type="primary" 
              size="small"
              disabled={unreadCount === 0}
              onClick={markAllAsRead}
            >
              全部标记已读
            </Button>
          </div>
          <div>
            <Select
              placeholder="筛选级别"
              style={{ width: 120, marginRight: 8 }}
              allowClear
              onChange={(value) => setFilter({ ...filter, level: value })}
            >
              <Option value="red">红色</Option>
              <Option value="orange">橙色</Option>
              <Option value="yellow">黄色</Option>
              <Option value="blue">蓝色</Option>
            </Select>
            <Select
              placeholder="筛选品种"
              style={{ width: 120, marginRight: 8 }}
              allowClear
              onChange={(value) => setFilter({ ...filter, commodity: value })}
            >
              <Option value="WTI">WTI</Option>
              <Option value="Brent">Brent</Option>
              <Option value="HH">HH</Option>
              <Option value="TTF">TTF</Option>
              <Option value="JKM">JKM</Option>
              <Option value="PG">PG</Option>
            </Select>
            <Select
              placeholder="阅读状态"
              style={{ width: 120 }}
              allowClear
              onChange={(value) => setFilter({ ...filter, unread_only: value === 'unread' })}
            >
              <Option value="unread">未读</Option>
              <Option value="read">已读</Option>
            </Select>
          </div>
        </div>
        
        {loading ? (
          <Spin size="large" style={{ display: 'block', textAlign: 'center', padding: '50px' }} />
        ) : alerts.length > 0 ? (
          <Table
            columns={columns}
            dataSource={alerts}
            rowKey="id"
            pagination={{ pageSize: 10 }}
          />
        ) : (
          <Empty description="暂无预警" />
        )}
      </Card>

      <Card title="预警说明">
        <div style={{ display: 'flex', gap: 24 }}>
          <div>
            <Tag color="red">红色预警</Tag>
            <span>综合评分突变±20分或地缘风险>10，需立即关注</span>
          </div>
          <div>
            <Tag color="orange">橙色预警</Tag>
            <span>单维度评分突变±15分或综合评分±15分，15分钟内响应</span>
          </div>
          <div>
            <Tag color="yellow">黄色预警</Tag>
            <span>连续3个周期评分同向变化>10分，1小时内关注</span>
          </div>
          <div>
            <Tag color="blue">蓝色预警</Tag>
            <span>评分趋势与价格背离，日报中提示</span>
          </div>
        </div>
      </Card>

      <Modal
        title="预警详情"
        visible={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailVisible(false)}>
            关闭
          </Button>
        ]}
        width={600}
      >
        {selectedAlert && (
          <div>
            <div style={{ marginBottom: 16 }}>
              <Tag color={getLevelColor(selectedAlert.level)} style={{ fontSize: '16px', padding: '4px 12px' }}>
                {getLevelText(selectedAlert.level)}预警
              </Tag>
            </div>
            <p><strong>预警类型：</strong>{selectedAlert.type}</p>
            <p><strong>关联品种：</strong>{selectedAlert.commodity || '-'}</p>
            <p><strong>预警时间：</strong>{moment(selectedAlert.timestamp).format('YYYY-MM-DD HH:mm:ss')}</p>
            <p><strong>预警内容：</strong></p>
            <div style={{ background: '#f5f5f5', padding: 16, borderRadius: 4 }}>
              {selectedAlert.message}
            </div>
            {selectedAlert.details && (
              <>
                <p style={{ marginTop: 16 }}><strong>详细信息：</strong></p>
                <pre style={{ background: '#f5f5f5', padding: 16, borderRadius: 4, overflow: 'auto' }}>
                  {JSON.stringify(selectedAlert.details, null, 2)}
                </pre>
              </>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Alerts;
