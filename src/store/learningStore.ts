import { create } from 'zustand';
import type { LearningModule, ChatSessionListItem, ChatSession, ChatMessage, ChatSendResponse, QuizGenerateResponse, QuizQuestion, QuizSubmitResponse, GradedResult, ErrorBookEntry, ErrorStats } from '@/types/learning';
import { api } from '@/services/apiClient';

interface LearningState {
  // Tutorial
  tutorial: LearningModule | null;
  tutorialLoading: boolean;

  // Chat
  sessions: ChatSessionListItem[];
  activeSession: ChatSession | null;
  sendingMessage: boolean;

  // Quiz
  currentQuestions: QuizQuestion[] | null;
  currentAttemptId: number | null;
  quizLoading: boolean;
  gradingResult: QuizSubmitResponse | null;
  grading: boolean;

  // Error book
  errors: ErrorBookEntry[];
  errorStats: ErrorStats | null;

  // Actions — Tutorial
  loadTutorial: (todoId: number) => Promise<void>;
  regenerateTutorial: (todoId: number) => Promise<void>;

  // Actions — lifecycle
  resetForTodo: () => void;

  // Actions — Chat
  loadSessions: (todoId: number) => Promise<void>;
  createSession: (todoId: number, title?: string) => Promise<number>;
  loadSession: (sessionId: number) => Promise<void>;
  deleteSession: (sessionId: number) => Promise<void>;
  toggleDeepThinking: (sessionId: number, enabled: boolean) => Promise<void>;
  sendMessage: (sessionId: number, message: string) => Promise<ChatSendResponse>;

  // Actions — Quiz
  generateQuiz: (todoId: number) => Promise<void>;
  submitQuiz: (attemptId: number, answers: { q_number: number; answer: string }[]) => Promise<void>;
  clearQuiz: () => void;

  // Actions — Error Book
  loadErrors: (filters?: { skill_id?: number; reviewed?: boolean }) => Promise<void>;
  loadErrorStats: () => Promise<void>;
  markErrorReviewed: (entryId: number) => Promise<void>;
  deleteError: (entryId: number) => Promise<void>;
}

export const useLearningStore = create<LearningState>((set, get) => ({
  tutorial: null,
  tutorialLoading: false,
  sessions: [],
  activeSession: null,
  sendingMessage: false,
  currentQuestions: null,
  currentAttemptId: null,
  quizLoading: false,
  gradingResult: null,
  grading: false,
  errors: [],
  errorStats: null,

  // ── Lifecycle ──
  // 切换学习任务时必须先调用：store 是全局单例，不清掉上一个任务的状态会串数据
  resetForTodo: () =>
    set({
      tutorial: null,
      tutorialLoading: false,
      sessions: [],
      activeSession: null,
      sendingMessage: false,
      currentQuestions: null,
      currentAttemptId: null,
      quizLoading: false,
      gradingResult: null,
      grading: false,
    }),

  // ── Tutorial ──
  loadTutorial: async (todoId) => {
    set({ tutorialLoading: true });
    try {
      const res = await api.generateTutorial(todoId);
      set({ tutorial: res, tutorialLoading: false });
    } catch {
      set({ tutorialLoading: false });
    }
  },

  regenerateTutorial: async (todoId) => {
    set({ tutorialLoading: true });
    try {
      const res = await api.generateTutorialRegenerate(todoId);
      set({ tutorial: res, tutorialLoading: false });
    } catch {
      set({ tutorialLoading: false });
    }
  },

  // ── Chat ──
  loadSessions: async (todoId) => {
    const sessions = await api.listChatSessions(todoId);
    set({ sessions });
  },

  createSession: async (todoId, title) => {
    const session = await api.createChatSession({ todo_id: todoId, title: title || '新对话' });
    get().loadSessions(todoId);
    return session.id;
  },

  loadSession: async (sessionId) => {
    const session = await api.getChatSession(sessionId);
    set({ activeSession: session });
  },

  deleteSession: async (sessionId) => {
    await api.deleteChatSession(sessionId);
    const state = get();
    if (state.activeSession?.id === sessionId) {
      set({ activeSession: null });
    }
    // Reload sessions for whatever todo is active
    if (state.activeSession?.todo_id) {
      get().loadSessions(state.activeSession.todo_id);
    }
  },

  toggleDeepThinking: async (sessionId, enabled) => {
    await api.updateChatSession(sessionId, { deep_thinking: enabled });
    const state = get();
    if (state.activeSession && state.activeSession.id === sessionId) {
      set({ activeSession: { ...state.activeSession, deep_thinking: enabled } });
    }
  },

  sendMessage: async (sessionId, message) => {
    set({ sendingMessage: true });
    try {
      const res = await api.sendChatMessage({ session_id: sessionId, message });
      const state = get();
      if (state.activeSession && state.activeSession.id === sessionId) {
        set({
          activeSession: {
            ...state.activeSession,
            messages: [...state.activeSession.messages, res.user_message, res.ai_message],
          },
        });
      }
      set({ sendingMessage: false });
      return res;
    } catch {
      set({ sendingMessage: false });
      throw new Error('消息发送失败');
    }
  },

  // ── Quiz ──
  generateQuiz: async (todoId) => {
    set({ quizLoading: true, gradingResult: null });
    try {
      const res = await api.generateQuiz(todoId);
      set({
        currentQuestions: res.questions,
        currentAttemptId: res.attempt_id,
        quizLoading: false,
      });
    } catch {
      set({ quizLoading: false });
    }
  },

  submitQuiz: async (attemptId, answers) => {
    set({ grading: true });
    try {
      const res = await api.submitQuiz({ attempt_id: attemptId, answers });
      set({ gradingResult: res, grading: false });
    } catch {
      set({ grading: false });
    }
  },

  clearQuiz: () => set({ currentQuestions: null, currentAttemptId: null, gradingResult: null }),

  // ── Error Book ──
  loadErrors: async (filters) => {
    const errors = await api.getErrors(filters);
    set({ errors });
  },

  loadErrorStats: async () => {
    const stats = await api.getErrorStats();
    set({ errorStats: stats });
  },

  markErrorReviewed: async (entryId) => {
    await api.updateError(entryId, { reviewed: true });
    get().loadErrors();
    get().loadErrorStats();
  },

  deleteError: async (entryId) => {
    await api.deleteError(entryId);
    get().loadErrors();
    get().loadErrorStats();
  },
}));
