import { Tag } from 'antd';
import type { ProficiencyLevel } from '@/types/skill';

const COLOR_MAP: Record<ProficiencyLevel, string> = {
  '认识': 'default',
  '熟悉': 'blue',
  '熟练': 'green',
  '完全掌握': 'gold',
};

interface Props {
  level: ProficiencyLevel;
}

export default function ProficiencyBadge({ level }: Props) {
  return <Tag color={COLOR_MAP[level] || 'default'}>{level}</Tag>;
}
