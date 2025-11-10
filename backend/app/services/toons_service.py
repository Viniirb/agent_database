import logging
from typing import Dict, List, Any, Optional
from hashlib import md5
import time
from app.utils.logger import log_info, log_debug, log_warning

logger = logging.getLogger(__name__)


class ToonsOptimizer:
    def __init__(self, max_cache_size: int = 100, compression_ratio: float = 0.7):
        self.max_cache_size = max_cache_size
        self.compression_ratio = compression_ratio
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_hits = 0
        self._cache_misses = 0
        self._total_tokens_saved = 0
        log_info(f"TOONS inicializado: cache={max_cache_size}, ratio={compression_ratio}", emoji='rocket', module='TOONS')

    def _hash_content(self, content: str) -> str:
        return md5(content.encode()).hexdigest()

    def compress_context(self, context: str, max_length: int = 1000) -> Dict[str, Any]:
        start_time = time.time()
        original_length = len(context)
        content_hash = self._hash_content(context)
        
        if content_hash in self._cache:
            cached = self._cache[content_hash]
            self._cache_hits += 1
            elapsed = time.time() - start_time
            logger.debug(f"Cache HIT: {content_hash[:8]}...")
            return {
                "compressed": cached['compressed'],
                "original_length": original_length,
                "compressed_length": len(cached['compressed']),
                "reduction_percentage": round((1 - len(cached['compressed']) / original_length) * 100, 1),
                "from_cache": True,
                "processing_time_ms": round(elapsed * 1000, 2),
                "tokens_saved_estimate": int(original_length * (1 - self.compression_ratio) / 4)
            }
        
        self._cache_misses += 1
        compressed = self._apply_compression_techniques(context, max_length)
        compressed_length = len(compressed)
        self._store_in_cache(content_hash, compressed)
        
        elapsed = time.time() - start_time
        tokens_saved = int(original_length * (1 - self.compression_ratio) / 4)
        self._total_tokens_saved += tokens_saved
        
        return {
            "compressed": compressed,
            "original_length": original_length,
            "compressed_length": compressed_length,
            "reduction_percentage": round((1 - compressed_length / original_length) * 100, 1),
            "from_cache": False,
            "processing_time_ms": round(elapsed * 1000, 2),
            "tokens_saved_estimate": tokens_saved
        }

    def _apply_compression_techniques(self, context: str, max_length: int) -> str:
        lines = [line.strip() for line in context.split('\n') if line.strip()]
        lines = list(dict.fromkeys(lines))
        compressed = '\n'.join(lines)
        
        if len(compressed) > max_length:
            half = max_length // 2
            compressed = compressed[:half] + f"\n[...resumido...]\n" + compressed[-half:]
        
        return compressed

    def _store_in_cache(self, content_hash: str, compressed_content: str):
        if len(self._cache) >= self.max_cache_size:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        self._cache[content_hash] = {'compressed': compressed_content, 'timestamp': time.time()}

    def optimize_prompt(self, system_prompt: str, context: str, user_message: str) -> Dict[str, Any]:
        compression_result = self.compress_context(context)
        optimized_prompt = (
            f"{system_prompt}\n\n{compression_result['compressed']}\n\n"
            f"Pergunta do usuário: {user_message}"
        )
        original_prompt = f"{system_prompt}\n\n{context}\n\nPergunta do usuário: {user_message}"
        
        return {
            "optimized_prompt": optimized_prompt,
            "original_size": len(original_prompt),
            "optimized_size": len(optimized_prompt),
            "tokens_saved_estimate": compression_result['tokens_saved_estimate'],
            "compression_details": compression_result,
            "cache_hit": compression_result['from_cache']
        }

    def get_statistics(self) -> Dict[str, Any]:
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "total_requests": total_requests,
            "hit_rate_percentage": round(hit_rate, 1),
            "cache_size": len(self._cache),
            "max_cache_size": self.max_cache_size,
            "total_tokens_saved": self._total_tokens_saved,
            "estimated_cost_saved": f"${self._total_tokens_saved * 0.00001:.4f}"
        }

    def reset_statistics(self):
        self._cache_hits = 0
        self._cache_misses = 0
        self._total_tokens_saved = 0
        logger.info("Estatísticas TOONS resetadas")

    def clear_cache(self):
        self._cache.clear()
        logger.info("Cache TOONS limpo")


# Instância global do otimizador
toons_optimizer = ToonsOptimizer(max_cache_size=100, compression_ratio=0.7)
