import { useLearningStore } from '@/store';
import { Button, Spin, message } from 'antd';
import QuizForm from './QuizForm';
import QuizResult from './QuizResult';

interface Props {
  todoId: number;
}

export default function QuizTab({ todoId }: Props) {
  const {
    currentQuestions, currentAttemptId, gradingResult,
    quizLoading, grading, generateQuiz, submitQuiz, clearQuiz,
  } = useLearningStore();

  const handleGenerate = async () => {
    try {
      await generateQuiz(todoId);
    } catch {
      message.error('生成测评失败，请检查后端服务后重试');
    }
  };

  const handleSubmit = async (answers: { q_number: number; answer: string }[]) => {
    if (!currentAttemptId) return;
    try {
      await submitQuiz(currentAttemptId, answers);
    } catch {
      message.error('提交答卷失败，答案未保存，请重试');
    }
  };

  // Show results after grading
  if (gradingResult) {
    return <QuizResult result={gradingResult} onRetry={() => clearQuiz()} />;
  }

  // Show quiz form
  if (currentQuestions && currentAttemptId) {
    return (
      <QuizForm
        questions={currentQuestions}
        onSubmit={handleSubmit}
        loading={grading}
        onCancel={() => clearQuiz()}
      />
    );
  }

  // Show loading or start button
  return (
    <div className="text-center py-12">
      {quizLoading ? (
        <Spin size="large" tip="AI 正在生成测评题目..." />
      ) : (
        <>
          <p className="text-gray-500 mb-4">
            还没有生成测评。AI 将根据你的学习任务生成一套包含选择题、大题和名词解释的完整测试。
          </p>
          <Button type="primary" size="large" onClick={handleGenerate}>
            📝 生成测评题目
          </Button>
        </>
      )}
    </div>
  );
}
