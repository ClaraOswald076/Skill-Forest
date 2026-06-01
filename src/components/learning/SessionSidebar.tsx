import { Button, List, Typography, Popconfirm } from 'antd';
import { PlusOutlined, DeleteOutlined, MessageOutlined } from '@ant-design/icons';
import { useLearningStore } from '@/store';

const { Text } = Typography;

interface Props {
  todoId: number;
  todoDescription: string;
}

export default function SessionSidebar({ todoId, todoDescription }: Props) {
  const { sessions, activeSession, createSession, loadSession, deleteSession } = useLearningStore();

  const handleNew = async () => {
    const id = await createSession(todoId, `学习: ${todoDescription.slice(0, 30)}`);
    await loadSession(id);
  };

  return (
    <div className="h-full flex flex-col">
      <div className="p-2 border-b border-gray-200">
        <Button type="primary" block icon={<PlusOutlined />} onClick={handleNew} size="small">
          新对话
        </Button>
      </div>
      <div className="flex-1 overflow-auto">
        <List
          dataSource={sessions}
          renderItem={(s) => (
            <List.Item
              className={`cursor-pointer px-3 py-2 hover:bg-gray-100 transition-colors ${
                activeSession?.id === s.id ? 'bg-blue-50 border-l-2 border-l-blue-500' : ''
              }`}
              onClick={() => loadSession(s.id)}
              actions={[
                <Popconfirm
                  key="del"
                  title="删除此对话？"
                  onConfirm={(e) => {
                    e?.stopPropagation();
                    deleteSession(s.id);
                  }}
                  onCancel={(e) => e?.stopPropagation()}
                >
                  <Button
                    type="text"
                    size="small"
                    danger
                    icon={<DeleteOutlined />}
                    onClick={(e) => e.stopPropagation()}
                  />
                </Popconfirm>,
              ]}
            >
              <div className="w-full overflow-hidden">
                <Text ellipsis className="text-sm block">
                  <MessageOutlined className="mr-1 text-xs" />
                  {s.title}
                </Text>
                <Text type="secondary" className="text-xs">
                  {s.message_count} 条消息
                </Text>
              </div>
            </List.Item>
          )}
          locale={{ emptyText: '暂无对话' }}
        />
      </div>
    </div>
  );
}
