import { motion, AnimatePresence } from 'framer-motion';
import { useState, type ReactNode } from 'react';

interface TooltipProps {
  content: string;
  children: ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
  delay?: number;
}

export const Tooltip = ({
  content,
  children,
  position = 'top',
  delay = 300
}: TooltipProps) => {
  const [isVisible, setIsVisible] = useState(false);
  const [timeoutId, setTimeoutId] = useState<ReturnType<typeof setTimeout> | null>(null);

  const handleMouseEnter = () => {
    const id = setTimeout(() => setIsVisible(true), delay);
    setTimeoutId(id);
  };

  const handleMouseLeave = () => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    setIsVisible(false);
  };

  const positionClasses = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2',
  };

  return (
    <div
      className="relative inline-block"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {children}
      <AnimatePresence>
        {isVisible && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className={`absolute z-50 px-3 py-1.5 text-xs text-foreground bg-background-hover rounded-lg shadow-lg border border-border-glass whitespace-nowrap ${positionClasses[position]}`}
          >
            {content}
            {/* Arrow */}
            <div
              className={`absolute w-2 h-2 bg-background-hover border-border-glass rotate-45
                ${position === 'top' ? 'bottom-[-4px] left-1/2 -translate-x-1/2 border-b border-r' : ''}
                ${position === 'bottom' ? 'top-[-4px] left-1/2 -translate-x-1/2 border-t border-l' : ''}
                ${position === 'left' ? 'right-[-4px] top-1/2 -translate-y-1/2 border-t border-r' : ''}
                ${position === 'right' ? 'left-[-4px] top-1/2 -translate-y-1/2 border-b border-l' : ''}
              `}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};