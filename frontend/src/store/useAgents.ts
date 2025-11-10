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
  createAgent: (agent: Omit<Agent, 'id'> & { id: string }) => Promise<void>;
  updateAgent: (id: string, agent: Partial<Agent>) => Promise<void>;
  deleteAgent: (id: string) => Promise<void>;
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
      const token = JSON.parse(localStorage.getItem('smart-room-auth') || '{}')?.state?.token;
      const res = await fetch(`${API_BASE}/api/agents/${id}/toggle`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`
        },
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

  createAgent: async (agent) => {
    try {
      const token = JSON.parse(localStorage.getItem('smart-room-auth') || '{}')?.state?.token;
      const res = await fetch(`${API_BASE}/api/agents/`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(agent),
      });
      if (!res.ok) throw new Error('Failed to create agent');
      const newAgent = await res.json();
      set((state) => ({
        agents: [...state.agents, newAgent],
      }));
    } catch (err) {
      console.error('createAgent error', err);
      throw err;
    }
  },

  updateAgent: async (id, agent) => {
    try {
      const token = JSON.parse(localStorage.getItem('smart-room-auth') || '{}')?.state?.token;
      const res = await fetch(`${API_BASE}/api/agents/${id}`, {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(agent),
      });
      if (!res.ok) throw new Error('Failed to update agent');
      const updatedAgent = await res.json();
      set((state) => ({
        agents: state.agents.map((a) => (a.id === id ? updatedAgent : a)),
      }));
    } catch (err) {
      console.error('updateAgent error', err);
      throw err;
    }
  },

  deleteAgent: async (id) => {
    try {
      const token = JSON.parse(localStorage.getItem('smart-room-auth') || '{}')?.state?.token;
      const res = await fetch(`${API_BASE}/api/agents/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        },
      });
      if (!res.ok) throw new Error('Failed to delete agent');
      set((state) => ({
        agents: state.agents.filter((a) => a.id !== id),
      }));
    } catch (err) {
      console.error('deleteAgent error', err);
      throw err;
    }
  },
}));
