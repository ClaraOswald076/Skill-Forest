import { Card, Descriptions, Button, Space, message } from 'antd';
import type { Skill } from '@/types/skill';
import ProficiencySelector from './ProficiencySelector';
import ProficiencyBadge from './ProficiencyBadge';
import { useSkillStore } from '@/store';

interface Props {
  skill: Skill;
}

export default function SkillDetailPanel({ skill }: Props) {
  const { updateSkill } = useSkillStore();

  const handleProficiencyChange = async (level: string) => {
    try {
      await updateSkill(skill.id, { proficiency: level });
      message.success('掌握程度已更新');
    } catch {
      message.error('更新失败');
    }
  };

  const handleStatusChange = async (status: string) => {
    try {
      await updateSkill(skill.id, { status });
      message.success('状态已更新');
    } catch {
      message.error('更新失败');
    }
  };

  return (
    <Card title={skill.name} className="h-full">
      <Descriptions column={1} bordered size="small">
        <Descriptions.Item label="分类路径">
          {skill.category_l1} &gt; {skill.category_l2}
          {skill.category_l3 ? ` > ${skill.category_l3}` : ''}
        </Descriptions.Item>
        <Descriptions.Item label="描述">
          {skill.description || '暂无描述'}
        </Descriptions.Item>
        <Descriptions.Item label="我的掌握程度">
          <ProficiencySelector
            value={skill.proficiency}
            onChange={handleProficiencyChange}
          />
        </Descriptions.Item>
        <Descriptions.Item label="学习状态">
          <Space>
            {(['not_started', 'in_progress', 'completed'] as const).map((s) => (
              <Button
                key={s}
                type={skill.status === s ? 'primary' : 'default'}
                size="small"
                onClick={() => handleStatusChange(s)}
              >
                {{ not_started: '未开始', in_progress: '进行中', completed: '已完成' }[s]}
              </Button>
            ))}
          </Space>
        </Descriptions.Item>
        <Descriptions.Item label="来源岗位">
          {skill.source_job_ids.length > 0
            ? `${skill.source_job_ids.length} 个岗位要求此技能`
            : '无关联岗位'}
        </Descriptions.Item>
      </Descriptions>
    </Card>
  );
}
