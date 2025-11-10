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
import { useActiveConversation } from '../../contexts/ChatContext';
import { SessionStats } from '../chat/SessionStats';
import type { Conversation } from '../../types';
import type { ExtendedMessage } from '../../hooks/useChat';

export const Sidebar = () => {
  const { activeConversationId, setActiveConversationId } = useActiveConversation();
  const [conversations, setConversations] = useState<Conversation[]>(
    storageService.getConversations()
  );
  const [searchTerm, setSearchTerm] = useState('');

  const activeConversation = conversations.find(c => c.id === activeConversationId);
  const activeMessages = (activeConversation?.messages || []) as ExtendedMessage[];

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
    <div className="h-full flex flex-col bg-gray-950 border-r border-gray-800">
      <div className="p-4 border-b border-gray-800">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleNewChat}
          className="w-full flex items-center justify-center gap-2 py-2.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
        >
          <Plus size={18} />
          <span>Nova Conversa</span>
        </motion.button>

        <div className="mt-3 relative">
          <Search 
            size={16} 
            className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-600" 
          />
          <input
            type="text"
            placeholder="Buscar..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-2 text-sm rounded-lg bg-gray-900 border border-gray-800 text-gray-200 placeholder:text-gray-600 focus:border-blue-500 focus:outline-none transition-colors"
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
              whileHover={{ x: 2 }}
              className={`
                group relative p-2.5 rounded-lg cursor-pointer
                transition-all duration-200
                ${activeConversationId === conversation.id 
                  ? 'bg-blue-600/20 border border-blue-500/30' 
                  : 'hover:bg-gray-900'
                }
              `}
              onClick={() => setActiveConversationId(conversation.id)}
            >
              <div className="flex items-start gap-2">
                <MessageSquare 
                  size={16} 
                  className="text-gray-600 mt-0.5 flex-shrink-0" 
                />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-200 truncate">
                    {conversation.title}
                  </p>
                  <p className="text-xs text-gray-600 mt-0.5">
                    {conversation.messages.length} msgs
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
                  className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:text-red-500 flex-shrink-0"
                >
                  <Trash2 size={14} />
                </motion.button>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {filteredConversations.length === 0 && (
          <div className="text-center py-8">
            <MessageSquare size={32} className="mx-auto text-gray-700 mb-2" />
            <p className="text-xs text-gray-600">
              {searchTerm ? 'Nenhuma conversa encontrada' : 'Nenhuma conversa ainda'}
            </p>
          </div>
        )}
      </div>

      <div className="p-3 border-t border-gray-800 space-y-1">
        {activeConversationId && (
          <SessionStats messages={activeMessages} currentConversationId={activeConversationId} />
        )}
      </div>
    </div>
  );
};