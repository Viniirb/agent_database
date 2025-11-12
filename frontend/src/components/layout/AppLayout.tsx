import type { ReactNode } from 'react';
import { useState } from 'react';
import { motion } from 'framer-motion';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { useHealthCheck } from '../../hooks/useHealthCheck';

interface AppLayoutProps {
  children: ReactNode;
  onNewChat: () => void;
}

export const AppLayout = ({ children, onNewChat }: AppLayoutProps) => {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const { isOnline, isChecking } = useHealthCheck();

  const toggleSidebar = () => {
    setIsSidebarCollapsed(prev => !prev);
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar retrátil */}
      <motion.aside
        initial={{ x: -300, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        className="flex-shrink-0"
      >
        <Sidebar isCollapsed={isSidebarCollapsed} onToggle={toggleSidebar} />
      </motion.aside>

      {/* Main content área */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header onNewChat={onNewChat} />

        {/* Chat container com card flutuante */}
        <main className="flex-1 overflow-hidden px-32 py-6 content-layer">
          <div className="h-full glass-card shadow-glass">
            {children}
          </div>
        </main>

        {/* Footer - overlay com sombra */}
        <footer className="backdrop-blur-glass bg-background-card/30 content-layer relative z-30" style={{ boxShadow: '0 -4px 24px rgba(0, 0, 0, 0.3)' }}>
          <div className="px-8 py-3 flex items-center justify-between text-xs text-foreground-subtle">
            <div className="flex items-center gap-4">
              <span>Assistente v1.0</span>
              <span className="text-border-glass">|</span>
              <span>Powered by Gemini AI</span>
            </div>
            <div className="flex items-center gap-4">
              {isChecking ? (
                <span className="badge">Verificando...</span>
              ) : (
                <span className={`badge ${isOnline ? 'badge-green' : 'badge-purple'}`}>
                  {isOnline ? 'Online' : 'Offline'}
                </span>
              )}
              <span className="text-border-glass">|</span>
              <span>© 2025 Vinicius Rolim Barbosa - Todos os direitos reservados</span>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};