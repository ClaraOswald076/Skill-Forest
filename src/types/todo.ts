import type { ProficiencyLevel } from './skill';

export type TodoStatus = 'pending' | 'in_progress' | 'completed';

export interface TodoItem {
  id: number;
  job_id: number;
  job_title: string;
  description: string;
  status: TodoStatus;
  proficiency_required: ProficiencyLevel;
  skill_ids: number[];
  skill_names: string[];
  notes: string;
  created_at: string | null;
  updated_at: string | null;
}
