import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Typography, Card, Descriptions, List, Tag, Button, Space } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { useJobStore } from '@/store';
import LoadingOverlay from '@/components/common/LoadingOverlay';
import ProficiencyBadge from '@/components/skills/ProficiencyBadge';

const { Title, Paragraph } = Typography;

export default function JobDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { selectedJob: job, loading, fetchJob } = useJobStore();

  useEffect(() => {
    if (id) fetchJob(Number(id));
  }, [id, fetchJob]);

  if (loading || !job) return <LoadingOverlay />;

  return (
    <div>
      <Button
        icon={<ArrowLeftOutlined />}
        onClick={() => navigate('/jobs')}
        className="mb-4"
      >
        返回岗位列表
      </Button>

      <Title level={3}>{job.title}</Title>
      {job.company && (
        <Tag color="purple" className="mb-4">
          {job.company}
        </Tag>
      )}
      {job.url && (
        <div className="mb-4">
          <a href={job.url} target="_blank" rel="noopener noreferrer" className="text-blue-500 underline text-sm">
            🔗 查看原始岗位链接
          </a>
        </div>
      )}

      <div className="flex gap-6">
        {/* Left column */}
        <div className="w-3/5">
          <Card title="原始 JD 文本" className="mb-4">
            <Paragraph className="whitespace-pre-wrap text-sm">
              {job.raw_text}
            </Paragraph>
          </Card>
        </div>

        {/* Right column */}
        <div className="w-2/5 space-y-4">
          <Card title={`技能要求 (${job.skills.length})`}>
            <List
              dataSource={job.skills}
              renderItem={(skill) => (
                <List.Item>
                  <div>
                    <span
                      className="cursor-pointer text-blue-600"
                      onClick={() => navigate('/skills')}
                    >
                      {skill.name}
                    </span>
                    <div className="text-xs text-gray-400 mt-1">
                      {skill.category_l1} &gt; {skill.category_l2}
                      {skill.category_l3 ? ` > ${skill.category_l3}` : ''}
                    </div>
                    <div className="mt-1">
                      <ProficiencyBadge level={skill.proficiency} />
                      <Tag className="ml-1">
                        {{ not_started: '未开始', in_progress: '进行中', completed: '已完成' }[
                          skill.status
                        ] || skill.status}
                      </Tag>
                    </div>
                  </div>
                </List.Item>
              )}
            />
          </Card>

          <Card title={`学习任务 (${job.todos.length})`}>
            <List
              dataSource={job.todos}
              renderItem={(todo) => (
                <List.Item>
                  <div>
                    <div>{todo.description}</div>
                    <div className="mt-1">
                      <Tag color={todo.status === 'completed' ? 'green' : 'orange'}>
                        {{ pending: '待办', in_progress: '进行中', completed: '已完成' }[
                          todo.status
                        ] || todo.status}
                      </Tag>
                      {todo.skill_names.map((s) => (
                        <Tag key={s} className="text-xs">
                          {s}
                        </Tag>
                      ))}
                    </div>
                  </div>
                </List.Item>
              )}
            />
          </Card>
        </div>
      </div>
    </div>
  );
}
