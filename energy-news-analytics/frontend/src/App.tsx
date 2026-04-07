import React, { useState, useEffect } from 'react';
import { Layout, Menu, theme, ConfigProvider } from 'antd';
import {
  DashboardOutlined,
  BarChartOutlined,
  FileTextOutlined,
  BellOutlined,
  SettingOutlined,
  ImportOutlined
} from '@ant-design/icons';
import Dashboard from './components/Dashboard';
import Analysis from './components/Analysis';
import NewsImport from './components/NewsImport';
import Alerts from './components/Alerts';
import Settings from './components/Settings';
import './App.css';

const { Header, Content, Sider } = Layout;

type MenuKey = 'dashboard' | 'analysis' | 'import' | 'alerts' | 'settings';

function App() {
  const [collapsed, setCollapsed] = useState(false);
  const [selectedKey, setSelectedKey] = useState<MenuKey>('dashboard');
  const {
    token: { colorBgContainer },
  } = theme.useToken();

  const menuItems = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: '仪表盘',
    },
    {
      key: 'analysis',
      icon: <BarChartOutlined />,
      label: '品种分析',
    },
    {
      key: 'import',
      icon: <ImportOutlined />,
      label: '导入新闻',
    },
    {
      key: 'alerts',
      icon: <BellOutlined />,
      label: '预警中心',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '系统设置',
    },
  ];

  const renderContent = () => {
    switch (selectedKey) {
      case 'dashboard':
        return <Dashboard />;
      case 'analysis':
        return <Analysis />;
      case 'import':
        return <NewsImport />;
      case 'alerts':
        return <Alerts />;
      case 'settings':
        return <Settings />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#1890ff',
          borderRadius: 6,
        },
      }}
    >
      <Layout style={{ minHeight: '100vh' }}>
        <Sider
          trigger={null}
          collapsible
          collapsed={collapsed}
          theme="dark"
          style={{
            overflow: 'auto',
            height: '100vh',
            position: 'fixed',
            left: 0,
            top: 0,
            bottom: 0,
          }}
        >
          <div className="logo">
            <h3 style={{ color: 'white', textAlign: 'center', padding: '16px 0', margin: 0 }}>
              {collapsed ? '能源' : '能源化工分析'}
            </h3>
          </div>
          <Menu
            theme="dark"
            mode="inline"
            selectedKeys={[selectedKey]}
            items={menuItems}
            onClick={({ key }) => setSelectedKey(key as MenuKey)}
          />
        </Sider>
        <Layout style={{ marginLeft: collapsed ? 80 : 200, transition: 'all 0.2s' }}>
          <Header style={{ padding: 0, background: colorBgContainer }}>
            <div style={{ padding: '0 24px', fontSize: '20px', fontWeight: 'bold' }}>
              能源化工新闻分析系统
            </div>
          </Header>
          <Content
            style={{
              margin: '24px 16px',
              padding: 24,
              minHeight: 280,
              background: colorBgContainer,
              borderRadius: 8,
            }}
          >
            {renderContent()}
          </Content>
        </Layout>
      </Layout>
    </ConfigProvider>
  );
}

export default App;
