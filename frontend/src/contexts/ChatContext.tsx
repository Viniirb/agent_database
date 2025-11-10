import { createContext, useContext, useState, type ReactNode } from 'react';

interface ChatContextType {
  activeConversationId: string | null;
  setActiveConversationId: (id: string | null) => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider = ({ children }: { children: ReactNode }) => {
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);

  return (
    <ChatContext.Provider value={{ activeConversationId, setActiveConversationId }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useActiveConversation = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useActiveConversation must be used within ChatProvider');
  }
  return context;
};
