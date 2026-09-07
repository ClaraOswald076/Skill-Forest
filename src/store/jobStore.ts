import { create } from 'zustand';
import type { Job, JobDetail } from '@/types/job';
import type { AnalysisResponse, JobSaveRequest, MergeSuggestion } from '@/types/analysis';
import { api } from '@/services/apiClient';

interface JobState {
  jobs: Job[];
  selectedJob: JobDetail | null;
  loading: boolean;
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
  isAnalyzing: false,
  analysisResult: null,
  mergeDecisions: {},
  pendingRawText: '',
  pendingUrl: '',

  fetchJobs: async () => {
    set({ loading: true });
    const jobs = await api.getJobs();
    set({ jobs, loading: false });
  },

  fetchJob: async (id) => {
    set({ loading: true });
    const job = await api.getJob(id);
    set({ selectedJob: job, loading: false });
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

    // The backend merges a skill only when merge_decisions says "merge" AND the
    // skill carries merge_with_existing_id, so resolve the target id from the
    // accepted suggestions instead of passing analysis skills through as-is.
    const mergeTargetByName = new Map<string, number>(); // new_skill_name -> existing_skill_id
    for (const ms of analysisResult.merge_suggestions) {
      if (ms.action === 'merge') mergeTargetByName.set(ms.new_skill_name, ms.existing_skill_id);
    }
    const skills = analysisResult.skills.map((s) => {
      const targetId = mergeTargetByName.get(s.name);
      return targetId != null ? { ...s, merge_with_existing_id: targetId } : s;
    });

    const saveReq: JobSaveRequest = {
      raw_text: pendingRawText,
      url: pendingUrl,
      title: analysisResult.job_title,
      company: analysisResult.company,
      skills,
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
