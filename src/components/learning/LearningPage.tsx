import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Typography, Tabs, Tag, Button, Space, Descriptions } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { useTodoStore, useLearningStore } from '@/store';
import { api } from '@/services/apiClient';
import type { TodoItem } from '@/types/todo';
import TutorialTab from './TutorialTab';
import ChatTab from './ChatTab';
import QuizTab from './QuizTab';
import LoadingOverlay from '@/components/common/LoadingOverlay';

const { Title } = Typography;

export default function LearningPage() {
  const { todoId } = useParams<{ todoId: string }>();
  const navigate = useNavigate();
  const { todos, fetchTodos } = useTodoStore();
  const { loadTutorial, resetForTodo } = useLearningStore();
  const [todo, setTodo] = useState<TodoItem | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      setLoading(true);
      // 任务切换时先清掉上一个任务的会话/测评状态，避免串数据
      resetForTodo();
      // Try to get todo from store, or fetch directly
      const existing = todos.find((t) => t.id === Number(todoId));
      if (existing) {
        setTodo(existing);
      } else {
        // Fetch single todo via the getTodo endpoint isn't available, try loading all
        await fetchTodos();
        const found = useTodoStore.getState().todos.find((t) => t.id === Number(todoId));
        if (found) setTodo(found);
      }
      // Auto-load tutorial
      if (todoId) {
        try {
          await loadTutorial(Number(todoId));
        } catch {
          // Will try to generate on first access
        }
      }
      setLoading(false);
    })();
  }, [todoId]);

  if (loading) return <LoadingOverlay tip="加载学习页面..." />;
  if (!todo) return <div className="text-center py-12 text-gray-400">任务不存在</div>;

  const tabItems = [
    {
      key: 'tutorial',
      label: '📖 教程',
      children: <TutorialTab todoId={Number(todoId)} />,
    },
    {
      key: 'chat',
      label: '💬 对话',
      children: <ChatTab todoId={Number(todoId)} todo={todo} />,
    },
    {
      key: 'quiz',
      label: '📝 测评',
      children: <QuizTab todoId={Number(todoId)} />,
    },
  ];

  return (
    <div>
      <Button
        icon={<ArrowLeftOutlined />}
        onClick={() => navigate('/todos')}
        className="mb-4"
      >
        返回任务列表
      </Button>

      {/* Todo info header */}
      <div className="bg-white rounded-lg p-4 mb-4 border border-gray-200">
        <Title level={4} className="mb-2">{todo.description}</Title>
        <Space wrap>
          <Tag color="blue">
            {{ pending: '待办', in_progress: '进行中', completed: '已完成' }[todo.status] || todo.status}
          </Tag>
          <Tag color="green">要求程度: {todo.proficiency_required}</Tag>
          {todo.skill_names?.map((s) => (
            <Tag key={s}>{s}</Tag>
          ))}
        </Space>
      </div>

      <Tabs defaultActiveKey="tutorial" items={tabItems} className="bg-white rounded-lg p-4 border border-gray-200" />
    </div>
  );
}
