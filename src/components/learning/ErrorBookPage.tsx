import { useEffect, useState } from 'react';
import { Typography, Card, Tag, Checkbox, Select, Statistic, Row, Col, Button, Popconfirm } from 'antd';
import { DeleteOutlined } from '@ant-design/icons';
import { useLearningStore, useSkillStore } from '@/store';
import EmptyState from '@/components/common/EmptyState';

const { Title, Text } = Typography;

export default function ErrorBookPage() {
  const { errors, errorStats, loadErrors, loadErrorStats, markErrorReviewed, deleteError } =
    useLearningStore();
  const { skills, fetchSkills } = useSkillStore();
  const [skillFilter, setSkillFilter] = useState<number | undefined>(undefined);
  const [reviewedFilter, setReviewedFilter] = useState<boolean | undefined>(undefined);

  useEffect(() => {
    loadErrors({ skill_id: skillFilter, reviewed: reviewedFilter });
    loadErrorStats();
    fetchSkills();
  }, [skillFilter, reviewedFilter]);

  return (
    <div>
      <Title level={3} className="mb-6">📕 错题本</Title>

      {/* Stats */}
      {errorStats && (
        <Row gutter={16} className="mb-4">
          <Col span={8}>
            <Card size="small">
              <Statistic title="总错题" value={errorStats.total} />
            </Card>
          </Col>
          <Col span={8}>
            <Card size="small">
              <Statistic title="未复习" value={errorStats.unreviewed} valueStyle={{ color: '#cf1322' }} />
            </Card>
          </Col>
          <Col span={8}>
            <Card size="small">
              <Statistic title="已复习" value={errorStats.reviewed} valueStyle={{ color: '#3f8600' }} />
            </Card>
          </Col>
        </Row>
      )}

      {/* Filters */}
      <div className="flex gap-4 mb-4">
        <Select
          placeholder="按技能筛选"
          allowClear
          style={{ width: 200 }}
          value={skillFilter}
          onChange={setSkillFilter}
          options={skills.map((s) => ({ value: s.id, label: s.name }))}
        />
        <Select
          placeholder="复习状态"
          allowClear
          style={{ width: 140 }}
          value={reviewedFilter}
          onChange={setReviewedFilter}
          options={[
            { value: false as never, label: '未复习' },
            { value: true as never, label: '已复习' },
          ]}
        />
      </div>

      {/* Error list */}
      {errors.length === 0 ? (
        <EmptyState description="错题本为空" />
      ) : (
        <div>
          {errors.map((entry) => (
            <Card
              key={entry.id}
              size="small"
              className={`mb-3 ${entry.reviewed ? 'opacity-60' : ''}`}
              title={
                <div className="flex justify-between items-center">
                  <span>
                    <Tag color="orange">{entry.question_type === 'choice' ? '选择题' : entry.question_type === 'essay' ? '大题' : '名词解释'}</Tag>
                    {entry.question_text.slice(0, 80)}...
                  </span>
                  <Checkbox
                    checked={entry.reviewed}
                    onChange={(e) => markErrorReviewed(entry.id)}
                  >
                    已复习
                  </Checkbox>
                </div>
              }
              extra={
                <Popconfirm title="删除？" onConfirm={() => deleteError(entry.id)}>
                  <Button type="text" size="small" danger icon={<DeleteOutlined />} />
                </Popconfirm>
              }
            >
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <Text type="secondary">我的答案：</Text>
                  <div className="mt-1 p-2 bg-red-50 rounded text-red-700">{entry.user_answer || '（未作答）'}</div>
                </div>
                <div>
                  <Text type="secondary">正确答案：</Text>
                  <div className="mt-1 p-2 bg-green-50 rounded text-green-700">{entry.correct_answer}</div>
                </div>
              </div>
              {entry.explanation && (
                <div className="mt-2 p-2 bg-blue-50 rounded text-sm text-blue-700">
                  💡 {entry.explanation}
                </div>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
