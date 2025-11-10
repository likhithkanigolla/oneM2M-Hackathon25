import { create } from 'zustand';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface DeviceService {
  name: string;
  active: boolean;
  inputSource: string;
  controlledBy?: string;
}

export interface Device {
  id: number;
  name: string;
  type: string;
  status: 'ON' | 'OFF';
  room_id: number;
  services: DeviceService[];
}

interface DeviceState {
  devices: Device[];
  setDevices: (devices: Device[]) => void;
  fetchRoomDevices: (roomId: number) => Promise<void>;
  createDevice: (device: Omit<Device, 'id'>) => Promise<void>;
  updateDevice: (id: number, device: Partial<Device>) => Promise<void>;
  deleteDevice: (id: number) => Promise<void>;
  updateDeviceStatus: (id: number, status: 'ON' | 'OFF') => Promise<void>;
}

export const useDevices = create<DeviceState>((set, get) => ({
  devices: [],
  setDevices: (devices) => set({ devices }),
  
  fetchRoomDevices: async (roomId: number) => {
    try {
      const token = JSON.parse(localStorage.getItem('smart-room-auth') || '{}')?.state?.token;
      const res = await fetch(`${API_BASE}/api/devices/room/${roomId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        },
      });
      if (!res.ok) throw new Error('Failed to fetch devices');
      const devices = await res.json();
      set({ devices });
    } catch (err) {
      console.error('fetchRoomDevices error', err);
    }
  },

  createDevice: async (device) => {
    try {
      const token = JSON.parse(localStorage.getItem('smart-room-auth') || '{}')?.state?.token;
      const res = await fetch(`${API_BASE}/api/devices/`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(device),
      });
      if (!res.ok) throw new Error('Failed to create device');
      const newDevice = await res.json();
      set((state) => ({
        devices: [...state.devices, newDevice],
      }));
    } catch (err) {
      console.error('createDevice error', err);
      throw err;
    }
  },

  updateDevice: async (id, device) => {
    try {
      const token = JSON.parse(localStorage.getItem('smart-room-auth') || '{}')?.state?.token;
      const res = await fetch(`${API_BASE}/api/devices/${id}`, {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(device),
      });
      if (!res.ok) throw new Error('Failed to update device');
      const updatedDevice = await res.json();
      set((state) => ({
        devices: state.devices.map((d) => (d.id === id ? updatedDevice : d)),
      }));
    } catch (err) {
      console.error('updateDevice error', err);
      throw err;
    }
  },

  deleteDevice: async (id) => {
    try {
      const token = JSON.parse(localStorage.getItem('smart-room-auth') || '{}')?.state?.token;
      const res = await fetch(`${API_BASE}/api/devices/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        },
      });
      if (!res.ok) throw new Error('Failed to delete device');
      set((state) => ({
        devices: state.devices.filter((d) => d.id !== id),
      }));
    } catch (err) {
      console.error('deleteDevice error', err);
      throw err;
    }
  },

  updateDeviceStatus: async (id, status) => {
    try {
      const token = JSON.parse(localStorage.getItem('smart-room-auth') || '{}')?.state?.token;
      const res = await fetch(`${API_BASE}/api/devices/${id}/status?status=${status}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`
        },
      });
      if (!res.ok) throw new Error('Failed to update device status');
      const updatedDevice = await res.json();
      set((state) => ({
        devices: state.devices.map((d) => (d.id === id ? updatedDevice : d)),
      }));
    } catch (err) {
      console.error('updateDeviceStatus error', err);
      throw err;
    }
  },
}));