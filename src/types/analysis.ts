import type { ProficiencyLevel } from './skill';

export interface AnalysisRequest {
  raw_text: string;
  job_title?: string;
  company?: string;
  url?: string;
}

export interface ExtractedSkill {
  name: string;
  description: string;
  category_l1: string;
  category_l2: string;
  category_l3: string;
  proficiency: ProficiencyLevel;
  merge_with_existing_id: number | null;
  merge_confidence: number;
}

export interface GeneratedTodo {
  description: string;
  skill_names: string[];
  proficiency_required: ProficiencyLevel;
}

export interface MergeSuggestion {
  existing_skill_id: number;
  existing_skill_name: string;
  new_skill_name: string;
  similarity: number;
  action: 'merge' | 'keep_separate';
}

export interface AnalysisResponse {
  job_title: string;
  company: string;
  skills: ExtractedSkill[];
  todos: GeneratedTodo[];
  merge_suggestions: MergeSuggestion[];
  summary: string;
}

export interface JobSaveRequest {
  raw_text: string;
  url: string;
  title: string;
  company: string;
  skills: ExtractedSkill[];
  todos: GeneratedTodo[];
  merge_decisions: Record<string, 'merge' | 'keep_separate'>;
}
