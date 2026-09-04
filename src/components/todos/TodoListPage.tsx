import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Typography, Table, Tag, Checkbox, Select, Space, Button, Alert } from 'antd';
import { BookOutlined } from '@ant-design/icons';
import { useTodoStore, useJobStore } from '@/store';
import type { TodoItem } from '@/types/todo';
import ProficiencyBadge from '@/components/skills/ProficiencyBadge';
import LoadingOverlay from '@/components/common/LoadingOverlay';
import EmptyState from '@/components/common/EmptyState';

const { Title } = Typography;

const STATUS_OPTIONS = [
  { value: '', label: '全部状态' },
  { value: 'pending', label: '待办' },
  { value: 'in_progress', label: '进行中' },
  { value: 'completed', label: '已完成' },
];

export default function TodoListPage() {
  const navigate = useNavigate();
  const { todos, loading, error, filters, fetchTodos, setFilter, toggleTodoStatus } =
    useTodoStore();
  const { jobs, fetchJobs } = useJobStore();

  useEffect(() => {
    fetchTodos();
    fetchJobs();
  }, [fetchTodos, fetchJobs]);

  const columns = [
    {
      title: '',
      key: 'checkbox',
      width: 48,
      render: (_: unknown, record: TodoItem) => (
        <Checkbox
          checked={record.status === 'completed'}
          onChange={() => toggleTodoStatus(record.id)}
        />
      ),
    },
    {
      title: '任务描述',
      dataIndex: 'description',
      key: 'description',
      render: (text: string, record: TodoItem) => (
        <span className={record.status === 'completed' ? 'line-through text-gray-400' : ''}>
          {text}
        </span>
      ),
    },
    {
      title: '关联岗位',
      dataIndex: 'job_title',
      key: 'job_title',
      render: (text: string) => text || '-',
    },
    {
      title: '关联技能',
      dataIndex: 'skill_names',
      key: 'skills',
      render: (names: string[]) => (
        <Space wrap>
          {names.map((n) => (
            <Tag key={n}>{n}</Tag>
          ))}
        </Space>
      ),
    },
    {
      title: '要求程度',
      dataIndex: 'proficiency_required',
      key: 'proficiency_required',
      render: (level: string) => <ProficiencyBadge level={level as never} />,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'completed' ? 'green' : status === 'in_progress' ? 'blue' : 'default'}>
          {{ pending: '待办', in_progress: '进行中', completed: '已完成' }[status] || status}
        </Tag>
      ),
    },
    {
      title: '学习',
      key: 'learn',
      render: (_: unknown, record: TodoItem) => (
        <Button
          type="primary"
          size="small"
          icon={<BookOutlined />}
          onClick={() => navigate(`/learn/${record.id}`)}
        >
          开始学习
        </Button>
      ),
    },
  ];

  return (
    <div>
      <Title level={3} className="mb-6">✅ 工作任务</Title>

      {/* Filters */}
      <Space className="mb-4" wrap>
        <Select
          placeholder="筛选岗位"
          allowClear
          style={{ width: 200 }}
          value={filters.job_id}
          onChange={(val) => setFilter('job_id', val)}
          options={[
            { value: null as never, label: '全部岗位' },
            ...jobs.map((j) => ({ value: j.id as never, label: j.title || `岗位 #${j.id}` })),
          ]}
        />
        <Select
          placeholder="筛选状态"
          style={{ width: 120 }}
          value={filters.status || ''}
          onChange={(val) => setFilter('status', val || null)}
          options={STATUS_OPTIONS}
        />
      </Space>

      {error ? (
        <Alert type="error" showIcon message="任务列表加载失败" description={error} />
      ) : loading ? (
        <LoadingOverlay />
      ) : todos.length === 0 ? (
        <EmptyState description="暂无任务数据" />
      ) : (
        <Table
          dataSource={todos}
          columns={columns}
          rowKey="id"
          className="bg-white rounded-lg"
          pagination={{ pageSize: 15 }}
        />
      )}
    </div>
  );
}
