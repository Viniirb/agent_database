import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import type { ReactNode } from 'react';

interface BadgeProps {
  children: ReactNode;
  variant?: 'default' | 'blue' | 'purple' | 'success' | 'warning' | 'error';
  className?: string;
}

export const Badge = ({ children, variant = 'default', className }: BadgeProps) => {
  const variantClasses = {
    default: 'badge',
    blue: 'badge badge-blue',
    purple: 'badge badge-purple',
    success: 'badge badge-blue',
    warning: 'badge text-orange-400',
    error: 'badge text-red-400',
  };

  return (
    <motion.span
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className={cn(variantClasses[variant], className)}
    >
      {children}
    </motion.span>
  );
};