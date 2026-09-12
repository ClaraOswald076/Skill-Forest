import { create } from 'zustand';
import type { TodoItem, TodoStatus } from '@/types/todo';
import { api } from '@/services/apiClient';

interface TodoFilter {
  job_id: number | null;
  status: TodoStatus | null;
  skill_id: number | null;
}

interface TodoState {
  todos: TodoItem[];
  loading: boolean;
  error: string | null;
  filters: TodoFilter;

  fetchTodos: () => Promise<void>;
  setFilter: (key: keyof TodoFilter, value: unknown) => void;
  toggleTodoStatus: (id: number) => Promise<void>;
  updateTodo: (id: number, data: Record<string, unknown>) => Promise<void>;
}

export const useTodoStore = create<TodoState>((set, get) => ({
  todos: [],
  loading: false,
  error: null,
  filters: { job_id: null, status: null, skill_id: null },

  fetchTodos: async () => {
    set({ loading: true, error: null });
    try {
      const { filters } = get();
      const todos = await api.getTodos({
        job_id: filters.job_id ?? undefined,
        status: filters.status ?? undefined,
        skill_id: filters.skill_id ?? undefined,
      });
      set({ todos, loading: false });
    } catch (err) {
      set({ loading: false, error: err instanceof Error ? err.message : '任务加载失败' });
    }
  },

  setFilter: (key, value) => {
    set((state) => ({
      filters: { ...state.filters, [key]: value },
    }));
    get().fetchTodos();
  },

  toggleTodoStatus: async (id) => {
    const todo = get().todos.find((t) => t.id === id);
    if (!todo) return;
    const nextStatus: TodoStatus =
      todo.status === 'completed' ? 'pending' : 'completed';
    // Optimistic update
    set((state) => ({
      todos: state.todos.map((t) =>
        t.id === id ? { ...t, status: nextStatus } : t
      ),
    }));
    try {
      await api.updateTodo(id, { status: nextStatus });
    } catch {
      // Revert on error
      get().fetchTodos();
    }
  },

  updateTodo: async (id, data) => {
    const updated = await api.updateTodo(id, data);
    set((state) => ({
      todos: state.todos.map((t) => (t.id === id ? updated : t)),
    }));
  },
}));
