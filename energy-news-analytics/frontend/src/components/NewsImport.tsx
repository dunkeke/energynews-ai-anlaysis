import React, { useState } from 'react';
import { 
  Card, Tabs, Form, Input, Button, Upload, Select, 
  message, Alert, Spin, Result, Divider 
} from 'antd';
import { UploadOutlined, LinkOutlined, FileTextOutlined, FilePdfOutlined } from '@ant-design/icons';
import axios from 'axios';

const { TabPane } = Tabs;
const { TextArea } = Input;
const { Option } = Select;

const NewsImport: React.FC = () => {
  const [activeTab, setActiveTab] = useState('url');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [form] = Form.useForm();

  const commodities = [
    'WTI', 'Brent', 'HH', 'TTF', 'JKM', 'PG', 'PP', 'MB', 'FEI', 'CP', '成品油'
  ];

  const handleUrlSubmit = async (values: any) => {
    try {
      setLoading(true);
      setError(null);
      
      const formData = new FormData();
      formData.append('import_type', 'url');
      formData.append('content', values.url);
      formData.append('source', values.source || 'user_url');
      if (values.commodities) {
        values.commodities.forEach((c: string) => {
          formData.append('commodities', c);
        });
      }
      
      const response = await axios.post('/api/v1/news/import', formData);
      setResult(response.data);
      message.success('URL导入成功');
    } catch (err: any) {
      console.error('URL导入失败:', err);
      setError(err.response?.data?.detail || '导入失败');
      message.error('导入失败');
    } finally {
      setLoading(false);
    }
  };

  const handleTextSubmit = async (values: any) => {
    try {
      setLoading(true);
      setError(null);
      
      const formData = new FormData();
      formData.append('import_type', 'text');
      formData.append('content', values.text);
      formData.append('source', values.source || 'user_text');
      if (values.commodities) {
        values.commodities.forEach((c: string) => {
          formData.append('commodities', c);
        });
      }
      
      const response = await axios.post('/api/v1/news/import', formData);
      setResult(response.data);
      message.success('文本导入成功');
    } catch (err: any) {
      console.error('文本导入失败:', err);
      setError(err.response?.data?.detail || '导入失败');
      message.error('导入失败');
    } finally {
      setLoading(false);
    }
  };

  const handlePdfSubmit = async (values: any) => {
    try {
      setLoading(true);
      setError(null);
      
      if (!values.file || values.file.fileList.length === 0) {
        message.error('请选择PDF文件');
        setLoading(false);
        return;
      }
      
      const formData = new FormData();
      formData.append('import_type', 'pdf');
      formData.append('file', values.file.fileList[0].originFileObj);
      formData.append('source', values.source || 'user_pdf');
      if (values.commodities) {
        values.commodities.forEach((c: string) => {
          formData.append('commodities', c);
        });
      }
      
      const response = await axios.post('/api/v1/news/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setResult(response.data);
      message.success('PDF导入成功');
    } catch (err: any) {
      console.error('PDF导入失败:', err);
      setError(err.response?.data?.detail || '导入失败');
      message.error('导入失败');
    } finally {
      setLoading(false);
    }
  };

  const renderResult = () => {
    if (!result) return null;
    
    return (
      <Result
        status="success"
        title="导入成功"
        subTitle={`新闻ID: ${result.news_id}`}
        extra={[
          <Button type="primary" key="view">
            查看分析结果
          </Button>,
          <Button key="again" onClick={() => { setResult(null); form.resetFields(); }}>
            继续导入
          </Button>
        ]}
      />
    );
  };

  return (
    <div>
      <h2>导入新闻内容</h2>
      <p>支持导入URL、文本或PDF文件，系统将自动进行NLP分析和量化评分</p>
      
      <Divider />
      
      {error && (
        <Alert
          message="导入失败"
          description={error}
          type="error"
          closable
          style={{ marginBottom: 24 }}
        />
      )}
      
      {result ? (
        renderResult()
      ) : (
        <Card>
          <Tabs activeKey={activeTab} onChange={setActiveTab}>
            <TabPane 
              tab={<span><LinkOutlined /> URL导入</span>} 
              key="url"
            >
              <Form
                form={form}
                onFinish={handleUrlSubmit}
                layout="vertical"
              >
                <Form.Item
                  name="url"
                  label="新闻URL"
                  rules={[
                    { required: true, message: '请输入URL' },
                    { type: 'url', message: '请输入有效的URL' }
                  ]}
                >
                  <Input placeholder="https://example.com/news/123" />
                </Form.Item>
                
                <Form.Item
                  name="commodities"
                  label="关联品种"
                >
                  <Select
                    mode="multiple"
                    placeholder="选择关联品种"
                    allowClear
                  >
                    {commodities.map(c => (
                      <Option key={c} value={c}>{c}</Option>
                    ))}
                  </Select>
                </Form.Item>
                
                <Form.Item
                  name="source"
                  label="来源标识"
                >
                  <Input placeholder="用户自定义来源" />
                </Form.Item>
                
                <Form.Item>
                  <Button 
                    type="primary" 
                    htmlType="submit"
                    icon={<LinkOutlined />}
                    loading={loading}
                  >
                    导入URL
                  </Button>
                </Form.Item>
              </Form>
            </TabPane>
            
            <TabPane 
              tab={<span><FileTextOutlined /> 文本导入</span>} 
              key="text"
            >
              <Form
                form={form}
                onFinish={handleTextSubmit}
                layout="vertical"
              >
                <Form.Item
                  name="text"
                  label="新闻内容"
                  rules={[{ required: true, message: '请输入新闻内容' }]}
                >
                  <TextArea 
                    rows={10} 
                    placeholder="粘贴新闻内容..."
                  />
                </Form.Item>
                
                <Form.Item
                  name="commodities"
                  label="关联品种"
                >
                  <Select
                    mode="multiple"
                    placeholder="选择关联品种"
                    allowClear
                  >
                    {commodities.map(c => (
                      <Option key={c} value={c}>{c}</Option>
                    ))}
                  </Select>
                </Form.Item>
                
                <Form.Item
                  name="source"
                  label="来源标识"
                >
                  <Input placeholder="用户自定义来源" />
                </Form.Item>
                
                <Form.Item>
                  <Button 
                    type="primary" 
                    htmlType="submit"
                    icon={<FileTextOutlined />}
                    loading={loading}
                  >
                    导入文本
                  </Button>
                </Form.Item>
              </Form>
            </TabPane>
            
            <TabPane 
              tab={<span><FilePdfOutlined /> PDF导入</span>} 
              key="pdf"
            >
              <Form
                form={form}
                onFinish={handlePdfSubmit}
                layout="vertical"
              >
                <Form.Item
                  name="file"
                  label="PDF文件"
                  rules={[{ required: true, message: '请选择PDF文件' }]}
                >
                  <Upload
                    accept=".pdf"
                    maxCount={1}
                    beforeUpload={() => false}
                  >
                    <Button icon={<UploadOutlined />}>
                      选择PDF文件
                    </Button>
                  </Upload>
                </Form.Item>
                
                <Form.Item
                  name="commodities"
                  label="关联品种"
                >
                  <Select
                    mode="multiple"
                    placeholder="选择关联品种"
                    allowClear
                  >
                    {commodities.map(c => (
                      <Option key={c} value={c}>{c}</Option>
                    ))}
                  </Select>
                </Form.Item>
                
                <Form.Item
                  name="source"
                  label="来源标识"
                >
                  <Input placeholder="用户自定义来源" />
                </Form.Item>
                
                <Form.Item>
                  <Button 
                    type="primary" 
                    htmlType="submit"
                    icon={<FilePdfOutlined />}
                    loading={loading}
                  >
                    导入PDF
                  </Button>
                </Form.Item>
              </Form>
            </TabPane>
          </Tabs>
        </Card>
      )}
      
      <Card style={{ marginTop: 24 }} title="导入说明">
        <ul>
          <li><strong>URL导入：</strong>输入新闻网页链接，系统将自动提取正文内容</li>
          <li><strong>文本导入：</strong>直接粘贴新闻文本内容</li>
          <li><strong>PDF导入：</strong>上传PDF文件，支持研报、公告等文档</li>
          <li>导入后系统将自动进行NLP分析，包括实体识别、情感分析、事件提取等</li>
          <li>分析结果将用于更新品种评分和生成交易信号</li>
        </ul>
      </Card>
    </div>
  );
};

export default NewsImport;
