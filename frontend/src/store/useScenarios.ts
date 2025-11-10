import { create } from 'zustand';

export interface Scenario {
  id: string;
  name: string;
  trigger: string;
  priority: 'Low' | 'Medium' | 'High' | 'Critical';
  active: boolean;
  affectedRooms: number[];
  impact: string;
}

interface ScenarioState {
  scenarios: Scenario[];
  activeScenarios: Scenario[];
  toggleScenario: (id: string) => void;
  addScenario: (scenario: Scenario) => void;
}

export const useScenarios = create<ScenarioState>((set, get) => ({
  scenarios: [
    {
      id: 'meeting',
      name: 'Meeting Priority',
      trigger: 'Calendar Event / Manual',
      priority: 'High',
      active: true,
      affectedRooms: [1, 2],
      impact: 'Comfort ↑',
    },
    {
      id: 'energy',
      name: 'Energy Shortage',
      trigger: 'Power < 70%',
      priority: 'Medium',
      active: true,
      affectedRooms: [1, 2, 3, 4],
      impact: 'Energy Efficiency ↑',
    },
    {
      id: 'aq-failure',
      name: 'AQ Sensor Failure',
      trigger: 'AQ Node Down',
      priority: 'High',
      active: false,
      affectedRooms: [3],
      impact: 'Reliability ↑',
    },
    {
      id: 'night',
      name: 'Night Mode',
      trigger: 'Time > 7PM',
      priority: 'Low',
      active: false,
      affectedRooms: [1, 2, 3, 4],
      impact: 'Lighting ↓',
    },
    {
      id: 'occupancy',
      name: 'Occupancy Spike',
      trigger: 'Occupancy > 10',
      priority: 'Medium',
      active: false,
      affectedRooms: [3],
      impact: 'Cooling ↑',
    },
    {
      id: 'aq-drop',
      name: 'Air Quality Drop',
      trigger: 'AQ > 120',
      priority: 'Critical',
      active: false,
      affectedRooms: [],
      impact: 'Filter Mode ON',
    },
  ],
  get activeScenarios() {
    return get().scenarios.filter((s) => s.active);
  },
  toggleScenario: (id) =>
    set((state) => ({
      scenarios: state.scenarios.map((scenario) =>
        scenario.id === id ? { ...scenario, active: !scenario.active } : scenario
      ),
    })),
  addScenario: (scenario) =>
    set((state) => ({
      scenarios: [...state.scenarios, scenario],
    })),
}));
