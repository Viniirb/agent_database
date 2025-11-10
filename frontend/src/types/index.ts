export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  attachments?: Attachment[];
  codeBlocks?: CodeBlock[];
  isLoading?: boolean;
}

export interface Attachment {
  id: string;
  type: 'image' | 'pdf' | 'excel' | 'word' | 'code';
  name: string;
  url?: string;
  preview?: string;
  size?: number;
  language?: string;
}

export interface CodeBlock {
  id: string;
  language: string;
  code: string;
  filename?: string;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Collection {
  name: string;
  count: number;
  metadata?: {
    table_name?: string;
    columns?: string[];
    relationships?: string[];
  };
}

export interface DatabaseStats {
  total_collections: number;
  total_documents: number;
  collections: Collection[];
}

export interface SearchResult {
  id: string;
  content: string;
  metadata: Record<string, unknown>;
  distance: number;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  search_results?: SearchResult[];
  collections_searched?: string[];
  model_used?: string;
  token_optimization?: {
    compression_ratio?: number;
    tokens_saved?: number;
  };
  from_cache?: boolean;
}

export interface HealthCheck {
  status: 'healthy' | 'unhealthy';
  database: 'connected' | 'disconnected';
  collections: number;
  message?: string;
}

export interface ToonsStats {
  cache_hits: number;
  cache_misses: number;
  hit_rate: number;
  total_tokens_saved: number;
  average_compression_ratio: number;
}

export interface ConversationHistory {
  conversation_id: string;
  messages: Array<{
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
  }>;
}

export interface CacheStats {
  redis_connected: boolean;
  total_keys: number;
  memory_usage: string;
  conversations: number;
  cached_responses: number;
  uptime_seconds: number;
}

export interface SchemaInfo {
  collections: Array<{
    name: string;
    document_count: number;
    metadata_fields: string[];
  }>;
}

export interface AppSettings {
  maxResults: number;
  autoScroll: boolean;
  soundEnabled: boolean;
}