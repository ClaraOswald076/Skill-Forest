export interface DomainCompletion {
  category_l1: string;
  total_skills: number;
  completed_skills: number;
  completion_rate: number;
}

export interface ExpertiseItem {
  category_l1: string;
  category_l2: string;
  skill_count: number;
  avg_proficiency_level: number;
  top_skills: string[];
}

export interface BestMatchingJob {
  job_id: number;
  job_title: string;
  company: string;
  total_skills_required: number;
  completed_skills: number;
  match_rate: number;
}

export interface DashboardStats {
  total_skills: number;
  completed_skills: number;
  overall_completion_rate: number;
  total_todos: number;
  completed_todos: number;
  total_jobs: number;
  domains: DomainCompletion[];
  best_matching_job: BestMatchingJob | null;
  deepest_expertise: ExpertiseItem[];
  recent_activity: string;
}
