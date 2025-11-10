import { create } from 'zustand';

interface SLO {
  id: number;
  name: string;
  description: string;
  weight: number;
  active: boolean;
  type?: string;
  criteria?: string;
  target_value?: number;
}

interface SLOStore {
  slos: SLO[];
  loading: boolean;
  fetchSLOs: () => Promise<void>;
  createSLO: (slo: Omit<SLO, 'id'>) => Promise<void>;
  updateSLO: (id: number, slo: Partial<SLO>) => Promise<void>;
  deleteSLO: (id: number) => Promise<void>;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const useSLOs = create<SLOStore>((set, get) => ({
  slos: [],
  loading: false,

  fetchSLOs: async () => {
    set({ loading: true });
    try {
      const response = await fetch(`${API_BASE}/api/slos`);
      const slos = await response.json();
      set({ slos, loading: false });
    } catch (error) {
      console.error('Failed to fetch SLOs:', error);
      set({ loading: false });
    }
  },

  createSLO: async (sloData) => {
    try {
      const response = await fetch(`${API_BASE}/api/slos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sloData),
      });
      const newSLO = await response.json();
      set(state => ({ slos: [...state.slos, newSLO] }));
    } catch (error) {
      console.error('Failed to create SLO:', error);
    }
  },

  updateSLO: async (id, sloData) => {
    try {
      const response = await fetch(`${API_BASE}/api/slos/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sloData),
      });
      const updatedSLO = await response.json();
      set(state => ({
        slos: state.slos.map(slo => slo.id === id ? updatedSLO : slo)
      }));
    } catch (error) {
      console.error('Failed to update SLO:', error);
    }
  },

  deleteSLO: async (id) => {
    try {
      await fetch(`${API_BASE}/api/slos/${id}`, {
        method: 'DELETE',
      });
      set(state => ({
        slos: state.slos.filter(slo => slo.id !== id)
      }));
    } catch (error) {
      console.error('Failed to delete SLO:', error);
    }
  },
}));