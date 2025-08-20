import axios from 'axios';
import { TranslationRequest, TranslationResponse, Lesson, User, UserProgress } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const languageApi = {
  getSupportedLanguages: async () => {
    const response = await api.get('/api/languages');
    return response.data;
  },

  translateText: async (request: TranslationRequest): Promise<TranslationResponse> => {
    const response = await api.post('/api/translate', request);
    return response.data;
  },

  sendMessage: async (message: string, languageCode: string, userId?: number) => {
    const response = await api.post('/api/conversation', {
      message,
      language_code: languageCode,
      user_id: userId
    });
    
    return response.data;
  },

  generateLesson: async (languageCode: string, level: string, topic?: string): Promise<Lesson> => {
    const response = await api.post('/lesson', {
      language_code: languageCode,
      level,
      topic,
    });
    return response.data;
  },

  createUser: async (username: string, email: string): Promise<User> => {
    const response = await api.post('/users', { username, email });
    return response.data;
  },

  getUserProgress: async (userId: number): Promise<UserProgress> => {
    const response = await api.get(`/users/${userId}/progress`);
    return response.data;
  },
};

export default api;
