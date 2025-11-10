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

export interface ChatResponse {
  response: string;
  conversation_id: string;
  results?: SearchResult[];
}

export interface SearchResult {
  id: string;
  content: string;
  metadata: Record<string, unknown>;
  distance: number;
}

export interface HealthCheck {
  status: 'healthy' | 'unhealthy';
  database: 'connected' | 'disconnected';
  collections: number;
  message?: string;
}

export interface AppSettings {
  maxResults: number;
  selectedCollections: string[];
  autoScroll: boolean;
  soundEnabled: boolean;
}