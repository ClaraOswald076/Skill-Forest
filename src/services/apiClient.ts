const BASE_URL = '/api';

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API Error ${res.status}: ${text}`);
  }
  return res.json();
}

export const api = {
  // Dashboard
  getDashboard: () => request<import('@/types/dashboard').DashboardStats>('/dashboard'),

  // Skills
  getSkills: (params?: { status?: string; category_l1?: string }) => {
    const qs = new URLSearchParams();
    if (params?.status) qs.set('status', params.status);
    if (params?.category_l1) qs.set('category_l1', params.category_l1);
    const q = qs.toString();
    return request<import('@/types/skill').Skill[]>(`/skills${q ? `?${q}` : ''}`);
  },
  getSkillTree: () => request<import('@/types/skill').SkillTreeResponse>('/skills/tree'),
  getSkill: (id: number) => request<import('@/types/skill').Skill>(`/skills/${id}`),
  updateSkill: (id: number, data: Record<string, unknown>) =>
    request<import('@/types/skill').Skill>(`/skills/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  mergeSkills: (source_id: number, target_id: number) =>
    request<{ ok: boolean }>('/skills/merge', {
      method: 'POST',
      body: JSON.stringify({ source_id, target_id }),
    }),

  // Jobs
  getJobs: () => request<import('@/types/job').Job[]>('/jobs'),
  getJob: (id: number) => request<import('@/types/job').JobDetail>(`/jobs/${id}`),
  createJob: (data: import('@/types/analysis').JobSaveRequest) =>
    request<import('@/types/job').JobDetail>('/jobs', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  deleteJob: (id: number) => request<{ ok: boolean }>(`/jobs/${id}`, { method: 'DELETE' }),

  // Analysis
  previewAnalysis: (data: import('@/types/analysis').AnalysisRequest) =>
    request<import('@/types/analysis').AnalysisResponse>('/analysis/preview', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Todos
  getTodos: (params?: { job_id?: number; status?: string; skill_id?: number }) => {
    const qs = new URLSearchParams();
    if (params?.job_id) qs.set('job_id', String(params.job_id));
    if (params?.status) qs.set('status', params.status);
    if (params?.skill_id) qs.set('skill_id', String(params.skill_id));
    const q = qs.toString();
    return request<import('@/types/todo').TodoItem[]>(`/todos${q ? `?${q}` : ''}`);
  },
  updateTodo: (id: number, data: Record<string, unknown>) =>
    request<import('@/types/todo').TodoItem>(`/todos/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  // ── Learning — Tutorial ──
  generateTutorial: (todoId: number) =>
    request<import('@/types/learning').LearningModule>('/learning/tutorial/generate', {
      method: 'POST',
      body: JSON.stringify({ todo_id: todoId }),
    }),
  generateTutorialRegenerate: (todoId: number) =>
    request<import('@/types/learning').LearningModule>('/learning/tutorial/generate', {
      method: 'POST',
      body: JSON.stringify({ todo_id: todoId, regenerate: true }),
    }),
  getTutorial: (todoId: number) =>
    request<import('@/types/learning').LearningModule>(`/learning/tutorial/${todoId}`),

  // ── Learning — Chat ──
  createChatSession: (data: { todo_id: number; title?: string }) =>
    request<import('@/types/learning').ChatSession>('/learning/chat/sessions', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  listChatSessions: (todoId: number) =>
    request<import('@/types/learning').ChatSessionListItem[]>(`/learning/chat/sessions?todo_id=${todoId}`),
  getChatSession: (sessionId: number) =>
    request<import('@/types/learning').ChatSession>(`/learning/chat/sessions/${sessionId}`),
  deleteChatSession: (sessionId: number) =>
    request<{ ok: boolean }>(`/learning/chat/sessions/${sessionId}`, { method: 'DELETE' }),
  updateChatSession: (sessionId: number, data: Record<string, unknown>) =>
    request<import('@/types/learning').ChatSession>(`/learning/chat/sessions/${sessionId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  sendChatMessage: (data: { session_id: number; message: string }) =>
    request<import('@/types/learning').ChatSendResponse>('/learning/chat/send', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // ── Learning — Quiz ──
  generateQuiz: (todoId: number) =>
    request<import('@/types/learning').QuizGenerateResponse>('/learning/quiz/generate', {
      method: 'POST',
      body: JSON.stringify({ todo_id: todoId }),
    }),
  listQuizAttempts: (todoId: number) =>
    request<import('@/types/learning').QuizAttempt[]>(`/learning/quiz/attempts?todo_id=${todoId}`),
  getQuizAttempt: (attemptId: number) =>
    request<import('@/types/learning').QuizAttempt>(`/learning/quiz/attempts/${attemptId}`),
  submitQuiz: (data: { attempt_id: number; answers: { q_number: number; answer: string }[] }) =>
    request<import('@/types/learning').QuizSubmitResponse>('/learning/quiz/submit', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // ── Learning — Error Book ──
  getErrors: (params?: { skill_id?: number; reviewed?: boolean }) => {
    const qs = new URLSearchParams();
    if (params?.skill_id) qs.set('skill_id', String(params.skill_id));
    if (params?.reviewed !== undefined) qs.set('reviewed', String(params.reviewed));
    const q = qs.toString();
    return request<import('@/types/learning').ErrorBookEntry[]>(`/learning/errors${q ? `?${q}` : ''}`);
  },
  updateError: (entryId: number, data: { reviewed: boolean }) =>
    request<import('@/types/learning').ErrorBookEntry>(`/learning/errors/${entryId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  deleteError: (entryId: number) =>
    request<{ ok: boolean }>(`/learning/errors/${entryId}`, { method: 'DELETE' }),
  getErrorStats: () => request<import('@/types/learning').ErrorStats>('/learning/errors/stats'),
};
