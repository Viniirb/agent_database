"""
Sistema de logging estruturado em JSON.
Facilita parsing por ferramentas de análise de logs (ELK, Grafana Loki, etc).
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path


class JSONFormatter(logging.Formatter):
    """
    Formata logs em JSON estruturado.
    Compatível com sistemas de log aggregation.
    """
    
    def __init__(
        self,
        service_name: str = "agent-database-api",
        environment: str = "development",
        include_extra: bool = True
    ):
        """
        Args:
            service_name: Nome do serviço
            environment: Ambiente (development, staging, production)
            include_extra: Se deve incluir campos extras do LogRecord
        """
        super().__init__()
        self.service_name = service_name
        self.environment = environment
        self.include_extra = include_extra
        self.hostname = self._get_hostname()
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Formata LogRecord em JSON.
        
        Args:
            record: Registro de log
            
        Returns:
            String JSON
        """
        # Campos base
        log_data = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": self.service_name,
            "environment": self.environment,
            "hostname": self.hostname,
        }
        
        # Adiciona informações de código
        log_data["source"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
            "module": record.module,
        }
        
        # Adiciona informações de thread/processo
        log_data["process"] = {
            "id": record.process,
            "name": record.processName,
            "thread_id": record.thread,
            "thread_name": record.threadName,
        }
        
        # Adiciona exception info se presente
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info) if record.exc_info else None,
            }
        
        # Adiciona stack info se presente
        if record.stack_info:
            log_data["stack"] = record.stack_info
        
        # Adiciona campos extras customizados
        if self.include_extra:
            extra_fields = self._extract_extra_fields(record)
            if extra_fields:
                log_data["extra"] = extra_fields
        
        # Adiciona correlation ID se presente
        if hasattr(record, 'correlation_id'):
            log_data["correlation_id"] = record.correlation_id
        
        # Adiciona user ID se presente
        if hasattr(record, 'user_id'):
            log_data["user_id"] = record.user_id
        
        # Adiciona request ID se presente
        if hasattr(record, 'request_id'):
            log_data["request_id"] = record.request_id
        
        return json.dumps(log_data, ensure_ascii=False)
    
    def _extract_extra_fields(self, record: logging.LogRecord) -> Dict[str, Any]:
        """Extrai campos extras do LogRecord"""
        # Campos padrão do LogRecord
        standard_fields = {
            'name', 'msg', 'args', 'created', 'filename', 'funcName', 'levelname',
            'levelno', 'lineno', 'module', 'msecs', 'message', 'pathname',
            'process', 'processName', 'relativeCreated', 'thread', 'threadName',
            'exc_info', 'exc_text', 'stack_info', 'taskName'
        }
        
        extra = {}
        for key, value in record.__dict__.items():
            if key not in standard_fields and not key.startswith('_'):
                # Converte valores não-serializáveis
                try:
                    json.dumps(value)
                    extra[key] = value
                except (TypeError, ValueError):
                    extra[key] = str(value)
        
        return extra
    
    def _get_hostname(self) -> str:
        """Obtém hostname da máquina"""
        try:
            import socket
            return socket.gethostname()
        except Exception:
            return "unknown"


class StructuredLogger:
    """
    Logger wrapper para facilitar logging estruturado.
    Adiciona contexto automaticamente aos logs.
    """
    
    def __init__(
        self,
        name: str,
        correlation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        **context
    ):
        """
        Args:
            name: Nome do logger
            correlation_id: ID de correlação
            user_id: ID do usuário
            request_id: ID da requisição
            **context: Contexto adicional
        """
        self.logger = logging.getLogger(name)
        self.correlation_id = correlation_id
        self.user_id = user_id
        self.request_id = request_id
        self.context = context
    
    def _add_context(self, extra: Optional[Dict] = None) -> Dict:
        """Adiciona contexto aos logs"""
        log_extra = self.context.copy()
        
        if self.correlation_id:
            log_extra['correlation_id'] = self.correlation_id
        if self.user_id:
            log_extra['user_id'] = self.user_id
        if self.request_id:
            log_extra['request_id'] = self.request_id
        
        if extra:
            log_extra.update(extra)
        
        return log_extra
    
    def debug(self, message: str, **extra):
        """Log debug com contexto"""
        self.logger.debug(message, extra=self._add_context(extra))
    
    def info(self, message: str, **extra):
        """Log info com contexto"""
        self.logger.info(message, extra=self._add_context(extra))
    
    def warning(self, message: str, **extra):
        """Log warning com contexto"""
        self.logger.warning(message, extra=self._add_context(extra))
    
    def error(self, message: str, **extra):
        """Log error com contexto"""
        self.logger.error(message, extra=self._add_context(extra))
    
    def critical(self, message: str, **extra):
        """Log critical com contexto"""
        self.logger.critical(message, extra=self._add_context(extra))
    
    def exception(self, message: str, **extra):
        """Log exception com contexto e traceback"""
        self.logger.exception(message, extra=self._add_context(extra))


def setup_json_logging(
    service_name: str = "agent-database-api",
    environment: str = "development",
    log_level: str = "INFO",
    log_file: Optional[str] = None
):
    """
    Configura logging em JSON para toda a aplicação.
    
    Args:
        service_name: Nome do serviço
        environment: Ambiente
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Caminho para arquivo de log (opcional)
    """
    # Remove handlers existentes
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configura nível de log
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Cria formatter JSON
    formatter = JSONFormatter(
        service_name=service_name,
        environment=environment
    )
    
    # Handler para console (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Handler para arquivo se especificado
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Desabilita logs verbose de bibliotecas
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    
    root_logger.info(
        f"JSON logging configurado",
        extra={
            "service": service_name,
            "environment": environment,
            "log_level": log_level,
            "log_file": log_file
        }
    )
