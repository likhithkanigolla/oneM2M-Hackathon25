import { create } from 'zustand';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface Scenario {
  id: number;
  name: string;
  description?: string;
  active: boolean;
  config?: any;
  priority?: string;
  trigger?: string;
  impact?: string;
}

interface ScenarioState {
  scenarios: Scenario[];
  setScenarios: (scenarios: Scenario[]) => void;
  fetchScenarios: () => Promise<void>;
  toggleScenario: (id: number) => Promise<void>;
}

export const useScenarios = create<ScenarioState>((set, get) => ({
  scenarios: [],
  setScenarios: (scenarios) => set({ scenarios }),
  
  fetchScenarios: async () => {
    try {
      const res = await fetch(`${API_BASE}/api/scenarios/`);
      if (!res.ok) throw new Error('Failed to fetch scenarios');
      const scenarios = await res.json();
      set({ scenarios });
    } catch (err) {
      console.error('fetchScenarios error', err);
    }
  },
  
  toggleScenario: async (id) => {
    try {
      const res = await fetch(`${API_BASE}/api/scenarios/${id}/toggle`, {
        method: 'PATCH',
      });
      if (!res.ok) throw new Error('Failed to toggle scenario');
      const updatedScenario = await res.json();
      set((state) => ({
        scenarios: state.scenarios.map((s) => (s.id === id ? updatedScenario : s)),
      }));
    } catch (err) {
      console.error('toggleScenario error', err);
    }
  },
}));
