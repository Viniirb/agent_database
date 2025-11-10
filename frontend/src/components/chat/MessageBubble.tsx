import { motion } from 'framer-motion';
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
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className={`flex gap-3 mb-4 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar */}
      <div className={`
        w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold
        ${isUser 
          ? 'bg-blue-600 text-white' 
          : 'bg-gray-700 text-gray-200'
        }
      `}>
        {isUser ? '👤' : '🤖'}
      </div>

      {/* Message Card */}
      <div className={`flex-1 max-w-2xl ${isUser ? 'text-right' : 'text-left'}`}>
        <motion.div
          whileHover={{ y: -2 }}
          className={`
            inline-block px-5 py-3 rounded-2xl text-sm leading-relaxed
            transition-all duration-200
            ${isUser 
              ? 'bg-blue-600/90 text-white rounded-br-none shadow-lg' 
              : 'bg-gray-800/80 border border-gray-700 text-gray-100 rounded-bl-none shadow-md hover:shadow-lg hover:bg-gray-800'
            }
          `}
        >
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {message.content}
          </ReactMarkdown>
        </motion.div>

        {/* Timestamp */}
        <div className="text-xs text-gray-500 mt-1.5 px-1">
          {new Date(message.timestamp).toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit'
          })}
        </div>
      </div>
    </motion.div>
  );
};