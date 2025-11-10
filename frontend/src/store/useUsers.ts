import { create } from 'zustand';

interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  assigned_rooms?: number[];
  created_at?: string;
}

interface UserStore {
  users: User[];
  currentUser: User | null;
  loading: boolean;
  fetchUsers: () => Promise<void>;
  createUser: (user: Omit<User, 'id'>) => Promise<void>;
  updateUser: (id: number, user: Partial<User>) => Promise<void>;
  deleteUser: (id: number) => Promise<void>;
  getCurrentUser: () => Promise<void>;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

export const useUsers = create<UserStore>((set, get) => ({
  users: [],
  currentUser: null,
  loading: false,

  fetchUsers: async () => {
    set({ loading: true });
    try {
      const response = await fetch(`${API_BASE}/api/users`);
      const users = await response.json();
      set({ users, loading: false });
    } catch (error) {
      console.error('Failed to fetch users:', error);
      set({ loading: false });
    }
  },

  getCurrentUser: async () => {
    try {
      const response = await fetch(`${API_BASE}/api/users/me`);
      if (response.ok) {
        const currentUser = await response.json();
        set({ currentUser });
      }
    } catch (error) {
      console.error('Failed to fetch current user:', error);
    }
  },

  createUser: async (userData) => {
    try {
      const response = await fetch(`${API_BASE}/api/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
      });
      const newUser = await response.json();
      set(state => ({ users: [...state.users, newUser] }));
    } catch (error) {
      console.error('Failed to create user:', error);
    }
  },

  updateUser: async (id, userData) => {
    try {
      const response = await fetch(`${API_BASE}/api/users/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
      });
      const updatedUser = await response.json();
      set(state => ({
        users: state.users.map(user => user.id === id ? updatedUser : user)
      }));
    } catch (error) {
      console.error('Failed to update user:', error);
    }
  },

  deleteUser: async (id) => {
    try {
      await fetch(`${API_BASE}/api/users/${id}`, {
        method: 'DELETE',
      });
      set(state => ({
        users: state.users.filter(user => user.id !== id)
      }));
    } catch (error) {
      console.error('Failed to delete user:', error);
    }
  },
}));