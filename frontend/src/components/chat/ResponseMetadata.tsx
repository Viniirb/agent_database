import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Database, Zap, Cpu, Clock } from 'lucide-react';
import type { ChatResponse } from '../../types';

interface ResponseMetadataProps {
  response: ChatResponse;
}

export const ResponseMetadata = ({ response }: ResponseMetadataProps) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const hasMetadata = 
    response.search_results?.length || 
    response.collections_searched?.length ||
    response.token_optimization ||
    response.model_used;

  if (!hasMetadata) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-4 rounded-lg bg-background-card border border-border/50 overflow-hidden"
    >
      <motion.button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-background-hover transition-colors"
      >
        <div className="flex items-center gap-2 text-sm text-foreground-muted">
          <Database size={16} />
          <span>Detalhes da Busca</span>
        </div>
        <motion.div
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <ChevronDown size={16} />
        </motion.div>
      </motion.button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="border-t border-border/50 px-4 py-3 space-y-3"
          >
            {/* Collections Searched */}
            {response.collections_searched && response.collections_searched.length > 0 && (
              <div>
                <div className="text-xs font-semibold text-foreground-subtle uppercase tracking-wide mb-2">
                  <Database size={12} className="inline mr-1" />
                  Coleções Buscadas
                </div>
                <div className="flex flex-wrap gap-1">
                  {response.collections_searched.map((collection) => (
                    <span
                      key={collection}
                      className="inline-flex items-center px-2 py-1 rounded-md bg-accent-blue/10 border border-accent-blue/20 text-xs text-accent-blue"
                    >
                      {collection}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Search Results Count */}
            {response.search_results && response.search_results.length > 0 && (
              <div>
                <div className="text-xs font-semibold text-foreground-subtle uppercase tracking-wide mb-2">
                  <Database size={12} className="inline mr-1" />
                  Documentos Encontrados
                </div>
                <p className="text-sm text-foreground">
                  {response.search_results.length} documento(s) recuperado(s)
                </p>
              </div>
            )}

            {/* Token Optimization */}
            {response.token_optimization && (
              <div>
                <div className="text-xs font-semibold text-foreground-subtle uppercase tracking-wide mb-2">
                  <Zap size={12} className="inline mr-1" />
                  Otimização de Tokens
                </div>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  {response.token_optimization.tokens_saved && (
                    <div className="flex items-center gap-2">
                      <div className="w-1 h-1 rounded-full bg-accent-green" />
                      <span className="text-foreground-muted">
                        Economizado: <span className="text-foreground font-semibold">{response.token_optimization.tokens_saved}</span>
                      </span>
                    </div>
                  )}
                  {response.token_optimization.compression_ratio && (
                    <div className="flex items-center gap-2">
                      <div className="w-1 h-1 rounded-full bg-accent-purple" />
                      <span className="text-foreground-muted">
                        Compressão: <span className="text-foreground font-semibold">{(response.token_optimization.compression_ratio * 100).toFixed(1)}%</span>
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Model Info */}
            {response.model_used && (
              <div>
                <div className="text-xs font-semibold text-foreground-subtle uppercase tracking-wide mb-2">
                  <Cpu size={12} className="inline mr-1" />
                  Modelo
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-accent-purple" />
                  <span className="text-sm text-foreground">{response.model_used}</span>
                </div>
              </div>
            )}

            {/* Cache Info */}
            {response.from_cache && (
              <div className="flex items-center gap-2 p-2 rounded-lg bg-accent-green/10 border border-accent-green/20">
                <Clock size={14} className="text-accent-green" />
                <span className="text-xs text-accent-green">Resposta obtida do cache</span>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};
