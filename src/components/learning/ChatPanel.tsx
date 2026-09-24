import { useRef, useEffect } from 'react';
import { Switch, Typography, Spin, message } from 'antd';
import { useLearningStore } from '@/store';
import ReasoningBubble from './ReasoningBubble';
import ChatInput from './ChatInput';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const { Text } = Typography;

export default function ChatPanel() {
  const { activeSession, sendingMessage, sendMessage, loadSession, toggleDeepThinking } = useLearningStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeSession?.messages]);

  if (!activeSession) return null;

  const handleSend = async (text: string) => {
    try {
      await sendMessage(activeSession.id, text);
    } catch {
      // 失败时用户的发言已入库，重新拉取会话让界面和真实历史一致
      message.error('消息发送失败，请重试');
      loadSession(activeSession.id);
    }
  };

  return (
    <>
      {/* Header with deep thinking toggle */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-200 bg-white">
        <Text strong className="text-sm">{activeSession.title}</Text>
        <div className="flex items-center gap-2">
          <Text className="text-xs text-gray-400">深度思考</Text>
          <Switch
            size="small"
            checked={activeSession.deep_thinking}
            onChange={(val) => toggleDeepThinking(activeSession.id, val)}
          />
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-auto px-4 py-4 bg-gray-50">
        {activeSession.messages.length === 0 && (
          <div className="text-center text-gray-400 mt-8">
            <p>👋 开始对话吧！有任何关于学习内容的问题都可以问我。</p>
          </div>
        )}
        {activeSession.messages.map((msg) => (
          <div
            key={msg.id}
            className={`mb-4 flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-3 ${
                msg.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-white border border-gray-200'
              }`}
            >
              {msg.role === 'assistant' && msg.reasoning_content && (
                <ReasoningBubble content={msg.reasoning_content} />
              )}
              {msg.role === 'user' ? (
                <div className="whitespace-pre-wrap text-sm">{msg.content}</div>
              ) : (
                <div className="prose prose-sm max-w-none text-sm">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {msg.content}
                  </ReactMarkdown>
                </div>
              )}
            </div>
          </div>
        ))}
        {sendingMessage && (
          <div className="flex justify-start mb-4">
            <div className="bg-white border border-gray-200 rounded-lg px-4 py-3">
              <Spin size="small" /> <Text className="text-gray-400 ml-2">思考中...</Text>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatInput onSend={handleSend} disabled={sendingMessage} />
    </>
  );
}
