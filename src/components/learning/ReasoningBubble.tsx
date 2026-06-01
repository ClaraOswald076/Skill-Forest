import { useState } from 'react';
import { Collapse } from 'antd';
import { BulbOutlined } from '@ant-design/icons';

interface Props {
  content: string;
}

export default function ReasoningBubble({ content }: Props) {
  const [open, setOpen] = useState(false);

  if (!content) return null;

  return (
    <div className="mb-2">
      <div
        className="flex items-center gap-1 text-xs text-gray-400 cursor-pointer hover:text-gray-600 mb-1"
        onClick={() => setOpen(!open)}
      >
        <BulbOutlined />
        <span>{open ? '收起思考过程' : '展开思考过程'}</span>
      </div>
      {open && (
        <div className="bg-gray-100 border border-gray-200 rounded-lg p-3 text-sm text-gray-600 whitespace-pre-wrap max-h-64 overflow-auto">
          {content}
        </div>
      )}
    </div>
  );
}
