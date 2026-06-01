import { useNavigate } from 'react-router-dom';
import { Button, Card, Typography, Tag, Progress, Space, Divider } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined, RetweetOutlined, BookOutlined } from '@ant-design/icons';
import type { QuizSubmitResponse } from '@/types/learning';

const { Title, Text, Paragraph } = Typography;

interface Props {
  result: QuizSubmitResponse;
  onRetry: () => void;
}

export default function QuizResult({ result, onRetry }: Props) {
  const navigate = useNavigate();
  const pct = result.max_score > 0 ? Math.round((result.total_score / result.max_score) * 100) : 0;
  const wrongCount = result.results.filter((r) => !r.is_correct).length;

  return (
    <div>
      {/* Score summary */}
      <Card className="mb-6 text-center bg-gradient-to-b from-blue-50 to-white">
        <Title level={2}>
          {pct >= 80 ? '🎉' : pct >= 60 ? '👍' : '💪'} 得分: {result.total_score} / {result.max_score}
        </Title>
        <Progress
          type="circle"
          percent={pct}
          size={140}
          status={pct >= 60 ? 'success' : 'exception'}
        />
        <div className="mt-4">
          <Space>
            <Tag color="green" icon={<CheckCircleOutlined />}>
              正确 {result.results.filter((r) => r.is_correct).length} 题
            </Tag>
            <Tag color="red" icon={<CloseCircleOutlined />}>
              错误 {wrongCount} 题
            </Tag>
          </Space>
        </div>
        {result.overall_feedback && (
          <Paragraph className="mt-3 text-gray-600 italic">
            {result.overall_feedback}
          </Paragraph>
        )}
        <Space className="mt-4">
          <Button icon={<RetweetOutlined />} onClick={onRetry}>
            重新测评
          </Button>
          {wrongCount > 0 && (
            <Button type="primary" icon={<BookOutlined />} onClick={() => navigate('/learn/errors')}>
              查看错题本
            </Button>
          )}
        </Space>
      </Card>

      {/* Detailed results */}
      <div>
        <Title level={5}>详细结果</Title>
        {result.results.map((r) => (
          <Card
            key={r.q_number}
            size="small"
            className={`mb-2 border-l-4 ${
              r.is_correct ? 'border-l-green-500' : 'border-l-red-500'
            }`}
          >
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <Text strong>
                  {r.is_correct ? (
                    <CheckCircleOutlined className="text-green-500 mr-1" />
                  ) : (
                    <CloseCircleOutlined className="text-red-500 mr-1" />
                  )}
                  第 {r.q_number} 题
                </Text>
                <Tag className="ml-2">{r.score}/{r.max_score} 分</Tag>
                {r.explanation && (
                  <div className="mt-2 text-sm text-gray-600 bg-gray-50 p-2 rounded">
                    {r.explanation}
                  </div>
                )}
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
