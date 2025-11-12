import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { RefreshCw } from 'lucide-react';
import type { Message } from '../../types';
import type { ExtendedMessage } from '../../hooks/useChat';

interface MessageBubbleProps {
  message: Message;
  onRetry?: (content: string) => void;
}

export const MessageBubble = ({ message, onRetry }: MessageBubbleProps) => {
  const isUser = message.role === 'user';
  const extendedMessage = message as ExtendedMessage;
  const hasError = extendedMessage.hasError;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -10, scale: 0.95 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar com glow */}
      <motion.div
        whileHover={{ scale: 1.1 }}
        className={`
          w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-base
          ${isUser
            ? 'bg-gradient-to-br from-accent-blue to-accent-purple shadow-glow-blue'
            : 'glass-card border-2 border-accent-purple/30 shadow-glow-purple'
          }
        `}
      >
        {isUser ? '👤' : '🤖'}
      </motion.div>

      {/* Message Card - Glass */}
      <div className={`flex-1 max-w-3xl ${isUser ? 'text-right' : 'text-left'}`}>
        <motion.div
          whileHover={{ y: -2, scale: 1.005 }}
          transition={{ duration: 0.2 }}
          className={`
            inline-block px-4 py-3 rounded-2xl text-sm leading-relaxed
            transition-all duration-300 relative
            ${isUser
              ? 'bg-gradient-to-br from-accent-blue to-accent-purple text-white rounded-tr-sm shadow-glow-blue'
              : 'glass-card glass-card-hover text-foreground rounded-tl-sm'
            }
          `}
        >
          <div className={isUser ? '' : 'prose prose-invert max-w-none'}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          </div>
        </motion.div>

        {/* Timestamp com badge e botão de reenvio */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.15 }}
          className={`flex items-center gap-2 mt-1.5 px-1 ${isUser ? 'justify-end' : 'justify-start'}`}
        >
          <span className="text-xs text-foreground-subtle">
            {new Date(message.timestamp).toLocaleTimeString('pt-BR', {
              hour: '2-digit',
              minute: '2-digit'
            })}
          </span>
          {!isUser && !hasError && (
            <span className="badge badge-purple">
              AI
            </span>
          )}
          {hasError && extendedMessage.originalUserMessage && onRetry && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onRetry(extendedMessage.originalUserMessage!)}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg glass-card hover:bg-accent-blue/10 hover:border-accent-blue/40 transition-all duration-300 group"
            >
              <RefreshCw size={12} className="text-accent-blue group-hover:rotate-180 transition-transform duration-300" />
              <span className="text-xs text-accent-blue">Reenviar</span>
            </motion.button>
          )}
        </motion.div>
      </div>
    </motion.div>
  );
};