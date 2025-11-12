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
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-end gap-3"
      >
        {/* Textarea com efeito glass */}
        <div className="flex-1 relative group">
          <div className="glass-card p-1 relative">
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Digite sua pergunta... (Shift+Enter para nova linha)"
              disabled={disabled}
              rows={1}
              className="
                w-full px-4 py-3 pr-14 rounded-xl resize-none
                bg-transparent border-none
                text-foreground placeholder:text-foreground-subtle
                focus:outline-none
                transition-all duration-300
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

            {/* Ícone de anexar - fixo no canto direito */}
            <motion.button
              type="button"
              whileHover={{ scale: 1.1, rotate: 15 }}
              whileTap={{ scale: 0.95 }}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-2 rounded-full glass-card hover:bg-accent-purple/10 hover:shadow-glow-purple transition-all duration-300 z-10"
            >
              <Paperclip size={18} className="text-accent-purple" />
            </motion.button>
          </div>
        </div>

        {/* Send Button - com gradiente e animação */}
        <Button
          type="submit"
          disabled={!message.trim() || disabled}
          isLoading={disabled}
          className="h-12 w-12 !p-0 rounded-xl btn-primary relative overflow-hidden group flex items-center justify-center"
        >
          {!disabled && (
            <motion.div
              whileHover={{ rotate: 45 }}
              transition={{ duration: 0.3 }}
            >
              <Send size={18} />
            </motion.div>
          )}
        </Button>
      </motion.div>
    </form>
  );
};