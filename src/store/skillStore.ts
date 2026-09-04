import { create } from 'zustand';
import type { Skill, SkillTreeNode } from '@/types/skill';
import { api } from '@/services/apiClient';

interface SkillState {
  skills: Skill[];
  skillTree: SkillTreeNode[];
  selectedSkill: Skill | null;
  loading: boolean;
  error: string | null;

  fetchSkills: () => Promise<void>;
  fetchSkillTree: () => Promise<void>;
  selectSkill: (skill: Skill | null) => void;
  updateSkill: (id: number, data: Record<string, unknown>) => Promise<void>;
  mergeSkills: (sourceId: number, targetId: number) => Promise<void>;
}

export const useSkillStore = create<SkillState>((set, get) => ({
  skills: [],
  skillTree: [],
  selectedSkill: null,
  loading: false,
  error: null,

  fetchSkills: async () => {
    set({ loading: true, error: null });
    try {
      const skills = await api.getSkills();
      set({ skills, loading: false });
    } catch (err) {
      set({ loading: false, error: err instanceof Error ? err.message : '技能加载失败' });
    }
  },

  fetchSkillTree: async () => {
    set({ loading: true, error: null });
    try {
      const res = await api.getSkillTree();
      set({ skillTree: res.tree, loading: false });
    } catch (err) {
      set({ loading: false, error: err instanceof Error ? err.message : '技能树加载失败' });
    }
  },

  selectSkill: (skill) => set({ selectedSkill: skill }),

  updateSkill: async (id, data) => {
    const updated = await api.updateSkill(id, data);
    set((state) => ({
      skills: state.skills.map((s) => (s.id === id ? { ...s, ...data } : s)),
      selectedSkill: state.selectedSkill?.id === id ? updated : state.selectedSkill,
    }));
    // Refresh tree to reflect changes
    get().fetchSkillTree();
  },

  mergeSkills: async (sourceId, targetId) => {
    await api.mergeSkills(sourceId, targetId);
    get().fetchSkills();
    get().fetchSkillTree();
    set({ selectedSkill: null });
  },
}));
