import { Select } from 'antd';
import type { ProficiencyLevel } from '@/types/skill';

const OPTIONS: { value: ProficiencyLevel; label: string }[] = [
  { value: '认识', label: '认识 — 基本了解' },
  { value: '熟悉', label: '熟悉 — 能独立使用' },
  { value: '熟练', label: '熟练 — 能指导他人' },
  { value: '完全掌握', label: '完全掌握 — 专家级' },
];

interface Props {
  value: ProficiencyLevel;
  onChange: (level: ProficiencyLevel) => void;
  disabled?: boolean;
}

export default function ProficiencySelector({ value, onChange, disabled }: Props) {
  return (
    <Select
      value={value}
      onChange={onChange}
      options={OPTIONS}
      disabled={disabled}
      style={{ width: 200 }}
    />
  );
}
