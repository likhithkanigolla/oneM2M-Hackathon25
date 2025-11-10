import { create } from 'zustand';

interface DecisionLog {
  id: number;
  room_id: number;
  agent_id: string;
  decision: string;
  reasoning: string;
  timestamp: string;
  confidence?: number;
  context?: any;
}

interface RoomMetrics {
  room_id: number;
  avg_temperature: number;
  avg_humidity: number;
  avg_air_quality: number;
  energy_consumption: number;
  comfort_score: number;
  efficiency_score: number;
  period: string;
}

interface AgentPerformance {
  agent_id: string;
  total_decisions: number;
  avg_confidence: number;
  success_rate: number;
  response_time: number;
}

interface AnalyticsStore {
  decisionLogs: DecisionLog[];
  roomMetrics: RoomMetrics[];
  agentPerformance: AgentPerformance[];
  loading: boolean;
  fetchDecisionLogs: (roomId?: number, agentId?: string, limit?: number) => Promise<void>;
  fetchRoomMetrics: (roomId: number) => Promise<void>;
  fetchAgentPerformance: () => Promise<void>;
  fetchRoomInsights: (roomId: number) => Promise<any>;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

export const useAnalytics = create<AnalyticsStore>((set, get) => ({
  decisionLogs: [],
  roomMetrics: [],
  agentPerformance: [],
  loading: false,

  fetchDecisionLogs: async (roomId, agentId, limit = 100) => {
    set({ loading: true });
    try {
      const params = new URLSearchParams();
      if (roomId) params.append('room_id', roomId.toString());
      if (agentId) params.append('agent_id', agentId);
      if (limit) params.append('limit', limit.toString());

      const response = await fetch(`${API_BASE}/api/analytics/decision-logs?${params}`);
      const decisionLogs = await response.json();
      set({ decisionLogs, loading: false });
    } catch (error) {
      console.error('Failed to fetch decision logs:', error);
      set({ loading: false });
    }
  },

  fetchRoomMetrics: async (roomId) => {
    try {
      const response = await fetch(`${API_BASE}/api/analytics/room-metrics/${roomId}`);
      const metrics = await response.json();
      set(state => ({
        roomMetrics: [...state.roomMetrics.filter(m => m.room_id !== roomId), metrics]
      }));
    } catch (error) {
      console.error('Failed to fetch room metrics:', error);
    }
  },

  fetchAgentPerformance: async () => {
    try {
      const response = await fetch(`${API_BASE}/api/analytics/agent-performance`);
      const agentPerformance = await response.json();
      set({ agentPerformance });
    } catch (error) {
      console.error('Failed to fetch agent performance:', error);
    }
  },

  fetchRoomInsights: async (roomId) => {
    try {
      const response = await fetch(`${API_BASE}/api/analytics/room-insights/${roomId}`);
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch room insights:', error);
      return null;
    }
  },
}));