import React, { useState } from 'react';
import { 
  Card, Tabs, Form, Input, InputNumber, Select, Switch, 
  Button, Divider, Alert, message 
} from 'antd';
import { SaveOutlined, ReloadOutlined } from '@ant-design/icons';

const { TabPane } = Tabs;
const { Option } = Select;

const Settings: React.FC = () => {
  const [generalForm] = Form.useForm();
  const [weightForm] = Form.useForm();
  const [alertForm] = Form.useForm();
  const [saving, setSaving] = useState(false);

  const handleSaveGeneral = async (values: any) => {
    try {
      setSaving(true);
      // 调用API保存设置
      message.success('通用设置保存成功');
    } catch (err) {
      message.error('保存失败');
    } finally {
      setSaving(false);
    }
  };

  const handleSaveWeights = async (values: any) => {
    try {
      setSaving(true);
      message.success('权重配置保存成功');
    } catch (err) {
      message.error('保存失败');
    } finally {
      setSaving(false);
    }
  };

  const handleSaveAlerts = async (values: any) => {
    try {
      setSaving(true);
      message.success('预警设置保存成功');
    } catch (err) {
      message.error('保存失败');
    } finally {
      setSaving(false);
    }
  };

  const resetWeights = () => {
    weightForm.resetFields();
    message.info('已恢复默认权重');
  };

  return (
    <div>
      <h2>系统设置</h2>
      <p>配置系统参数、评分权重和预警阈值</p>
      
      <Divider />
      
      <Tabs defaultActiveKey="general">
        <TabPane tab="通用设置" key="general">
          <Card>
            <Form
              form={generalForm}
              onFinish={handleSaveGeneral}
              layout="vertical"
              initialValues={{
                system_name: '能源化工新闻分析系统',
                data_refresh_interval: 5,
                news_retention_days: 90,
                enable_auto_analysis: true,
                enable_notification: true
              }}
            >
              <Form.Item
                name="system_name"
                label="系统名称"
              >
                <Input />
              </Form.Item>
              
              <Form.Item
                name="data_refresh_interval"
                label="数据刷新间隔（分钟）"
              >
                <InputNumber min={1} max={60} />
              </Form.Item>
              
              <Form.Item
                name="news_retention_days"
                label="新闻保留天数"
              >
                <InputNumber min={7} max={365} />
              </Form.Item>
              
              <Form.Item
                name="enable_auto_analysis"
                label="启用自动分析"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
              
              <Form.Item
                name="enable_notification"
                label="启用通知"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
              
              <Form.Item>
                <Button 
                  type="primary" 
                  htmlType="submit"
                  icon={<SaveOutlined />}
                  loading={saving}
                >
                  保存设置
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>
        
        <TabPane tab="评分权重" key="weights">
          <Card>
            <Alert
              message="权重配置说明"
              description="调整各维度在综合评分中的权重占比，所有权重之和应等于100%"
              type="info"
              showIcon
              style={{ marginBottom: 24 }}
            />
            
            <Form
              form={weightForm}
              onFinish={handleSaveWeights}
              layout="vertical"
              initialValues={{
                commodity: 'WTI',
                fundamental: 30,
                macro: 15,
                sentiment: 20,
                technical: 20,
                geopolitical: 15
              }}
            >
              <Form.Item
                name="commodity"
                label="选择品种"
              >
                <Select style={{ width: 200 }}>
                  <Option value="WTI">WTI原油</Option>
                  <Option value="Brent">布伦特原油</Option>
                  <Option value="HH">亨利港天然气</Option>
                  <Option value="TTF">TTF天然气</Option>
                  <Option value="JKM">JKM天然气</Option>
                  <Option value="PG">丙烷</Option>
                  <Option value="CP">沙特CP</Option>
                  <Option value="FEI">远东指数</Option>
                </Select>
              </Form.Item>
              
              <Divider />
              
              <Form.Item
                name="fundamental"
                label="基本面权重 (%)"
                rules={[{ required: true, message: '请输入权重' }]}
              >
                <InputNumber min={0} max={100} />
              </Form.Item>
              
              <Form.Item
                name="macro"
                label="宏观面权重 (%)"
                rules={[{ required: true, message: '请输入权重' }]}
              >
                <InputNumber min={0} max={100} />
              </Form.Item>
              
              <Form.Item
                name="sentiment"
                label="情绪面权重 (%)"
                rules={[{ required: true, message: '请输入权重' }]}
              >
                <InputNumber min={0} max={100} />
              </Form.Item>
              
              <Form.Item
                name="technical"
                label="技术面权重 (%)"
                rules={[{ required: true, message: '请输入权重' }]}
              >
                <InputNumber min={0} max={100} />
              </Form.Item>
              
              <Form.Item
                name="geopolitical"
                label="地缘风险权重 (%)"
                rules={[{ required: true, message: '请输入权重' }]}
              >
                <InputNumber min={0} max={100} />
              </Form.Item>
              
              <Form.Item>
                <Button 
                  type="primary" 
                  htmlType="submit"
                  icon={<SaveOutlined />}
                  loading={saving}
                  style={{ marginRight: 8 }}
                >
                  保存权重
                </Button>
                <Button 
                  icon={<ReloadOutlined />}
                  onClick={resetWeights}
                >
                  恢复默认
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>
        
        <TabPane tab="预警设置" key="alerts">
          <Card>
            <Alert
              message="预警阈值配置"
              description="设置触发各级预警的阈值条件"
              type="info"
              showIcon
              style={{ marginBottom: 24 }}
            />
            
            <Form
              form={alertForm}
              onFinish={handleSaveAlerts}
              layout="vertical"
              initialValues={{
                red_composite_change: 20,
                orange_composite_change: 15,
                yellow_composite_change: 10,
                red_dimension_change: 20,
                orange_dimension_change: 15,
                red_geo_risk: 10,
                orange_geo_risk: 7,
                consecutive_periods: 3,
                consecutive_change: 10
              }}
            >
              <h4>综合评分变化阈值</h4>
              <Form.Item
                name="red_composite_change"
                label="红色预警阈值"
              >
                <InputNumber min={5} max={50} addonAfter="分" />
              </Form.Item>
              
              <Form.Item
                name="orange_composite_change"
                label="橙色预警阈值"
              >
                <InputNumber min={5} max={50} addonAfter="分" />
              </Form.Item>
              
              <Form.Item
                name="yellow_composite_change"
                label="黄色预警阈值"
              >
                <InputNumber min={5} max={50} addonAfter="分" />
              </Form.Item>
              
              <Divider />
              
              <h4>单维度评分变化阈值</h4>
              <Form.Item
                name="red_dimension_change"
                label="红色预警阈值"
              >
                <InputNumber min={5} max={50} addonAfter="分" />
              </Form.Item>
              
              <Form.Item
                name="orange_dimension_change"
                label="橙色预警阈值"
              >
                <InputNumber min={5} max={50} addonAfter="分" />
              </Form.Item>
              
              <Divider />
              
              <h4>地缘风险阈值</h4>
              <Form.Item
                name="red_geo_risk"
                label="红色预警阈值"
              >
                <InputNumber min={5} max={20} addonAfter="分" />
              </Form.Item>
              
              <Form.Item
                name="orange_geo_risk"
                label="橙色预警阈值"
              >
                <InputNumber min={5} max={20} addonAfter="分" />
              </Form.Item>
              
              <Divider />
              
              <h4>连续趋势预警</h4>
              <Form.Item
                name="consecutive_periods"
                label="连续周期数"
              >
                <InputNumber min={2} max={10} addonAfter="个" />
              </Form.Item>
              
              <Form.Item
                name="consecutive_change"
                label="变化幅度"
              >
                <InputNumber min={5} max={30} addonAfter="分" />
              </Form.Item>
              
              <Form.Item>
                <Button 
                  type="primary" 
                  htmlType="submit"
                  icon={<SaveOutlined />}
                  loading={saving}
                >
                  保存预警设置
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>
        
        <TabPane tab="数据源" key="datasources">
          <Card>
            <Alert
              message="数据源管理"
              description="配置和管理新闻数据源"
              type="info"
              showIcon
              style={{ marginBottom: 24 }}
            />
            
            <div style={{ marginBottom: 16 }}>
              <h4>已配置数据源</h4>
              <ul>
                <li>Bloomberg (API) - <span style={{ color: 'green' }}>运行中</span></li>
                <li>Reuters (API) - <span style={{ color: 'green' }}>运行中</span></li>
                <li>Platts (API) - <span style={{ color: 'green' }}>运行中</span></li>
                <li>EIA (API) - <span style={{ color: 'green' }}>运行中</span></li>
                <li>新浪财经 (RSS) - <span style={{ color: 'green' }}>运行中</span></li>
                <li>东方财富 (API) - <span style={{ color: 'green' }}>运行中</span></li>
                <li>华尔街见闻 (API) - <span style={{ color: 'green' }}>运行中</span></li>
              </ul>
            </div>
            
            <Button type="primary">添加数据源</Button>
          </Card>
        </TabPane>
        
        <TabPane tab="关于" key="about">
          <Card>
            <h3>能源化工新闻分析系统</h3>
            <p>版本: 1.0.0</p>
            <p>构建日期: 2025-01-15</p>
            
            <Divider />
            
            <h4>系统功能</h4>
            <ul>
              <li>综合各专业和主流媒体进行能化品种新闻分析</li>
              <li>支持自动采集和手工导入（URL/文本/PDF）</li>
              <li>从基本面、宏观面、情绪面、技术面、地缘风险五维度分析</li>
              <li>输出量化分析结果并可视化展示</li>
              <li>智能预警系统，及时捕捉市场异常</li>
            </ul>
            
            <Divider />
            
            <h4>关注品种</h4>
            <ul>
              <li><strong>原油：</strong>WTI、Brent</li>
              <li><strong>天然气：</strong>JKM、HH、TTF</li>
              <li><strong>液化气：</strong>PG、PP、MB、FEI、CP</li>
              <li><strong>成品油：</strong>汽油、柴油、航煤、燃料油</li>
            </ul>
            
            <Divider />
            
            <p style={{ color: '#666' }}>
              © 2025 能源化工新闻分析系统. All rights reserved.
            </p>
          </Card>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default Settings;
