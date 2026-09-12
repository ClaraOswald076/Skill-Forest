import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Table, Button, Typography, Space, Popconfirm, Tag, Alert } from 'antd';
import { PlusOutlined, EyeOutlined, DeleteOutlined } from '@ant-design/icons';
import { useJobStore, useUIStore } from '@/store';
import type { Job } from '@/types/job';
import JobInputModal from './JobInputModal';
import LoadingOverlay from '@/components/common/LoadingOverlay';
import EmptyState from '@/components/common/EmptyState';

const { Title } = Typography;

export default function JobListPage() {
  const navigate = useNavigate();
  const { jobs, loading, error, fetchJobs, deleteJob } = useJobStore();
  const { openJobInput } = useUIStore();

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  const columns = [
    {
      title: '岗位名称',
      dataIndex: 'title',
      key: 'title',
      render: (text: string, record: Job) => (
        <a onClick={() => navigate(`/jobs/${record.id}`)}>{text || '未命名岗位'}</a>
      ),
    },
    {
      title: '公司',
      dataIndex: 'company',
      key: 'company',
      render: (text: string) => text || '-',
    },
    {
      title: '技能数',
      dataIndex: 'skill_count',
      key: 'skill_count',
      render: (count: number) => <Tag color="blue">{count}</Tag>,
    },
    {
      title: '任务数',
      dataIndex: 'todo_count',
      key: 'todo_count',
      render: (count: number) => <Tag color="green">{count}</Tag>,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text: string) => text?.slice(0, 10) || '-',
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: unknown, record: Job) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/jobs/${record.id}`)}
          >
            查看
          </Button>
          <Popconfirm
            title="确定删除此岗位？"
            description="相关的任务也会被删除"
            onConfirm={() => deleteJob(record.id)}
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <Title level={3} className="mb-0">💼 岗位列表</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={openJobInput}>
          新岗位
        </Button>
      </div>

      {error ? (
        <Alert type="error" showIcon message="岗位列表加载失败" description={error} />
      ) : loading ? (
        <LoadingOverlay />
      ) : jobs.length === 0 ? (
        <EmptyState
          description="还没有添加任何岗位"
          actionText="添加第一个岗位"
          onAction={openJobInput}
        />
      ) : (
        <Table
          dataSource={jobs}
          columns={columns}
          rowKey="id"
          className="bg-white rounded-lg"
          pagination={{ pageSize: 10 }}
        />
      )}

      <JobInputModal />
    </div>
  );
}
