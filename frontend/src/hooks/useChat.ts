import { useState, useCallback, useEffect } from 'react';
import { apiService } from '../services/api';
import { storageService } from '../services/storage';
import { generateId } from '../utils/uuid';
import { showToast } from './useToasts';
import type { Message, Conversation, Attachment, ChatResponse } from '../types';

export interface ExtendedMessage extends Message {
  responseData?: ChatResponse;
  hasError?: boolean;
  originalUserMessage?: string;
}

export const useChat = (conversationId?: string) => {
  const [messages, setMessages] = useState<ExtendedMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentConversationId, setCurrentConversationId] = useState<string>(
    conversationId || generateId()
  );
  const [hasUserMessage, setHasUserMessage] = useState(false);

  useEffect(() => {
    const conversations = storageService.getConversations();
    const conversation = conversations.find(c => c.id === currentConversationId);
    if (conversation) {
      setMessages(conversation.messages as ExtendedMessage[]);
      // Se a conversa já existe, significa que já tem mensagem do usuário
      setHasUserMessage(true);
    } else {
      // Adiciona mensagem de boas-vindas automática para nova conversa
      const greetingMessage: ExtendedMessage = {
        id: generateId(),
        role: 'assistant',
        content: 'Olá! Sou o Assistente de Banco de Dados. Posso ajudá-lo a consultar informações do seu banco de dados usando linguagem natural. Como posso ajudar?',
        timestamp: new Date(),
      };
      setMessages([greetingMessage]);
      setHasUserMessage(false);
    }
  }, [currentConversationId]);

  // Salvar no localStorage apenas após a primeira mensagem do usuário
  useEffect(() => {
    if (messages.length > 0 && hasUserMessage) {
      // Encontra a primeira mensagem do usuário para usar como título
      const firstUserMessage = messages.find(m => m.role === 'user');
      const title = firstUserMessage?.content.slice(0, 50) || 'Nova Conversa';

      const conversation: Conversation = {
        id: currentConversationId,
        title,
        messages: messages.map(({ responseData, ...msg }) => msg),
        createdAt: new Date(),
        updatedAt: new Date(),
      };
      storageService.saveConversation(conversation);
    }
  }, [messages, currentConversationId, hasUserMessage]);

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
    setHasUserMessage(true); // Marca que agora tem mensagem do usuário
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
        hasError: true,
        originalUserMessage: content,
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  }, [currentConversationId]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setHasUserMessage(false);
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