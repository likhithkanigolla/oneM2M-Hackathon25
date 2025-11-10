import { create } from 'zustand';

// Debug: log environment variable
console.log('VITE_API_BASE_URL:', import.meta.env.VITE_API_BASE_URL);
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
console.log('Using API_BASE:', API_BASE);

export interface Device {
  name: string;
  type: string;
  status: 'ON' | 'OFF';
  services: Service[];
}

export interface Service {
  name: string;
  inputSource: string;
  active: boolean;
  controlledBy?: string;
}

export interface Room {
  id: number;
  name: string;
  gsi: number;
  aq: number;
  temp: number;
  occupancy: number;
  devices: Device[];
  position?: { x: number; y: number };
}

interface RoomState {
  rooms: Room[];
  selectedRoom: Room | null;
  setRooms: (rooms: Room[]) => void;
  selectRoom: (room: Room | null) => void;
  updateRoomDevice: (roomId: number, deviceName: string, status: 'ON' | 'OFF') => Promise<void>;
  fetchRooms: () => Promise<void>;
  createRoom: (room: Omit<Room, 'id' | 'devices'>) => Promise<void>;
  updateRoom: (id: number, room: Partial<Room>) => Promise<void>;
  deleteRoom: (id: number) => Promise<void>;
}

export const useRooms = create<RoomState>((set, get) => ({
  rooms: [],
  selectedRoom: null,
  setRooms: (rooms) => set({ rooms }),
  selectRoom: (room) => set({ selectedRoom: room }),
  updateRoomDevice: async (roomId, deviceName, status) => {
    try {
      const res = await fetch(`${API_BASE}/api/rooms/${roomId}/devices/${encodeURIComponent(deviceName)}?status=${encodeURIComponent(status)}`, {
        method: 'PATCH',
      });
      if (!res.ok) throw new Error('Failed to update device');
      const updatedRoom = await res.json();
      set((state) => ({
        rooms: state.rooms.map((r) => (r.id === updatedRoom.id ? updatedRoom : r)),
      }));
    } catch (err) {
      console.error('updateRoomDevice error', err);
    }
  },
  fetchRooms: async () => {
    try {
      console.log('Fetching rooms from:', `${API_BASE}/api/rooms/`);
      const res = await fetch(`${API_BASE}/api/rooms/`);
      console.log('Response status:', res.status);
      if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      const rooms = await res.json();
      console.log('Fetched rooms:', rooms.length);
      set({ rooms });
    } catch (err) {
      console.error('fetchRooms error', err);
    }
  },

  createRoom: async (room) => {
    try {
      const token = JSON.parse(localStorage.getItem('smart-room-auth') || '{}')?.state?.token;
      const res = await fetch(`${API_BASE}/api/rooms/`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(room),
      });
      if (!res.ok) throw new Error('Failed to create room');
      const newRoom = await res.json();
      set((state) => ({
        rooms: [...state.rooms, newRoom],
      }));
    } catch (err) {
      console.error('createRoom error', err);
      throw err;
    }
  },

  updateRoom: async (id, room) => {
    try {
      const token = JSON.parse(localStorage.getItem('smart-room-auth') || '{}')?.state?.token;
      const res = await fetch(`${API_BASE}/api/rooms/${id}`, {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(room),
      });
      if (!res.ok) throw new Error('Failed to update room');
      const updatedRoom = await res.json();
      set((state) => ({
        rooms: state.rooms.map((r) => (r.id === id ? updatedRoom : r)),
      }));
    } catch (err) {
      console.error('updateRoom error', err);
      throw err;
    }
  },

  deleteRoom: async (id) => {
    try {
      const token = JSON.parse(localStorage.getItem('smart-room-auth') || '{}')?.state?.token;
      const res = await fetch(`${API_BASE}/api/rooms/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        },
      });
      if (!res.ok) throw new Error('Failed to delete room');
      set((state) => ({
        rooms: state.rooms.filter((r) => r.id !== id),
      }));
    } catch (err) {
      console.error('deleteRoom error', err);
      throw err;
    }
  },
}));

// Simple initializer: fetch rooms on module load (optional)
async function initRooms() {
  try {
    console.log('Initializing rooms from:', `${API_BASE}/api/rooms/`);
    const res = await fetch(`${API_BASE}/api/rooms/`);
    if (!res.ok) {
      console.warn('Failed to fetch initial rooms:', res.status, res.statusText);
      return;
    }
    const rooms = await res.json();
    console.log('Initial rooms loaded:', rooms.length);
    const setState = (useRooms as any).getState().setRooms;
    setState(rooms);
  } catch (e) {
    console.warn('Could not fetch initial rooms from backend', e);
  }
}

// Don't auto-init on module load, let components handle it
// initRooms();
