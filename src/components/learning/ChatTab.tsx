import { useEffect } from 'react';
import { useLearningStore } from '@/store';
import type { TodoItem } from '@/types/todo';
import SessionSidebar from './SessionSidebar';
import ChatPanel from './ChatPanel';

interface Props {
  todoId: number;
  todo: TodoItem;
}

export default function ChatTab({ todoId, todo }: Props) {
  const { loadSessions, activeSession } = useLearningStore();

  useEffect(() => {
    loadSessions(todoId);
  }, [todoId, loadSessions]);

  return (
    <div className="flex h-[70vh] gap-0 -m-4">
      {/* Session sidebar */}
      <div className="w-56 border-r border-gray-200 flex-shrink-0 bg-gray-50">
        <SessionSidebar todoId={todoId} todoDescription={todo.description} />
      </div>

      {/* Chat panel */}
      <div className="flex-1 flex flex-col">
        {activeSession ? (
          <ChatPanel />
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-400">
            <div className="text-center">
              <p className="text-4xl mb-4">💬</p>
              <p>选择或创建一个对话开始学习</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
