import { useState } from 'react';
import { Button, Radio, Input, Typography, Card, Divider, Space } from 'antd';
import type { QuizQuestion } from '@/types/learning';

const { TextArea } = Input;
const { Title, Text } = Typography;

interface Props {
  questions: QuizQuestion[];
  onSubmit: (answers: { q_number: number; answer: string }[]) => Promise<void>;
  onCancel: () => void;
  loading: boolean;
}

export default function QuizForm({ questions, onSubmit, onCancel, loading }: Props) {
  const [answers, setAnswers] = useState<Record<number, string>>({});

  const handleSubmit = () => {
    const ansList = questions.map((q) => ({
      q_number: q.q_number,
      answer: answers[q.q_number] || '',
    }));
    onSubmit(ansList);
  };

  const choices = questions.filter((q) => q.question_type === 'choice');
  const essays = questions.filter((q) => q.question_type === 'essay');
  const definitions = questions.filter((q) => q.question_type === 'definition');

  const answeredCount = Object.keys(answers).filter((k) => answers[Number(k)]?.trim()).length;

  return (
    <div>
      <div className="flex justify-between items-center mb-4 sticky top-0 bg-white py-2 z-10 border-b">
        <Text>
          共 {questions.length} 题 · 已答 {answeredCount} 题
        </Text>
        <Space>
          <Button onClick={onCancel}>取消</Button>
          <Button type="primary" onClick={handleSubmit} loading={loading}>
            提交评分
          </Button>
        </Space>
      </div>

      {/* Multiple choice */}
      {choices.length > 0 && (
        <div className="mb-6">
          <Title level={5}>一、选择题 ({choices.length} 题)</Title>
          {choices.map((q) => (
            <Card key={q.q_number} size="small" className="mb-3">
              <Text strong>{q.q_number}. {q.question_text}</Text>
              <div className="mt-2">
                <Radio.Group
                  onChange={(e) => setAnswers((prev) => ({ ...prev, [q.q_number]: e.target.value }))}
                  value={answers[q.q_number]}
                >
                  <div className="flex flex-col gap-1">
                    {(q.options || []).map((opt, i) => (
                      <Radio key={i} value={String.fromCharCode(65 + i)}>
                        {opt}
                      </Radio>
                    ))}
                  </div>
                </Radio.Group>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Essay questions */}
      {essays.length > 0 && (
        <div className="mb-6">
          <Title level={5}>二、大题 ({essays.length} 题)</Title>
          {essays.map((q) => (
            <Card key={q.q_number} size="small" className="mb-3">
              <Text strong>{q.q_number}. {q.question_text}</Text>
              <TextArea
                rows={5}
                className="mt-2"
                placeholder="请输入你的答案..."
                value={answers[q.q_number] || ''}
                onChange={(e) => setAnswers((prev) => ({ ...prev, [q.q_number]: e.target.value }))}
              />
            </Card>
          ))}
        </div>
      )}

      {/* Term definitions */}
      {definitions.length > 0 && (
        <div className="mb-6">
          <Title level={5}>三、名词解释 ({definitions.length} 题)</Title>
          {definitions.map((q) => (
            <Card key={q.q_number} size="small" className="mb-3">
              <Text strong>{q.q_number}. {q.question_text}</Text>
              <TextArea
                rows={3}
                className="mt-2"
                placeholder="请输入你的解释..."
                value={answers[q.q_number] || ''}
                onChange={(e) => setAnswers((prev) => ({ ...prev, [q.q_number]: e.target.value }))}
              />
            </Card>
          ))}
        </div>
      )}

      <Divider />
      <div className="text-center pb-4">
        <Button
          type="primary"
          size="large"
          onClick={handleSubmit}
          loading={loading}
          disabled={answeredCount < questions.length}
        >
          提交评分 ({answeredCount}/{questions.length})
        </Button>
      </div>
    </div>
  );
}
