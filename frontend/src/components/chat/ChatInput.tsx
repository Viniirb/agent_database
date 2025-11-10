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
            placeholder="Digite sua mensagem... (Shift+Enter para nova linha)"
            disabled={disabled}
            rows={1}
            className="
              w-full px-4 py-3 pr-12 rounded-input resize-none
              bg-background-card border border-border
              text-foreground placeholder:text-foreground-subtle
              focus:border-accent-blue focus:ring-2 focus:ring-accent-blue/20
              transition-all duration-200
              disabled:opacity-50 disabled:cursor-not-allowed
              max-h-32
            "
            style={{
              height: 'auto',
              minHeight: '48px',
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
            className="absolute right-3 bottom-3 p-1 hover:bg-background-hover rounded-lg transition-colors"
          >
            <Paperclip size={18} className="text-foreground-muted" />
          </motion.button>
        </div>

        {/* Send Button */}
        <Button
          type="submit"
          disabled={!message.trim() || disabled}
          isLoading={disabled}
          className="h-12 w-12 !p-0"
        >
          <Send size={18} />
        </Button>
      </div>
    </form>
  );
};