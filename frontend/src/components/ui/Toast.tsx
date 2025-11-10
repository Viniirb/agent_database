import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle, CheckCircle, Info, X } from 'lucide-react';
import { useToasts, type ToastType } from '../../hooks/useToasts';

interface ToastContainerProps {
  maxToasts?: number;
}

export const ToastContainer = ({ maxToasts = 5 }: ToastContainerProps) => {
  const { toasts, removeToast } = useToasts(maxToasts);

  const getIcon = (type: ToastType) => {
    switch (type) {
      case 'error':
        return <AlertCircle size={18} className="text-accent-red" />;
      case 'success':
        return <CheckCircle size={18} className="text-accent-green" />;
      case 'warning':
        return <AlertCircle size={18} className="text-accent-yellow" />;
      default:
        return <Info size={18} className="text-accent-blue" />;
    }
  };

  const getBackgroundColor = (type: ToastType) => {
    switch (type) {
      case 'error':
        return 'bg-accent-red/10 border-accent-red/30';
      case 'success':
        return 'bg-accent-green/10 border-accent-green/30';
      case 'warning':
        return 'bg-accent-yellow/10 border-accent-yellow/30';
      default:
        return 'bg-accent-blue/10 border-accent-blue/30';
    }
  };

  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2">
      <AnimatePresence>
        {toasts.map((toast) => (
          <motion.div
            key={toast.id}
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.9 }}
            className={`
              flex items-center gap-3 px-4 py-3 rounded-lg border
              ${getBackgroundColor(toast.type)}
              text-foreground backdrop-blur-sm
              shadow-lg
            `}
          >
            {getIcon(toast.type)}
            <p className="text-sm flex-1">{toast.message}</p>
            <button
              onClick={() => removeToast(toast.id)}
              className="p-1 hover:bg-background/20 rounded transition-colors"
            >
              <X size={16} />
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};
