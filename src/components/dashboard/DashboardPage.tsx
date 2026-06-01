import { Card, Row, Col, Progress, Statistic, List, Tag, Typography } from 'antd';
import {
  TrophyOutlined,
  BookOutlined,
  CheckCircleOutlined,
  RiseOutlined,
} from '@ant-design/icons';
import { useDashboard } from '@/hooks/useDashboard';
import LoadingOverlay from '@/components/common/LoadingOverlay';
import EmptyState from '@/components/common/EmptyState';

const { Title, Text } = Typography;

const PROFICIENCY_COLORS: Record<string, string> = {
  '认识': '#default',
  '熟悉': 'blue',
  '熟练': 'green',
  '完全掌握': 'gold',
};

export default function DashboardPage() {
  const { stats, loading, refresh } = useDashboard();

  if (loading) return <LoadingOverlay tip="加载仪表盘..." />;
  if (!stats) return <EmptyState description="无法加载仪表盘" />;

  return (
    <div>
      <Title level={3} className="mb-6">📊 学习仪表盘</Title>

      {/* Top stats */}
      <Row gutter={[16, 16]} className="mb-6">
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="总技能数"
              value={stats.total_skills}
              prefix={<BookOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="已完成"
              value={stats.completed_skills}
              suffix={`/ ${stats.total_skills}`}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="岗位数"
              value={stats.total_jobs}
              prefix={<TrophyOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="待办任务"
              value={stats.total_todos - stats.completed_todos}
              suffix={`/ ${stats.total_todos}`}
              prefix={<RiseOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* Overall progress */}
        <Col xs={24} md={12}>
          <Card title="总体完成度">
            {stats.total_skills > 0 ? (
              <div className="text-center py-4">
                <Progress
                  type="circle"
                  percent={Math.round(stats.overall_completion_rate * 100)}
                  size={160}
                />
                <p className="mt-4 text-gray-500">{stats.recent_activity}</p>
              </div>
            ) : (
              <EmptyState description="还没有技能数据，请先添加岗位" />
            )}
          </Card>
        </Col>

        {/* Best matching job */}
        <Col xs={24} md={12}>
          <Card title="最佳匹配岗位">
            {stats.best_matching_job ? (
              <div className="text-center py-4">
                <Title level={4}>{stats.best_matching_job.job_title}</Title>
                <Text type="secondary">{stats.best_matching_job.company}</Text>
                <div className="mt-4">
                  <Progress
                    type="circle"
                    percent={Math.round(stats.best_matching_job.match_rate * 100)}
                    size={120}
                  />
                  <p className="mt-2 text-gray-500">
                    技能匹配：{stats.best_matching_job.completed_skills}/
                    {stats.best_matching_job.total_skills_required}
                  </p>
                </div>
              </div>
            ) : (
              <EmptyState description="暂无岗位数据" />
            )}
          </Card>
        </Col>

        {/* Domain completion */}
        <Col xs={24} md={12}>
          <Card title="各领域完成度">
            {stats.domains.length > 0 ? (
              <div className="space-y-3">
                {stats.domains.map((d) => (
                  <div key={d.category_l1}>
                    <div className="flex justify-between mb-1">
                      <Text>{d.category_l1}</Text>
                      <Text type="secondary">
                        {d.completed_skills}/{d.total_skills}
                      </Text>
                    </div>
                    <Progress
                      percent={Math.round(d.completion_rate * 100)}
                      size="small"
                    />
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState description="暂无分类数据" />
            )}
          </Card>
        </Col>

        {/* Deepest expertise */}
        <Col xs={24} md={12}>
          <Card title="最深入领域">
            {stats.deepest_expertise.length > 0 ? (
              <List
                dataSource={stats.deepest_expertise}
                renderItem={(item) => (
                  <List.Item>
                    <div className="w-full">
                      <div className="flex justify-between">
                        <Text strong>
                          {item.category_l1} / {item.category_l2}
                        </Text>
                        <Text type="secondary">
                          综合水平：{item.avg_proficiency_level.toFixed(1)}
                        </Text>
                      </div>
                      <div className="mt-1">
                        {item.top_skills.map((s) => (
                          <Tag key={s} className="mb-1">
                            {s}
                          </Tag>
                        ))}
                      </div>
                    </div>
                  </List.Item>
                )}
              />
            ) : (
              <EmptyState description="暂无深入领域数据" />
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
}
