import { useState, useCallback, useEffect } from 'react';
import { apiService } from '../services/api';
import { storageService } from '../services/storage';
import { generateId } from '../utils/uuid';
import { showToast } from './useToasts';
import type { Message, Conversation, Attachment, ChatResponse } from '../types';

export interface ExtendedMessage extends Message {
  responseData?: ChatResponse;
}

export const useChat = (conversationId?: string) => {
  const [messages, setMessages] = useState<ExtendedMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentConversationId, setCurrentConversationId] = useState<string>(
    conversationId || generateId()
  );

  useEffect(() => {
    const conversations = storageService.getConversations();
    const conversation = conversations.find(c => c.id === currentConversationId);
    if (conversation) {
      setMessages(conversation.messages as ExtendedMessage[]);
    }
  }, [currentConversationId]);

  // Salvar no localStorage quando mensagens mudam
  useEffect(() => {
    if (messages.length > 0) {
      const conversation: Conversation = {
        id: currentConversationId,
        title: messages[0]?.content.slice(0, 50) || 'Nova Conversa',
        messages: messages.map(({ responseData, ...msg }) => msg),
        createdAt: new Date(),
        updatedAt: new Date(),
      };
      storageService.saveConversation(conversation);
    }
  }, [messages, currentConversationId]);

  const sendMessage = useCallback(async (
    content: string,
    attachments?: Attachment[]
  ) => {
    const userMessage: ExtendedMessage = {
      id: generateId(),
      role: 'user',
      content,
      timestamp: new Date(),
      attachments,
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const settings = storageService.getSettings();
      const response = await apiService.sendMessage(
        content,
        currentConversationId,
        undefined, // Deixar o IA decidir as coleções
        settings.maxResults
      );

      const assistantMessage: ExtendedMessage = {
        id: generateId(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        responseData: response,
      };

      setMessages(prev => [...prev, assistantMessage]);
      showToast('Resposta recebida!', 'success', 2000);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Falha ao enviar mensagem';
      setError(errorMessage);
      showToast(errorMessage, 'error', 4000);
      
      const errorMsg: ExtendedMessage = {
        id: generateId(),
        role: 'assistant',
        content: `❌ Erro: ${errorMessage}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  }, [currentConversationId]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    const newId = generateId();
    setCurrentConversationId(newId);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
    conversationId: currentConversationId,
  };
};