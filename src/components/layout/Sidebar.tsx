import { useNavigate, useLocation } from 'react-router-dom';
import { Menu } from 'antd';
import {
  DashboardOutlined,
  ApartmentOutlined,
  FileTextOutlined,
  CheckSquareOutlined,
  EditOutlined,
} from '@ant-design/icons';

const menuItems = [
  { key: '/', icon: <DashboardOutlined />, label: '仪表盘' },
  { key: '/skills', icon: <ApartmentOutlined />, label: '技能树' },
  { key: '/jobs', icon: <FileTextOutlined />, label: '岗位' },
  { key: '/todos', icon: <CheckSquareOutlined />, label: '工作任务' },
  { key: '/learn/errors', icon: <EditOutlined />, label: '错题本' },
];

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <div className="h-full flex flex-col">
      <div className="h-16 flex items-center justify-center border-b border-gray-200">
        <h1 className="text-lg font-bold text-blue-600 m-0">技能树管理</h1>
      </div>
      <Menu
        mode="inline"
        selectedKeys={[location.pathname]}
        items={menuItems}
        onClick={({ key }) => navigate(key)}
        className="flex-1 border-r-0 pt-2"
      />
    </div>
  );
}
