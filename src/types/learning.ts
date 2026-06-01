// Learning module types

export interface LearningModule {
  id: number;
  todo_id: number;
  tutorial_content: string;
  tutorial_version: number;
  last_generated_at: string | null;
  created_at: string | null;
}

// ── Chat ──

export interface ChatSessionListItem {
  id: number;
  todo_id: number;
  title: string;
  deep_thinking: boolean;
  message_count: number;
  last_message_preview: string;
  created_at: string | null;
  updated_at: string | null;
}

export interface ChatMessage {
  id: number;
  session_id: number;
  role: 'user' | 'assistant';
  content: string;
  reasoning_content: string;
  tokens_used: number;
  created_at: string | null;
}

export interface ChatSession {
  id: number;
  todo_id: number;
  title: string;
  deep_thinking: boolean;
  messages: ChatMessage[];
  created_at: string | null;
  updated_at: string | null;
}

export interface ChatSendResponse {
  user_message: ChatMessage;
  ai_message: ChatMessage;
}

// ── Quiz ──

export interface QuizQuestion {
  q_number: number;
  question_type: 'choice' | 'essay' | 'definition';
  question_text: string;
  options: string[];
  correct_answer: string;
}

export interface QuizGenerateResponse {
  attempt_id: number;
  todo_id: number;
  questions: QuizQuestion[];
}

export interface QuizAnswer {
  q_number: number;
  answer: string;
}

export interface GradedResult {
  q_number: number;
  score: number;
  max_score: number;
  is_correct: boolean;
  explanation: string;
}

export interface QuizSubmitResponse {
  attempt_id: number;
  results: GradedResult[];
  total_score: number;
  max_score: number;
  overall_feedback: string;
}

export interface QuizAttempt {
  id: number;
  todo_id: number;
  questions_json: string;
  answers_json: string;
  started_at: string | null;
  submitted_at: string | null;
  graded_json: string;
  total_score: number | null;
  max_score: number | null;
  created_at: string | null;
}

// ── Error Book ──

export interface ErrorBookEntry {
  id: number;
  quiz_attempt_id: number | null;
  todo_id: number;
  skill_id: number | null;
  question_type: string;
  question_text: string;
  user_answer: string;
  correct_answer: string;
  explanation: string;
  reviewed: boolean;
  created_at: string | null;
  reviewed_at: string | null;
}

export interface ErrorStats {
  total: number;
  reviewed: number;
  unreviewed: number;
  by_skill: { skill_id: number; skill_name: string; count: number }[];
}
