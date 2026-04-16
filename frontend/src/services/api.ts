import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
});

// Add a request interceptor to include the JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Add a response interceptor to handle 401 Unauthorized
api.interceptors.response.use((response) => {
  return response;
}, (error) => {
  if (error.response?.status === 401) {
    localStorage.removeItem('token');
    window.location.href = '/login';
  }
  return Promise.reject(error);
});

export const authApi = {
  login: (formData: FormData) => api.post('/auth/login/access-token', formData),
  register: (userData: any) => api.post('/auth/register', userData),
  getMe: () => api.get('/users/me'),
};

export const simulationApi = {
  getState: () => api.get('/simulation/state'),
  step: (action: string, amount: number) => api.post('/simulation/step', { action, amount }),
  reset: (task: string, difficulty: string, seed?: number) => 
    api.post('/simulation/reset', { task, difficulty, seed }),
  getHistory: () => api.get('/simulation/history'),
  getLeaderboard: () => api.get('/simulation/leaderboard'),
};

export default api;
