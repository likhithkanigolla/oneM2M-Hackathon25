import { create } from 'zustand';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface Agent {
  id: string;
  name: string;
  goal: string;
  rag_sources: string[];
  active: boolean;
  endpoint?: string;
  weight: number;
}

interface AgentState {
  agents: Agent[];
  setAgents: (agents: Agent[]) => void;
  fetchAgents: () => Promise<void>;
  toggleAgent: (id: string) => Promise<void>;
}

export const useAgents = create<AgentState>((set, get) => ({
  agents: [],
  setAgents: (agents) => set({ agents }),
  
  fetchAgents: async () => {
    try {
      const res = await fetch(`${API_BASE}/api/agents/`);
      if (!res.ok) throw new Error('Failed to fetch agents');
      const agents = await res.json();
      set({ agents });
    } catch (err) {
      console.error('fetchAgents error', err);
    }
  },
  
  toggleAgent: async (id) => {
    try {
      const res = await fetch(`${API_BASE}/api/agents/${id}/toggle`, {
        method: 'PATCH',
      });
      if (!res.ok) throw new Error('Failed to toggle agent');
      const updatedAgent = await res.json();
      set((state) => ({
        agents: state.agents.map((a) => (a.id === id ? updatedAgent : a)),
      }));
    } catch (err) {
      console.error('toggleAgent error', err);
    }
  },
}));
