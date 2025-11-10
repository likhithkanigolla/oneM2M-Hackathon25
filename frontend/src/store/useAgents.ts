import { create } from 'zustand';

export interface Agent {
  id: string;
  name: string;
  goal: string;
  ragSources: string[];
  active: boolean;
  endpoint?: string;
  weight: number;
}

interface AgentState {
  agents: Agent[];
  addAgent: (agent: Agent) => void;
  removeAgent: (id: string) => void;
  toggleAgent: (id: string) => void;
  updateAgent: (id: string, updates: Partial<Agent>) => void;
}

export const useAgents = create<AgentState>((set) => ({
  agents: [
    {
      id: 'gemini',
      name: 'Gemini',
      goal: 'Energy Efficiency',
      ragSources: ['sensor', 'energy', 'device_logs'],
      active: true,
      weight: 0.35,
    },
    {
      id: 'claude',
      name: 'Claude',
      goal: 'SLO Priority & Comfort',
      ragSources: ['slo', 'scenario', 'occupancy'],
      active: true,
      weight: 0.40,
    },
    {
      id: 'gpt',
      name: 'GPT-5',
      goal: 'Security & Reliability',
      ragSources: ['device_logs', 'weather', 'scenarios'],
      active: true,
      weight: 0.25,
    },
  ],
  addAgent: (agent) =>
    set((state) => ({
      agents: [...state.agents, agent],
    })),
  removeAgent: (id) =>
    set((state) => ({
      agents: state.agents.filter((agent) => agent.id !== id),
    })),
  toggleAgent: (id) =>
    set((state) => ({
      agents: state.agents.map((agent) =>
        agent.id === id ? { ...agent, active: !agent.active } : agent
      ),
    })),
  updateAgent: (id, updates) =>
    set((state) => ({
      agents: state.agents.map((agent) =>
        agent.id === id ? { ...agent, ...updates } : agent
      ),
    })),
}));
