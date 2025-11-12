import { useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2, MessageCircle, Sparkles } from 'lucide-react';
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
    <div className="h-full flex flex-col content-layer relative">
      {/* Messages Area - com padding bottom para overlay */}
      <div
        className="flex-1 overflow-y-auto px-4 py-5 pb-32"
        style={{
          scrollbarWidth: 'thin',
          scrollbarColor: 'rgba(120, 120, 120, 0.5) transparent',
        }}
      >
        <div className="max-w-4xl mx-auto space-y-4">
          {/* Empty State - quando não há conversa ativa */}
          {!activeConversationId && messages.length === 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
              className="flex items-center justify-center min-h-[50vh]"
            >
              <div className="text-center max-w-md">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.1, type: "spring", stiffness: 200 }}
                  className="relative inline-block mb-6"
                >
                  <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-accent-blue/20 to-accent-purple/20 border border-accent-blue/30 flex items-center justify-center">
                    <MessageCircle size={36} className="text-accent-blue" />
                  </div>
                  <motion.div
                    animate={{ 
                      scale: [1, 1.2, 1],
                      rotate: [0, 10, -10, 0]
                    }}
                    transition={{ 
                      duration: 2,
                      repeat: Infinity,
                      repeatDelay: 3
                    }}
                    className="absolute -top-1 -right-1"
                  >
                    <Sparkles size={20} className="text-accent-purple" />
                  </motion.div>
                </motion.div>
                
                <motion.h3
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="text-xl font-semibold text-foreground mb-2"
                >
                  Nenhuma conversa ativa
                </motion.h3>
                
                <motion.p
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="text-sm text-foreground-muted"
                >
                  Clique em <span className="text-accent-purple font-medium">"Nova Conversa"</span> no topo para começar
                </motion.p>
              </div>
            </motion.div>
          )}

          <AnimatePresence mode="popLayout">
            {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
            {messages.map((message: any) => (
              <MessageBubble
                key={message.id}
                message={message}
                onRetry={sendMessage}
              />
            ))}
          </AnimatePresence>

          {/* Loading Indicator */}
          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-3 text-foreground-muted text-sm ml-11"
            >
              <div className="flex items-center gap-1">
                <motion.div
                  animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
                  transition={{ repeat: Infinity, duration: 1, delay: 0 }}
                  className="w-2 h-2 rounded-full bg-accent-blue"
                />
                <motion.div
                  animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
                  transition={{ repeat: Infinity, duration: 1, delay: 0.2 }}
                  className="w-2 h-2 rounded-full bg-accent-purple"
                />
                <motion.div
                  animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
                  transition={{ repeat: Infinity, duration: 1, delay: 0.4 }}
                  className="w-2 h-2 rounded-full bg-accent-pink"
                />
              </div>
              <span className="text-foreground-muted">Pensando...</span>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area - Overlay fixo com blur intenso */}
      <div
        className="absolute bottom-0 left-0 right-0 p-4 backdrop-blur-glass bg-background-card/50 z-20"
        style={{
          boxShadow: '0 -8px 32px rgba(0, 0, 0, 0.4)',
        }}
      >
        <div className="max-w-4xl mx-auto">
          <ChatInput onSend={sendMessage} disabled={isLoading} />
        </div>
      </div>
    </div>
  );
};