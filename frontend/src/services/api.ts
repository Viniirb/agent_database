import axios, { type AxiosInstance, AxiosError } from 'axios';
import type { ChatResponse, DatabaseStats, Collection, HealthCheck } from '../types';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor para tratamento de erros
    this.api.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // Health check
  async checkHealth(): Promise<HealthCheck> {
    try {
      const response = await this.api.get('/health');
      return response.data;
    } catch (error) {
      return {
        status: 'unhealthy',
        database: 'disconnected',
        collections: 0,
        message: `Failed to connect to server${error instanceof Error ? `: ${error.message}` : ''}`,
      };
    }
  }

  // Chat
  async sendMessage(
    message: string,
    conversationId?: string,
    collections?: string[],
    maxResults: number = 10
  ): Promise<ChatResponse> {
    const response = await this.api.post('/api/chat', {
      query: message,
      conversation_id: conversationId,
      max_results: maxResults,
      collections: collections && collections.length > 0 ? collections : undefined,
    });
    return response.data;
  }

  // Buscar coleções
  async getCollections(): Promise<Collection[]> {
    const response = await this.api.get('/api/collections');
    return response.data.collections || [];
  }

  // Estatísticas
  async getStats(): Promise<DatabaseStats> {
    const response = await this.api.get('/api/stats');
    return response.data;
  }
}

export const apiService = new ApiService();