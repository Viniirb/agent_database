import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MessageSquare,
  Trash2,
  Search,
  ChevronRight
} from 'lucide-react';
import { storageService } from '../../services/storage';
import { useActiveConversation } from '../../contexts/ChatContext';
import type { Conversation } from '../../types';

interface SidebarProps {
  isCollapsed: boolean;
  onToggle: () => void;
}

export const Sidebar = ({ isCollapsed, onToggle }: SidebarProps) => {
  const { activeConversationId, setActiveConversationId } = useActiveConversation();
  const [conversations, setConversations] = useState<Conversation[]>(
    storageService.getConversations()
  );
  const [searchTerm, setSearchTerm] = useState('');

  const filteredConversations = conversations.filter(conv =>
    conv.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleDeleteConversation = (id: string) => {
    storageService.deleteConversation(id);
    setConversations(storageService.getConversations());
  };

  return (
    <div className="relative h-full">
      <motion.div
        initial={false}
        animate={{ width: isCollapsed ? '80px' : '280px' }}
        transition={{ duration: 0.3 }}
        className="h-full flex flex-col backdrop-blur-glass bg-background-card/40 content-layer relative z-30"
        style={{
          boxShadow: '4px 0 24px rgba(0, 0, 0, 0.3)',
        }}
      >
      {/* Lista de conversas */}
      <div className="flex-1 overflow-y-auto p-3 pt-4 pb-24 space-y-2 scrollbar-hide">
        <AnimatePresence>
          {filteredConversations.map((conversation) => (
            <motion.div
              key={conversation.id}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, x: -100 }}
              whileHover={{ x: isCollapsed ? 0 : 2, scale: isCollapsed ? 1 : 1.01 }}
              className={`
                group relative p-3 rounded-xl cursor-pointer
                transition-all duration-200
                ${activeConversationId === conversation.id
                  ? 'glass-card shadow-glow-blue border border-accent-blue/30 bg-accent-blue/5'
                  : 'glass-card hover:bg-background-hover/50 border border-transparent'
                }
              `}
              onClick={() => setActiveConversationId(conversation.id)}
            >
              {isCollapsed ? (
                <div className="flex items-center justify-center">
                  <MessageSquare
                    size={18}
                    className="text-accent-blue"
                  />
                </div>
              ) : (
                <div className="flex items-start gap-3">
                  <MessageSquare
                    size={18}
                    className={`mt-0.5 flex-shrink-0 transition-colors ${
                      activeConversationId === conversation.id
                        ? 'text-accent-blue'
                        : 'text-accent-purple'
                    }`}
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground truncate leading-snug">
                      {conversation.title}
                    </p>
                    {/* Preview da última mensagem */}
                    {conversation.messages.length > 0 && (
                      <p className="text-xs text-foreground-muted mt-1 truncate opacity-75">
                        {conversation.messages[conversation.messages.length - 1].content.slice(0, 40)}
                        {conversation.messages[conversation.messages.length - 1].content.length > 40 ? '...' : ''}
                      </p>
                    )}
                    <p className="text-xs text-foreground-subtle mt-0.5">
                      {conversation.messages.length} mensagens
                    </p>
                  </div>

                  {/* Delete Button */}
                  <motion.button
                    whileHover={{ scale: 1.15 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteConversation(conversation.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 transition-all p-1.5 rounded-lg hover:bg-accent-pink/10 hover:text-accent-pink flex-shrink-0"
                  >
                    <Trash2 size={14} />
                  </motion.button>
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {filteredConversations.length === 0 && !isCollapsed && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12 px-4"
          >
            <div className="glass-card p-6 rounded-2xl">
              <MessageSquare size={40} className="mx-auto text-foreground-muted mb-3 opacity-50" />
              <p className="text-sm text-foreground-muted font-medium">
                {searchTerm ? 'Nenhuma conversa encontrada' : 'Nenhuma conversa ainda'}
              </p>
              <p className="text-xs text-foreground-muted mt-2 opacity-70">
                {searchTerm ? 'Tente outro termo de busca' : 'Clique em "Nova Conversa" para começar'}
              </p>
            </div>
          </motion.div>
        )}
      </div>

      {/* Seção de busca - overlay fixo no rodapé com blur background */}
      {!isCollapsed && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute bottom-0 left-0 right-0 px-4 py-4 backdrop-blur-glass bg-background-card/40 z-20"
          style={{
            boxShadow: '0 -4px 24px rgba(0, 0, 0, 0.3)',
          }}
        >
          <div className="relative">
            <Search
              size={16}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-foreground-muted"
            />
            <input
              type="text"
              placeholder="Buscar conversas..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input text-sm pl-9"
            />
          </div>
        </motion.div>
      )}
    </motion.div>

      {/* Botão de Toggle Flutuante - Estilo Shadcn UI */}
      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={onToggle}
        className="absolute top-1/2 -translate-y-1/2 -right-3 z-50 w-6 h-6 rounded-full glass-card shadow-lg hover:shadow-glow-blue transition-all duration-300 flex items-center justify-center group"
        style={{
          background: 'linear-gradient(135deg, rgba(30, 30, 30, 0.95), rgba(20, 20, 20, 0.95))',
          border: '1px solid rgba(255, 255, 255, 0.2)',
        }}
      >
        <motion.div
          animate={{ rotate: isCollapsed ? 0 : 180 }}
          transition={{ duration: 0.3 }}
        >
          <ChevronRight size={14} className="text-foreground group-hover:text-accent-blue transition-colors" />
        </motion.div>
      </motion.button>
    </div>
  );
};