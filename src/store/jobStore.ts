import { create } from 'zustand';
import type { Job, JobDetail } from '@/types/job';
import type { AnalysisResponse, JobSaveRequest, MergeSuggestion } from '@/types/analysis';
import { api } from '@/services/apiClient';

interface JobState {
  jobs: Job[];
  selectedJob: JobDetail | null;
  loading: boolean;
  error: string | null;
  isAnalyzing: boolean;
  analysisResult: AnalysisResponse | null;
  mergeDecisions: Record<string, 'merge' | 'keep_separate'>;
  pendingRawText: string;
  pendingUrl: string;

  fetchJobs: () => Promise<void>;
  fetchJob: (id: number) => Promise<void>;
  selectJob: (job: JobDetail | null) => void;
  startAnalysis: (rawText: string, title?: string, company?: string, url?: string) => Promise<void>;
  setMergeDecision: (skillName: string, decision: 'merge' | 'keep_separate') => void;
  confirmAndSave: () => Promise<JobDetail | null>;
  deleteJob: (id: number) => Promise<void>;
  clearAnalysis: () => void;
}

export const useJobStore = create<JobState>((set, get) => ({
  jobs: [],
  selectedJob: null,
  loading: false,
  error: null,
  isAnalyzing: false,
  analysisResult: null,
  mergeDecisions: {},
  pendingRawText: '',
  pendingUrl: '',

  fetchJobs: async () => {
    set({ loading: true, error: null });
    try {
      const jobs = await api.getJobs();
      set({ jobs, loading: false });
    } catch (err) {
      set({ loading: false, error: err instanceof Error ? err.message : '岗位列表加载失败' });
    }
  },

  fetchJob: async (id) => {
    set({ loading: true, error: null });
    try {
      const job = await api.getJob(id);
      set({ selectedJob: job, loading: false });
    } catch (err) {
      set({ loading: false, error: err instanceof Error ? err.message : '岗位加载失败' });
    }
  },

  selectJob: (job) => set({ selectedJob: job }),

  startAnalysis: async (rawText, title, company, url) => {
    set({ isAnalyzing: true, analysisResult: null, mergeDecisions: {}, pendingRawText: rawText, pendingUrl: url || '' });
    try {
      const result = await api.previewAnalysis({ raw_text: rawText, job_title: title, company });
      // Auto-decide merge decisions based on suggestions
      const decisions: Record<string, 'merge' | 'keep_separate'> = {};
      for (const ms of result.merge_suggestions) {
        decisions[ms.new_skill_name] = ms.action;
      }
      set({ analysisResult: result, mergeDecisions: decisions, isAnalyzing: false });
    } catch (err) {
      set({ isAnalyzing: false });
      throw err;
    }
  },

  setMergeDecision: (skillName, decision) => {
    set((state) => ({
      mergeDecisions: { ...state.mergeDecisions, [skillName]: decision },
    }));
  },

  confirmAndSave: async () => {
    const { analysisResult, mergeDecisions, pendingRawText, pendingUrl } = get();
    if (!analysisResult) return null;

    const saveReq: JobSaveRequest = {
      raw_text: pendingRawText,
      url: pendingUrl,
      title: analysisResult.job_title,
      company: analysisResult.company,
      skills: analysisResult.skills,
      todos: analysisResult.todos,
      merge_decisions: mergeDecisions,
    };

    const job = await api.createJob(saveReq);
    set({ analysisResult: null, mergeDecisions: {} });
    get().fetchJobs();
    return job;
  },

  deleteJob: async (id) => {
    await api.deleteJob(id);
    get().fetchJobs();
    if (get().selectedJob?.id === id) {
      set({ selectedJob: null });
    }
  },

  clearAnalysis: () => set({ analysisResult: null, mergeDecisions: {}, pendingRawText: '', pendingUrl: '' }),
}));
