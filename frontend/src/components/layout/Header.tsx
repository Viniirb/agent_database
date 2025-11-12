import { motion } from 'framer-motion';
import { Database, Zap, Plus } from 'lucide-react';
import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogBody,
  DialogClose
} from '@/components/ui';
import { useActiveConversation } from '@/contexts/ChatContext';
import { SessionStats } from '@/components/chat/SessionStats';
import { storageService } from '@/services/storage';
import type { ExtendedMessage } from '@/hooks/useChat';

interface HeaderProps {
  onNewChat: () => void;
}

export const Header = ({ onNewChat }: HeaderProps) => {
  const [showStats, setShowStats] = useState(false);
  const { activeConversationId } = useActiveConversation();

  const conversations = storageService.getConversations();
  const activeConversation = conversations.find(c => c.id === activeConversationId);
  const activeMessages = (activeConversation?.messages || []) as ExtendedMessage[];

  return (
    <>
      <header className="backdrop-blur-glass bg-background-card/30 content-layer relative z-30" style={{ boxShadow: '0 4px 24px rgba(0, 0, 0, 0.3)' }}>
        <div className="h-16 flex items-center justify-between px-8">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center gap-3"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-blue to-accent-purple flex items-center justify-center shadow-glow-blue">
              <Database size={20} className="text-white" />
            </div>
            <div>
              <div className="text-xl font-semibold text-gradient tracking-wide">
                Assistente de IA
              </div>
              <p className="text-xs text-foreground-muted">
                Assistente que traduz linguagem natural em consultas SQL Server
              </p>
            </div>
          </motion.div>

          {/* Botões de ação */}
          <div className="flex items-center gap-2">
            {/* Botão de Nova Conversa */}
            <motion.button
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.95 }}
              onClick={onNewChat}
              className="flex items-center gap-2 px-3 py-2 rounded-xl glass-card hover:bg-accent-purple/10 hover:border-accent-purple/40 hover:shadow-glow-purple transition-all duration-300 group"
            >
              <motion.div
                whileHover={{ rotate: 90 }}
                transition={{ duration: 0.3 }}
              >
                <Plus size={18} className="text-accent-purple group-hover:text-accent-purple/90" />
              </motion.div>
              <span className="text-sm text-foreground group-hover:text-accent-purple">Nova Conversa</span>
            </motion.button>

            {/* Botão de Estatísticas */}
            <motion.button
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowStats(true)}
              className="flex items-center gap-2 px-3 py-2 rounded-xl glass-card hover:bg-accent-blue/10 hover:border-accent-blue/40 hover:shadow-glow-blue transition-all duration-300 group"
            >
              <motion.div
                whileHover={{ rotate: -15, scale: 1.1 }}
                transition={{ duration: 0.3 }}
              >
                <Zap size={18} className="text-accent-blue group-hover:text-accent-blue/90" />
              </motion.div>
              <span className="text-sm text-foreground group-hover:text-accent-blue">Estatísticas</span>
            </motion.button>
          </div>
        </div>
      </header>

      {/* Dialog de Estatísticas */}
      <Dialog open={showStats} onOpenChange={setShowStats}>
        <DialogContent>
          <DialogClose onClick={() => setShowStats(false)} />
          <DialogHeader>
            <DialogTitle>Estatísticas da Sessão</DialogTitle>
            <DialogDescription>
              Métricas detalhadas da conversa ativa
            </DialogDescription>
          </DialogHeader>
          <DialogBody>
            {activeConversationId ? (
              <SessionStats messages={activeMessages} currentConversationId={activeConversationId} />
            ) : (
              <p className="text-sm text-foreground-muted text-center py-8">
                Nenhuma conversa ativa
              </p>
            )}
          </DialogBody>
        </DialogContent>
      </Dialog>
    </>
  );
}