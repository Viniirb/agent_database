import { useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import { MessageBubble } from './MessageBubble';
import { ChatInput } from './ChatInput';
import { useChat } from '../../hooks/useChat';

export const ChatContainer = () => {
  const { messages, isLoading, sendMessage } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto scroll para última mensagem
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="h-full flex flex-col">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-4xl mx-auto space-y-6">
          <AnimatePresence mode="popLayout">
            {messages.length === 0 ? (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="text-center py-20"
              >
                <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-accent-blue to-accent-purple flex items-center justify-center">
                  <span className="text-4xl">💬</span>
                </div>
                <h2 className="text-2xl font-semibold text-foreground mb-2">
                  Bem-vindo ao Agent Database
                </h2>
                <p className="text-foreground-muted">
                  Faça perguntas sobre seu banco de dados e receba respostas inteligentes
                </p>
              </motion.div>
            ) : (
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              messages.map((message: { id: any; }) => (
                <MessageBubble key={message.id} message={message} />
              ))
            )}
          </AnimatePresence>

          {/* Loading Indicator */}
          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-3 text-foreground-muted"
            >
              <Loader2 size={18} className="animate-spin" />
              <span className="text-sm">Pensando...</span>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-border p-4 bg-background/80 backdrop-blur-md">
        <div className="max-w-4xl mx-auto">
          <ChatInput onSend={sendMessage} disabled={isLoading} />
        </div>
      </div>
    </div>
  );
};