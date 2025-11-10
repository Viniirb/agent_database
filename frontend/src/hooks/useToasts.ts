import { useEffect, useState } from 'react';

export type ToastType = 'error' | 'success' | 'info' | 'warning';

export interface Toast {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
}

let toastId = 0;
const listeners: Set<(toast: Toast) => void> = new Set();

export const showToast = (message: string, type: ToastType = 'info', duration = 3000) => {
  const id = `toast-${toastId++}`;
  const toast: Toast = { id, message, type, duration };
  listeners.forEach(listener => listener(toast));
};

export const useToasts = (maxToasts = 5) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  useEffect(() => {
    const handleShowToast = (toast: Toast) => {
      setToasts(prev => [toast, ...prev].slice(0, maxToasts));

      if (toast.duration && toast.duration > 0) {
        const timer = setTimeout(() => {
          setToasts(prev => prev.filter(t => t.id !== toast.id));
        }, toast.duration);

        return () => clearTimeout(timer);
      }
    };

    listeners.add(handleShowToast);
    return () => listeners.delete(handleShowToast);
  }, [maxToasts]);

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  return { toasts, removeToast };
};
