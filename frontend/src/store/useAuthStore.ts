import { create } from 'zustand';
import { authApi } from '../services/api';

interface AuthState {
  user: any | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (formData: FormData) => Promise<void>;
  register: (userData: any) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  login: async (formData) => {
    const res = await authApi.login(formData);
    const token = res.data.access_token;
    localStorage.setItem('token', token);
    const userRes = await authApi.getMe();
    set({ token, user: userRes.data, isAuthenticated: true });
  },
  register: async (userData) => {
    await authApi.register(userData);
  },
  logout: () => {
    localStorage.removeItem('token');
    set({ token: null, user: null, isAuthenticated: false });
  },
  checkAuth: async () => {
    try {
      const userRes = await authApi.getMe();
      set({ user: userRes.data, isAuthenticated: true });
    } catch (error) {
      localStorage.removeItem('token');
      set({ user: null, token: null, isAuthenticated: false });
    }
  },
}));
