import { useState, type KeyboardEvent, type FormEvent } from 'react';
import { motion } from 'framer-motion';
import { Send, Paperclip } from 'lucide-react';
import { Button } from '../ui/Button';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export const ChatInput = ({ onSend, disabled }: ChatInputProps) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className="flex items-end gap-2">
        {/* Textarea */}
        <div className="flex-1 relative">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Digite sua pergunta... (Shift+Enter para nova linha)"
            disabled={disabled}
            rows={1}
            className="
              w-full px-4 py-3 pr-12 rounded-xl resize-none
              bg-gray-800 border border-gray-700
              text-gray-100 placeholder:text-gray-600
              focus:border-blue-500 focus:ring-1 focus:ring-blue-500/20
              transition-all duration-200
              disabled:opacity-50 disabled:cursor-not-allowed
              max-h-32 text-sm
            "
            style={{
              height: 'auto',
              minHeight: '44px',
            }}
            onInput={(e) => {
              const target = e.target as HTMLTextAreaElement;
              target.style.height = 'auto';
              target.style.height = `${Math.min(target.scrollHeight, 128)}px`;
            }}
          />
          
          <motion.button
            type="button"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            className="absolute right-3 bottom-3 p-1 hover:bg-gray-700 rounded transition-colors"
          >
            <Paperclip size={16} className="text-gray-500" />
          </motion.button>
        </div>

        {/* Send Button */}
        <Button
          type="submit"
          disabled={!message.trim() || disabled}
          isLoading={disabled}
          className="h-10 w-10 !p-0 rounded-xl bg-blue-600 hover:bg-blue-700 text-white"
        >
          {!disabled && <Send size={16} />}
        </Button>
      </div>
    </form>
  );
};