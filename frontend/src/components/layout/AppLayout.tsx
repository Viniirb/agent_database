import type { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

interface AppLayoutProps {
  children: ReactNode;
}

export const AppLayout = ({ children }: AppLayoutProps) => {
  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <motion.aside
        initial={{ x: -300, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        className="w-80 border-r border-border flex-shrink-0 hidden lg:block"
      >
        <Sidebar />
      </motion.aside>

      <div className="flex-1 flex flex-col min-w-0">
        <Header />

        <main className="flex-1 overflow-hidden">
          {children}
        </main>
      </div>
    </div>
  );
};