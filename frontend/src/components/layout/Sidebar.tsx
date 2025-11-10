import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Plus, 
  MessageSquare, 
  Trash2, 
  Search,
  Database,
  Settings
} from 'lucide-react';
import { storageService } from '../../services/storage';
import type { Conversation } from '../../types';

export const Sidebar = () => {
  const [conversations, setConversations] = useState<Conversation[]>(
    storageService.getConversations()
  );
  const [searchTerm, setSearchTerm] = useState('');
  const [activeId, setActiveId] = useState<string | null>(
    storageService.getActiveConversationId()
  );

  const filteredConversations = conversations.filter(conv =>
    conv.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleNewChat = () => {
    console.log('New chat');
  };

  const handleDeleteConversation = (id: string) => {
    storageService.deleteConversation(id);
    setConversations(storageService.getConversations());
  };

  return (
    <div className="h-full flex flex-col bg-background">
      <div className="p-4 border-b border-border">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleNewChat}
          className="w-full btn btn-primary flex items-center justify-center gap-2 py-3"
        >
          <Plus size={20} />
          <span>Nova Conversa</span>
        </motion.button>

        <div className="mt-4 relative">
          <Search 
            size={18} 
            className="absolute left-3 top-1/2 -translate-y-1/2 text-foreground-subtle" 
          />
          <input
            type="text"
            placeholder="Buscar conversas..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input pl-10 py-2 text-sm"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        <AnimatePresence>
          {filteredConversations.map((conversation) => (
            <motion.div
              key={conversation.id}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, x: -100 }}
              whileHover={{ x: 4 }}
              className={`
                group relative p-3 rounded-lg cursor-pointer
                transition-colors duration-200
                ${activeId === conversation.id 
                  ? 'bg-background-hover border border-border-hover' 
                  : 'hover:bg-background-card'
                }
              `}
              onClick={() => setActiveId(conversation.id)}
            >
              <div className="flex items-start gap-3">
                <MessageSquare 
                  size={18} 
                  className="text-foreground-muted mt-1 flex-shrink-0" 
                />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-foreground truncate">
                    {conversation.title}
                  </p>
                  <p className="text-xs text-foreground-subtle mt-1">
                    {conversation.messages.length} mensagens
                  </p>
                </div>
                
                {/* Delete Button */}
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteConversation(conversation.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:text-accent-red"
                >
                  <Trash2 size={16} />
                </motion.button>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {filteredConversations.length === 0 && (
          <div className="text-center py-12">
            <MessageSquare size={48} className="mx-auto text-foreground-subtle/30 mb-4" />
            <p className="text-sm text-foreground-muted">
              {searchTerm ? 'Nenhuma conversa encontrada' : 'Nenhuma conversa ainda'}
            </p>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-border space-y-2">
        <motion.button
          whileHover={{ x: 4 }}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-background-hover transition-colors text-foreground-muted"
        >
          <Database size={18} />
          <span className="text-sm">Database Stats</span>
        </motion.button>
        
        <motion.button
          whileHover={{ x: 4 }}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-background-hover transition-colors text-foreground-muted"
        >
          <Settings size={18} />
          <span className="text-sm">Configurações</span>
        </motion.button>
      </div>
    </div>
  );
};