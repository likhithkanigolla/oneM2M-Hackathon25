import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface User {
  id: number;
  username: string;
  full_name: string;
  role: string;
  assigned_rooms?: number[];
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
  
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  register: (username: string, password: string, fullName: string, role?: string) => Promise<void>;
  refreshToken: () => Promise<void>;
  clearError: () => void;
}

export const useAuth = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      loading: false,
      error: null,
      
      login: async (username: string, password: string) => {
        set({ loading: true, error: null });
        try {
          const res = await fetch(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
          });
          
          if (!res.ok) {
            const error = await res.json();
            throw new Error(error.detail || 'Login failed');
          }
          
          const data = await res.json();
          set({
            user: data.user,
            token: data.access_token,
            isAuthenticated: true,
            loading: false,
            error: null,
          });
        } catch (err) {
          console.error('Login error:', err);
          set({
            error: err instanceof Error ? err.message : 'Login failed',
            loading: false,
            isAuthenticated: false,
          });
          throw err;
        }
      },
      
      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null,
        });
      },
      
      register: async (username: string, password: string, fullName: string, role = 'operator') => {
        set({ loading: true, error: null });
        try {
          const res = await fetch(`${API_BASE}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              username,
              password,
              full_name: fullName,
              role,
            }),
          });
          
          if (!res.ok) {
            const error = await res.json();
            throw new Error(error.detail || 'Registration failed');
          }
          
          // Auto-login after registration
          await get().login(username, password);
        } catch (err) {
          console.error('Registration error:', err);
          set({
            error: err instanceof Error ? err.message : 'Registration failed',
            loading: false,
          });
          throw err;
        }
      },
      
      refreshToken: async () => {
        const { token } = get();
        if (!token) return;
        
        try {
          const res = await fetch(`${API_BASE}/api/auth/refresh-token`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });
          
          if (!res.ok) {
            throw new Error('Token refresh failed');
          }
          
          const data = await res.json();
          set({ token: data.access_token });
        } catch (err) {
          console.error('Token refresh error:', err);
          get().logout();
        }
      },
      
      clearError: () => set({ error: null }),
    }),
    {
      name: 'smart-room-auth',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);