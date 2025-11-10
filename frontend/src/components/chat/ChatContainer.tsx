import { useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import { MessageBubble } from './MessageBubble';
import { ChatInput } from './ChatInput';
import { useChat } from '../../hooks/useChat';
import { useActiveConversation } from '../../contexts/ChatContext';

export const ChatContainer = () => {
  const { activeConversationId } = useActiveConversation();
  const { messages, isLoading, sendMessage } = useChat(activeConversationId || undefined);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto scroll para última mensagem
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="h-full flex flex-col bg-gray-900">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-8">
        <div className="max-w-2xl mx-auto space-y-2">
          <AnimatePresence mode="popLayout">
            {messages.length === 0 ? (
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="text-center py-32"
              >
                <motion.div
                  animate={{ y: [0, -10, 0] }}
                  transition={{ repeat: Infinity, duration: 3 }}
                  className="text-5xl mb-6"
                >
                  💬
                </motion.div>
                <h2 className="text-2xl font-light text-gray-200 mb-2 tracking-tight">
                  Agent Database
                </h2>
                <p className="text-gray-500 text-sm">
                  Faça perguntas sobre seu banco de dados
                </p>
              </motion.div>
            ) : (
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              messages.map((message: any) => (
                <MessageBubble 
                  key={message.id} 
                  message={message}
                />
              ))
            )}
          </AnimatePresence>

          {/* Loading Indicator */}
          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-2 text-gray-400 text-sm ml-11"
            >
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ repeat: Infinity, duration: 1 }}
              >
                <Loader2 size={16} />
              </motion.div>
              <span>Pensando...</span>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-800 p-4 bg-gray-900">
        <div className="max-w-2xl mx-auto">
          <ChatInput onSend={sendMessage} disabled={isLoading} />
        </div>
      </div>
    </div>
  );
};