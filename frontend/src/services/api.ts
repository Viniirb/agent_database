import axios, { type AxiosInstance, AxiosError } from 'axios';
import type { 
  ChatResponse, 
  DatabaseStats, 
  Collection, 
  HealthCheck,
  ToonsStats,
  ConversationHistory,
  CacheStats,
  SchemaInfo
} from '../types';

interface ChatRequest {
  message: string;
  conversation_id?: string;
  search_collections?: string[];
  max_results?: number;
}

interface ToonsStatsResponse {
  cache_hits: number;
  cache_misses: number;
  hit_rate: number;
  total_tokens_saved: number;
  average_compression_ratio: number;
}

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
      timeout: 60000, // 60 segundos para aguardar fallback do backend
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

  // ===== CHAT & CONVERSATIONS =====
  
  async sendMessage(
    message: string,
    conversationId?: string,
    collections?: string[],
    maxResults: number = 10
  ): Promise<ChatResponse> {
    const payload: ChatRequest = {
      message: message,
      conversation_id: conversationId,
      max_results: maxResults,
    };
    
    if (collections && collections.length > 0) {
      payload.search_collections = collections;
    }
    
    // Timeout maior para mensagens de chat (90 segundos)
    // para aguardar fallback entre modelos no backend
    const response = await this.api.post('/api/chat', payload, {
      timeout: 90000 // 90 segundos
    });
    return response.data;
  }

  async getConversationHistory(conversationId: string): Promise<ConversationHistory> {
    const response = await this.api.get(`/api/conversations/${conversationId}/history`);
    return response.data;
  }

  async deleteConversation(conversationId: string): Promise<void> {
    await this.api.delete(`/api/conversations/${conversationId}`);
  }

  // ===== COLLECTIONS & SCHEMA =====
  
  async getCollections(): Promise<Collection[]> {
    const response = await this.api.get('/api/collections');
    return response.data.collections || [];
  }

  async getCollectionInfo(collectionName: string): Promise<Collection> {
    const response = await this.api.get(`/api/collections/${collectionName}`);
    return response.data;
  }

  async getSchema(): Promise<SchemaInfo> {
    const response = await this.api.get('/api/schema');
    return response.data;
  }

  // ===== STATISTICS =====
  
  async getStats(): Promise<DatabaseStats> {
    const response = await this.api.get('/api/stats');
    return response.data;
  }

  // ===== TOONS TOKEN OPTIMIZATION =====
  
  async getToonsStats(): Promise<ToonsStatsResponse> {
    const response = await this.api.get('/api/toons-stats');
    return response.data;
  }

  async resetToonsStats(): Promise<{ message: string }> {
    const response = await this.api.post('/api/toons-reset');
    return response.data;
  }

  async clearToonsCache(): Promise<{ message: string }> {
    const response = await this.api.delete('/api/toons-cache');
    return response.data;
  }

  // ===== REDIS CACHE =====
  
  async getCacheStats(): Promise<CacheStats> {
    const response = await this.api.get('/api/cache-stats');
    return response.data;
  }

  async clearCache(): Promise<{ message: string }> {
    const response = await this.api.post('/api/cache-clear');
    return response.data;
  }
}

export const apiService = new ApiService();