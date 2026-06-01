import { Card, List, Tag, Button, Space, Typography } from 'antd';
import type { MergeSuggestion } from '@/types/analysis';

const { Text } = Typography;

interface Props {
  suggestions: MergeSuggestion[];
  decisions: Record<string, 'merge' | 'keep_separate'>;
  onDecisionChange: (skillName: string, decision: 'merge' | 'keep_separate') => void;
}

export default function MergePreview({ suggestions, decisions, onDecisionChange }: Props) {
  if (suggestions.length === 0) return null;

  return (
    <Card
      title={`发现 ${suggestions.length} 个可能重复的技能`}
      size="small"
      className="mb-4 bg-yellow-50 border-yellow-200"
    >
      <Text type="secondary" className="text-sm mb-2 block">
        以下技能与已有技能高度相似，请确认是否合并：
      </Text>
      <List
        dataSource={suggestions}
        renderItem={(s) => {
          const decision = decisions[s.new_skill_name] || s.action;
          return (
            <List.Item
              actions={[
                <Button
                  key="merge"
                  type={decision === 'merge' ? 'primary' : 'default'}
                  size="small"
                  onClick={() => onDecisionChange(s.new_skill_name, 'merge')}
                >
                  合并
                </Button>,
                <Button
                  key="keep"
                  type={decision === 'keep_separate' ? 'primary' : 'default'}
                  size="small"
                  onClick={() => onDecisionChange(s.new_skill_name, 'keep_separate')}
                >
                  保留独立
                </Button>,
              ]}
            >
              <div>
                <Text>
                  「{s.new_skill_name}」与已有技能「
                  {s.existing_skill_name}」
                </Text>
                <Tag color="orange" className="ml-2">
                  相似度 {Math.round(s.similarity * 100)}%
                </Tag>
              </div>
            </List.Item>
          );
        }}
      />
    </Card>
  );
}
