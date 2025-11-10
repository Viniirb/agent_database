import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Database, Zap, Search, Clock } from 'lucide-react';
import { useState } from 'react';
import type { ExtendedMessage } from '../../hooks/useChat';

interface SessionStatsProps {
  messages: ExtendedMessage[];
  currentConversationId: string;
}

export const SessionStats = ({ messages, currentConversationId }: SessionStatsProps) => {
  const [isOpen, setIsOpen] = useState(false);

  // Calcula estatísticas
  const totalMessages = messages.length;
  
  const totalTokensSaved = messages.reduce((acc, m) => {
    const tokens = m.responseData?.token_optimization?.tokens_saved || 0;
    return acc + tokens;
  }, 0);

  const totalDocumentsFound = messages.reduce((acc, m) => {
    const docs = m.responseData?.search_results?.length || 0;
    return acc + docs;
  }, 0);

  const collectionsUsed = new Set(
    messages
      .flatMap(m => m.responseData?.search_results || [])
      .map(r => r.content)
  );

  const sessionStartTime = messages[0]?.timestamp 
    ? new Date(messages[0].timestamp).toLocaleTimeString('pt-BR')
    : '--:--';

  return (
    <div className="border-t border-border pt-4 mt-4">
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-3 rounded-lg hover:bg-background-hover transition-colors group"
        whileHover={{ x: 4 }}
      >
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-accent-blue group-hover:scale-125 transition-transform" />
          <span className="text-sm font-medium text-foreground">
            Estatísticas da Sessão
          </span>
        </div>
        <motion.div
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <ChevronDown size={18} className="text-foreground-muted" />
        </motion.div>
      </motion.button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-4 py-3 space-y-2 bg-background-card/50 rounded-lg mt-2">
              {/* Total de Mensagens */}
              <div className="flex items-center justify-between text-sm">
                <span className="text-foreground-muted flex items-center gap-2">
                  <span className="text-lg">💬</span> Mensagens
                </span>
                <span className="text-foreground font-medium">{totalMessages}</span>
              </div>

              {/* Documentos Encontrados */}
              <div className="flex items-center justify-between text-sm">
                <span className="text-foreground-muted flex items-center gap-2">
                  <Search size={16} /> Documentos
                </span>
                <span className="text-foreground font-medium">{totalDocumentsFound}</span>
              </div>

              {/* Coleções Usadas */}
              <div className="flex items-center justify-between text-sm">
                <span className="text-foreground-muted flex items-center gap-2">
                  <Database size={16} /> Coleções
                </span>
                <span className="text-foreground font-medium">{collectionsUsed.size}</span>
              </div>

              {/* Tokens Economizados */}
              <div className="flex items-center justify-between text-sm">
                <span className="text-foreground-muted flex items-center gap-2">
                  <Zap size={16} /> Tokens Economizados
                </span>
                <span className="text-accent-green font-medium">{totalTokensSaved}</span>
              </div>

              {/* Hora de Início */}
              <div className="flex items-center justify-between text-sm">
                <span className="text-foreground-muted flex items-center gap-2">
                  <Clock size={16} /> Iniciado em
                </span>
                <span className="text-foreground font-medium">{sessionStartTime}</span>
              </div>

              {/* ID da Conversa */}
              <div className="flex items-center justify-between text-sm pt-2 border-t border-border mt-2">
                <span className="text-foreground-muted text-xs">ID da Sessão</span>
                <span className="text-foreground-muted text-xs font-mono truncate max-w-[150px]">
                  {currentConversationId.slice(0, 8)}...
                </span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
