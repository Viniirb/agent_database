"""
Serviço de Cache Persistente usando Redis.
Integrado com TOONS para cache inteligente e eficiente.
"""

import json
import logging
from typing import Dict, Any, Optional
from hashlib import md5
from datetime import datetime
import os
from app.utils.logger import log_info, log_warning, log_error, log_debug

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)


class CacheService:
    """
    Serviço de cache persistente usando Redis.
    Armazena respostas de chat, histórico de conversas e estatísticas.
    """

    def __init__(
        self,
        redis_host: str = os.getenv("REDIS_HOST", "localhost"),
        redis_port: int = int(os.getenv("REDIS_PORT", 6379)),
        redis_db: int = int(os.getenv("REDIS_DB", 0)),
        default_ttl: int = 3600
    ):
        """
        Inicializa o serviço de cache.
        
        Args:
            redis_host: Host do Redis
            redis_port: Porta do Redis
            redis_db: Database do Redis
            default_ttl: TTL padrão em segundos
        """
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.default_ttl = default_ttl
        self._client = None
        self._initialized = False
        
        try:
            self._initialize_connection()
        except Exception as e:
            log_warning(f"Redis não está rodando. Cache em memória será usado.", module='CACHE')
            self._initialized = False

    def _initialize_connection(self):
        """Inicializa conexão com Redis."""
        if not REDIS_AVAILABLE:
            log_warning("Pacote redis não instalado. Cache desabilitado.", module='CACHE')
            return
            
        try:
            self._client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                decode_responses=True,
                socket_connect_timeout=5
            )
            self._client.ping()
            self._initialized = True
            log_info(f"Conectado ao Redis em {self.redis_host}:{self.redis_port}", emoji='cache', module='CACHE')
        except Exception as e:
            log_warning(f"Redis indisponível no {self.redis_host}:{self.redis_port} - usando fallback em memória", module='CACHE')
            self._client = None
            self._initialized = False

    def _is_available(self) -> bool:
        """Verifica se Redis está disponível."""
        if not self._initialized:
            return False
        try:
            self._client.ping()
            return True
        except Exception as e:
            logger.warning(f"Redis não respondendo: {e}")
            return False

    def _generate_key(self, prefix: str, identifier: str) -> str:
        """Gera uma chave Redis única."""
        return f"{prefix}:{identifier}"

    def cache_chat_response(
        self,
        message: str,
        response: str,
        conversation_id: str,
        metadata: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """Cacheia uma resposta de chat."""
        if not self._is_available():
            return False
        
        try:
            message_hash = md5(message.encode()).hexdigest()
            key = self._generate_key(f"chat_response:{conversation_id}", message_hash)
            
            cache_data = {
                "message": message,
                "response": response,
                "conversation_id": conversation_id,
                "metadata": metadata,
                "cached_at": datetime.now().isoformat()
            }
            
            ttl = ttl or self.default_ttl
            self._client.setex(
                key,
                ttl,
                json.dumps(cache_data, ensure_ascii=False)
            )
            
            logger.debug(f"Chat response cacheado: {key} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao cachear resposta de chat: {e}")
            return False

    def get_cached_response(
        self,
        message: str,
        conversation_id: str
    ) -> Optional[Dict[str, Any]]:
        """Recupera uma resposta cacheada."""
        if not self._is_available():
            return None
        
        try:
            message_hash = md5(message.encode()).hexdigest()
            key = self._generate_key(f"chat_response:{conversation_id}", message_hash)
            
            cached_data = self._client.get(key)
            if cached_data:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(cached_data)
            
            logger.debug(f"Cache MISS: {key}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao recuperar cache: {e}")
            return None

    def save_conversation(
        self,
        conversation_id: str,
        user_id: Optional[str] = None,
        ttl: Optional[int] = None
    ) -> bool:
        """Salva metadata de uma conversa."""
        if not self._is_available():
            return False
        
        try:
            key = self._generate_key("conversation", conversation_id)
            
            conv_data = {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "messages_count": 0
            }
            
            ttl = ttl or self.default_ttl * 24
            self._client.setex(
                key,
                ttl,
                json.dumps(conv_data, ensure_ascii=False)
            )
            
            logger.debug(f"Conversa salva: {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar conversa: {e}")
            return False

    def add_message_to_conversation(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Adiciona uma mensagem ao histórico da conversa."""
        if not self._is_available():
            return False
        
        try:
            messages_key = self._generate_key("messages", conversation_id)
            
            message_data = {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            self._client.lpush(
                messages_key,
                json.dumps(message_data, ensure_ascii=False)
            )
            
            self._client.ltrim(messages_key, 0, 99)
            self._client.expire(messages_key, self.default_ttl * 24)
            
            logger.debug(f"Mensagem adicionada: {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar mensagem: {e}")
            return False

    def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 50
    ) -> list:
        """Recupera o histórico de uma conversa."""
        if not self._is_available():
            return []
        
        try:
            messages_key = self._generate_key("messages", conversation_id)
            raw_messages = self._client.lrange(messages_key, 0, limit - 1)
            messages = [json.loads(msg) for msg in raw_messages]
            
            logger.debug(f"Histórico recuperado: {conversation_id} ({len(messages)} msgs)")
            return messages
            
        except Exception as e:
            logger.error(f"Erro ao recuperar histórico: {e}")
            return []

    def delete_conversation(self, conversation_id: str) -> bool:
        """Deleta uma conversa e seu histórico."""
        if not self._is_available():
            return False
        
        try:
            keys_to_delete = [
                self._generate_key("conversation", conversation_id),
                self._generate_key("messages", conversation_id),
            ]
            
            pattern = f"chat_response:{conversation_id}:*"
            for key in self._client.scan_iter(match=pattern):
                keys_to_delete.append(key)
            
            if keys_to_delete:
                self._client.delete(*keys_to_delete)
            
            logger.info(f"Conversa deletada: {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao deletar conversa: {e}")
            return False

    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do Redis."""
        if not self._is_available():
            return {
                "status": "offline",
                "message": "Redis não está disponível"
            }
        
        try:
            info = self._client.info()
            
            return {
                "status": "online",
                "connected_clients": info.get('connected_clients', 0),
                "used_memory": info.get('used_memory_human', 'N/A'),
                "total_keys": self._client.dbsize(),
                "redis_version": info.get('redis_version', 'N/A'),
                "uptime_seconds": info.get('uptime_in_seconds', 0)
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas Redis: {e}")
            return {"status": "error", "error": str(e)}

    def clear_all_cache(self) -> bool:
        """Limpa todo o cache."""
        if not self._is_available():
            return False
        
        try:
            self._client.flushdb()
            logger.warning("ALERTA: Todo o cache foi limpo!")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
            return False

    def close(self):
        """Fecha a conexão com Redis."""
        if self._client:
            try:
                self._client.close()
                logger.info("Conexão Redis fechada")
            except Exception as e:
                logger.error(f"Erro ao fechar Redis: {e}")


# Instância global do serviço de cache
cache_service = CacheService()
