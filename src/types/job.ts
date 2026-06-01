import type { Skill } from './skill';
import type { TodoItem } from './todo';

export interface Job {
  id: number;
  title: string;
  company: string;
  raw_text: string;
  url: string;
  skill_ids: number[];
  skill_count: number;
  todo_count: number;
  created_at: string | null;
}

export interface JobDetail extends Job {
  skills: Skill[];
  todos: TodoItem[];
}

export interface JobCreateRequest {
  raw_text: string;
  url?: string;
  title?: string;
  company?: string;
}
