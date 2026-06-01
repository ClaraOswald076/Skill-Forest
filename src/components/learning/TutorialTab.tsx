import { useLearningStore } from '@/store';
import { Button, Spin, message } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Props {
  todoId: number;
}

export default function TutorialTab({ todoId }: Props) {
  const { tutorial, tutorialLoading, loadTutorial, regenerateTutorial } = useLearningStore();

  const handleGenerate = async () => {
    try {
      await loadTutorial(todoId);
      message.success('教程已生成');
    } catch {
      message.error('生成失败，请重试');
    }
  };

  const handleRegenerate = async () => {
    try {
      await regenerateTutorial(todoId);
      message.success('教程已重新生成');
    } catch {
      message.error('重新生成失败');
    }
  };

  if (tutorialLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spin size="large" tip="AI 正在生成教程..." />
      </div>
    );
  }

  if (!tutorial) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 mb-4">还没有生成教程</p>
        <Button type="primary" onClick={handleGenerate}>
          🤖 AI 生成 0 基础教程
        </Button>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <span className="text-gray-400 text-sm">
          版本 {tutorial.tutorial_version} · 生成于 {tutorial.last_generated_at?.slice(0, 16) || ''}
        </span>
        <Button icon={<ReloadOutlined />} onClick={handleRegenerate} size="small">
          重新生成
        </Button>
      </div>
      <div className="prose max-w-none">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {tutorial.tutorial_content}
        </ReactMarkdown>
      </div>
    </div>
  );
}
