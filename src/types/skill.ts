export type ProficiencyLevel = '认识' | '熟悉' | '熟练' | '完全掌握';
export type SkillStatus = 'not_started' | 'in_progress' | 'completed';

export interface Skill {
  id: number;
  name: string;
  description: string;
  category_l1: string;
  category_l2: string;
  category_l3: string;
  proficiency: ProficiencyLevel;
  status: SkillStatus;
  source_job_ids: number[];
  created_at: string | null;
  updated_at: string | null;
}

export interface SkillTreeNode {
  key: string;
  title: string;
  type: 'l1' | 'l2' | 'l3' | 'skill';
  skill?: Skill;
  children: SkillTreeNode[];
}

export interface SkillTreeResponse {
  tree: SkillTreeNode[];
}
