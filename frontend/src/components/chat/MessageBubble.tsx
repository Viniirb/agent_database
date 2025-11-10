import { motion } from 'framer-motion';
import { Bot, User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Message } from '../../types';

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble = ({ message }: MessageBubbleProps) => {
  const isUser = message.role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.3 }}
      className={`flex gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar */}
      <div className={`
        w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0
        ${isUser 
          ? 'bg-accent-blue' 
          : 'bg-gradient-to-br from-accent-purple to-accent-blue'
        }
      `}>
        {isUser ? (
          <User size={20} className="text-white" />
        ) : (
          <Bot size={20} className="text-white" />
        )}
      </div>

      {/* Message Content */}
      <motion.div
        whileHover={{ scale: 1.01 }}
        className={`
          flex-1 max-w-2xl card p-4
          ${isUser ? 'bg-accent-blue/10 border-accent-blue/20' : ''}
        `}
      >
        <div className="prose prose-invert prose-sm max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {message.content}
          </ReactMarkdown>
        </div>

        {/* Timestamp */}
        <div className={`
          mt-2 text-xs text-foreground-subtle
          ${isUser ? 'text-right' : 'text-left'}
        `}>
          {new Date(message.timestamp).toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit'
          })}
        </div>
      </motion.div>
    </motion.div>
  );
};