import { Layout } from 'antd';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

const { Sider, Content } = Layout;

export default function AppLayout() {
  return (
    <Layout className="h-screen">
      <Sider
        width={220}
        theme="light"
        className="border-r border-gray-200"
        breakpoint="lg"
        collapsedWidth={60}
      >
        <Sidebar />
      </Sider>
      <Layout>
        <Content className="p-6 bg-gray-50 overflow-auto">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
