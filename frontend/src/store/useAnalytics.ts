import { create } from 'zustand';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface HistoricalDataPoint {
  time: string;
  comfort: number;
  energy: number;
  reliability: number;
}

export interface RecentEvent {
  time: string;
  room: string;
  event: string;
  impact: string;
}

export interface AgentDecision {
  time: string;
  agent: string;
  decision: string;
  confidence: number;
  reasoning: string;
}

export interface SLOPerformanceData {
  id: number;
  name: string;
  current_value: number;
  target_value: number;
  performance_score: number;
  unit: string;
}

interface AnalyticsState {
  historicalData: HistoricalDataPoint[];
  recentEvents: RecentEvent[];
  agentDecisions: AgentDecision[];
  sloPerformance: SLOPerformanceData[];
  loading: boolean;
  error: string | null;
  
  fetchHistoricalData: () => Promise<void>;
  fetchRecentEvents: () => Promise<void>;
  fetchAgentDecisions: (roomId: number) => Promise<void>;
  fetchSLOPerformance: (roomId: number) => Promise<void>;
}

export const useAnalytics = create<AnalyticsState>((set) => ({
  historicalData: [],
  recentEvents: [],
  agentDecisions: [],
  sloPerformance: [],
  loading: false,
  error: null,
  
  fetchHistoricalData: async () => {
    set({ loading: true, error: null });
    try {
      const res = await fetch(`${API_BASE}/api/analytics/historical-data`);
      if (!res.ok) throw new Error('Failed to fetch historical data');
      const data = await res.json();
      set({ historicalData: data, loading: false });
    } catch (err) {
      console.error('fetchHistoricalData error:', err);
      set({ error: err instanceof Error ? err.message : 'Unknown error', loading: false });
    }
  },
  
  fetchRecentEvents: async () => {
    set({ loading: true, error: null });
    try {
      const res = await fetch(`${API_BASE}/api/analytics/recent-events`);
      if (!res.ok) throw new Error('Failed to fetch recent events');
      const data = await res.json();
      set({ recentEvents: data, loading: false });
    } catch (err) {
      console.error('fetchRecentEvents error:', err);
      set({ error: err instanceof Error ? err.message : 'Unknown error', loading: false });
    }
  },
  
  fetchAgentDecisions: async (roomId: number) => {
    set({ loading: true, error: null });
    try {
      const res = await fetch(`${API_BASE}/api/analytics/agent-decisions/${roomId}`);
      if (!res.ok) throw new Error('Failed to fetch agent decisions');
      const data = await res.json();
      set({ agentDecisions: data, loading: false });
    } catch (err) {
      console.error('fetchAgentDecisions error:', err);
      set({ error: err instanceof Error ? err.message : 'Unknown error', loading: false });
    }
  },
  
  fetchSLOPerformance: async (roomId: number) => {
    set({ loading: true, error: null });
    try {
      const res = await fetch(`${API_BASE}/api/analytics/slo-performance/${roomId}`);
      if (!res.ok) throw new Error('Failed to fetch SLO performance');
      const data = await res.json();
      set({ sloPerformance: data, loading: false });
    } catch (err) {
      console.error('fetchSLOPerformance error:', err);
      set({ error: err instanceof Error ? err.message : 'Unknown error', loading: false });
    }
  },
}));
