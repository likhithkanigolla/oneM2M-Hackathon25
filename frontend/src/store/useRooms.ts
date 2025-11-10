import { create } from 'zustand';

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
  updateRoomDevice: (roomId: number, deviceName: string, status: 'ON' | 'OFF') => void;
}

export const useRooms = create<RoomState>((set) => ({
  rooms: [
    {
      id: 1,
      name: "Conference Room A",
      gsi: 0.84,
      aq: 85,
      temp: 24,
      occupancy: 5,
      position: { x: 100, y: 100 },
      devices: [
        {
          name: "AC",
          type: "HVAC",
          status: "ON",
          services: [
            { name: "TempFromWeatherStation", inputSource: "Weather Node", active: true, controlledBy: "Claude" }
          ]
        },
        {
          name: "Light",
          type: "Lighting",
          status: "ON",
          services: [
            { name: "CameraLighting", inputSource: "Camera Sensor", active: true, controlledBy: "Gemini" }
          ]
        },
        {
          name: "Fan",
          type: "AirFlow",
          status: "ON",
          services: [
            { name: "CirculateAir", inputSource: "Occupancy Sensor", active: true, controlledBy: "Gemini" }
          ]
        },
        {
          name: "Camera",
          type: "Security",
          status: "ON",
          services: [
            { name: "Monitoring", inputSource: "Motion Sensor", active: true, controlledBy: "GPT" }
          ]
        }
      ]
    },
    {
      id: 2,
      name: "Conference Room B",
      gsi: 0.76,
      aq: 78,
      temp: 26,
      occupancy: 3,
      position: { x: 350, y: 100 },
      devices: [
        {
          name: "AC",
          type: "HVAC",
          status: "ON",
          services: [
            { name: "TempControl", inputSource: "Temp Sensor", active: true, controlledBy: "Claude" }
          ]
        },
        {
          name: "Light",
          type: "Lighting",
          status: "ON",
          services: [
            { name: "AutoLight", inputSource: "Light Sensor", active: true, controlledBy: "Gemini" }
          ]
        },
        {
          name: "Fan",
          type: "AirFlow",
          status: "OFF",
          services: [
            { name: "CirculateAir", inputSource: "Occupancy Sensor", active: false }
          ]
        }
      ]
    },
    {
      id: 3,
      name: "Office Space",
      gsi: 0.92,
      aq: 92,
      temp: 23,
      occupancy: 8,
      position: { x: 100, y: 300 },
      devices: [
        {
          name: "AC",
          type: "HVAC",
          status: "ON",
          services: [
            { name: "SmartTemp", inputSource: "Multi Sensor", active: true, controlledBy: "Claude" }
          ]
        },
        {
          name: "Light",
          type: "Lighting",
          status: "ON",
          services: [
            { name: "DynamicLighting", inputSource: "Occupancy + Light", active: true, controlledBy: "GPT" }
          ]
        },
        {
          name: "Fan",
          type: "AirFlow",
          status: "ON",
          services: [
            { name: "AirCirculation", inputSource: "AQ Sensor", active: true, controlledBy: "Gemini" }
          ]
        },
        {
          name: "Camera",
          type: "Security",
          status: "ON",
          services: [
            { name: "Monitoring", inputSource: "Motion Sensor", active: true, controlledBy: "GPT" }
          ]
        }
      ]
    },
    {
      id: 4,
      name: "Lab Room",
      gsi: 0.68,
      aq: 72,
      temp: 27,
      occupancy: 2,
      position: { x: 350, y: 300 },
      devices: [
        {
          name: "AC",
          type: "HVAC",
          status: "ON",
          services: [
            { name: "PrecisionTemp", inputSource: "Lab Sensor", active: true, controlledBy: "Claude" }
          ]
        },
        {
          name: "Light",
          type: "Lighting",
          status: "ON",
          services: [
            { name: "TaskLighting", inputSource: "Manual", active: true }
          ]
        },
        {
          name: "Fan",
          type: "AirFlow",
          status: "ON",
          services: [
            { name: "ExhaustControl", inputSource: "AQ Sensor", active: true, controlledBy: "Gemini" }
          ]
        }
      ]
    }
  ],
  selectedRoom: null,
  setRooms: (rooms) => set({ rooms }),
  selectRoom: (room) => set({ selectedRoom: room }),
  updateRoomDevice: (roomId, deviceName, status) =>
    set((state) => ({
      rooms: state.rooms.map((room) =>
        room.id === roomId
          ? {
              ...room,
              devices: room.devices.map((device) =>
                device.name === deviceName ? { ...device, status } : device
              ),
            }
          : room
      ),
    })),
}));
