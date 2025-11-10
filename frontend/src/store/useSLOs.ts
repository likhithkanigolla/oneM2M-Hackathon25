import { create } from 'zustand';
import { useAuth } from './useAuth';

interface SLO {
  id: number;
  name: string;
  description?: string;
  weight: number;
  active: boolean;
  type?: string;
  criteria?: string;
  target_value?: number;
  metric?: string;
  config?: any;
  created_by: string;
  is_system_defined: boolean;
}

interface SLOStore {
  slos: SLO[];
  loading: boolean;
  error: string | null;
  fetchSLOs: () => Promise<void>;
  createSLO: (slo: Omit<SLO, 'id' | 'created_by'>) => Promise<void>;
  updateSLO: (id: number, slo: Partial<SLO>) => Promise<void>;
  deleteSLO: (id: number) => Promise<void>;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const useSLOs = create<SLOStore>((set, get) => ({
  slos: [],
  loading: false,
  error: null,

  fetchSLOs: async () => {
    const { token } = useAuth.getState();
    if (!token) {
      set({ error: 'No authentication token' });
      return;
    }

    set({ loading: true, error: null });
    try {
      const response = await fetch(`${API_BASE}/api/slos/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch SLOs');
      }

      const slos = await response.json();
      set({ slos, loading: false });
    } catch (error) {
      console.error('Failed to fetch SLOs:', error);
      set({ error: (error as Error).message, loading: false });
    }
  },

  createSLO: async (sloData) => {
    const { token } = useAuth.getState();
    if (!token) {
      set({ error: 'No authentication token' });
      return;
    }

    set({ loading: true, error: null });
    try {
      const response = await fetch(`${API_BASE}/api/slos/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(sloData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create SLO');
      }

      const newSLO = await response.json();
      set(state => ({ 
        slos: [...state.slos, newSLO], 
        loading: false 
      }));
    } catch (error) {
      console.error('Failed to create SLO:', error);
      set({ error: (error as Error).message, loading: false });
      throw error;
    }
  },

  updateSLO: async (id, sloData) => {
    const { token } = useAuth.getState();
    if (!token) {
      set({ error: 'No authentication token' });
      return;
    }

    set({ loading: true, error: null });
    try {
      const response = await fetch(`${API_BASE}/api/slos/${id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(sloData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update SLO');
      }

      const updatedSLO = await response.json();
      set(state => ({
        slos: state.slos.map(slo => slo.id === id ? updatedSLO : slo),
        loading: false
      }));
    } catch (error) {
      console.error('Failed to update SLO:', error);
      set({ error: (error as Error).message, loading: false });
      throw error;
    }
  },

  deleteSLO: async (id) => {
    const { token } = useAuth.getState();
    if (!token) {
      set({ error: 'No authentication token' });
      return;
    }

    set({ loading: true, error: null });
    try {
      const response = await fetch(`${API_BASE}/api/slos/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete SLO');
      }

      set(state => ({
        slos: state.slos.filter(slo => slo.id !== id),
        loading: false
      }));
    } catch (error) {
      console.error('Failed to delete SLO:', error);
      set({ error: (error as Error).message, loading: false });
      throw error;
    }
  },
}));