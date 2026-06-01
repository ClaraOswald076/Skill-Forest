import { Tree } from 'antd';
import type { SkillTreeNode, Skill } from '@/types/skill';
import ProficiencyBadge from './ProficiencyBadge';

interface Props {
  tree: SkillTreeNode[];
  onSelectSkill: (skill: Skill) => void;
}

export default function SkillTree({ tree, onSelectSkill }: Props) {
  return (
    <Tree
      treeData={tree}
      defaultExpandAll
      blockNode
      titleRender={(node) => {
        const n = node as unknown as SkillTreeNode;
        if (n.type === 'skill' && n.skill) {
          return (
            <span
              className="cursor-pointer hover:text-blue-600"
              onClick={() => onSelectSkill(n.skill!)}
            >
              {n.title}
              <ProficiencyBadge level={n.skill.proficiency} />
            </span>
          );
        }
        return <span className="font-medium text-gray-700">{n.title}</span>;
      }}
      className="bg-transparent"
    />
  );
}
