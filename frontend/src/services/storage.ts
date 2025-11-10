import type { Conversation, AppSettings } from '../types';

const STORAGE_KEYS = {
  CONVERSATIONS: 'agent-db-conversations',
  ACTIVE_CONVERSATION: 'agent-db-active-conversation',
  SETTINGS: 'agent-db-settings',
  THEME: 'agent-db-theme',
} as const;

class StorageService {
  // Conversas
  getConversations(): Conversation[] {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.CONVERSATIONS);
      if (!data) return [];
      
      const parsed = JSON.parse(data);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return parsed.map((conv: any) => ({
        ...conv,
        createdAt: new Date(conv.createdAt),
        updatedAt: new Date(conv.updatedAt),
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        messages: conv.messages.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp),
        })),
      }));
    } catch (error) {
      console.error('Error loading conversations:', error);
      return [];
    }
  }

  saveConversation(conversation: Conversation): void {
    try {
      const conversations = this.getConversations();
      const index = conversations.findIndex(c => c.id === conversation.id);
      
      if (index >= 0) {
        conversations[index] = conversation;
      } else {
        conversations.push(conversation);
      }
      
      localStorage.setItem(STORAGE_KEYS.CONVERSATIONS, JSON.stringify(conversations));
    } catch (error) {
      console.error('Error saving conversation:', error);
    }
  }

  deleteConversation(id: string): void {
    try {
      const conversations = this.getConversations().filter(c => c.id !== id);
      localStorage.setItem(STORAGE_KEYS.CONVERSATIONS, JSON.stringify(conversations));
    } catch (error) {
      console.error('Error deleting conversation:', error);
    }
  }

  getActiveConversationId(): string | null {
    return localStorage.getItem(STORAGE_KEYS.ACTIVE_CONVERSATION);
  }

  setActiveConversationId(id: string): void {
    localStorage.setItem(STORAGE_KEYS.ACTIVE_CONVERSATION, id);
  }

  getSettings(): AppSettings {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.SETTINGS);
      return data ? JSON.parse(data) : {
        maxResults: 10,
        autoScroll: true,
        soundEnabled: false,
      };
    } catch (error) {
      console.error('Error loading settings:', error);
      return {
        maxResults: 10,
        autoScroll: true,
        soundEnabled: false,
      };
    }
  }

  saveSettings(settings: AppSettings): void {
    try {
      localStorage.setItem(STORAGE_KEYS.SETTINGS, JSON.stringify(settings));
    } catch (error) {
      console.error('Error saving settings:', error);
    }
  }

  getTheme(): 'light' | 'dark' {
    const theme = localStorage.getItem(STORAGE_KEYS.THEME);
    return (theme === 'light' || theme === 'dark') ? theme : 'dark';
  }

  setTheme(theme: 'light' | 'dark'): void {
    localStorage.setItem(STORAGE_KEYS.THEME, theme);
  }

  clearAll(): void {
    Object.values(STORAGE_KEYS).forEach(key => {
      localStorage.removeItem(key);
    });
  }
}

export const storageService = new StorageService();