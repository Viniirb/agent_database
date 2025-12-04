"""
Circuit Breaker Pattern para proteger chamadas à API Gemini.
Previne sobrecarga quando o serviço externo está falhando.
"""

import time
import logging
from enum import Enum
from typing import Callable, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Estados do Circuit Breaker"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failure threshold exceeded, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerError(Exception):
    """Exceção quando o circuit breaker está aberto"""
    pass


class CircuitBreaker:
    """
    Implementa o padrão Circuit Breaker.
    
    Estados:
    - CLOSED: Funcionamento normal
    - OPEN: Muitas falhas, rejeita requisições
    - HALF_OPEN: Teste para ver se serviço recuperou
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception,
        name: str = "CircuitBreaker"
    ):
        """
        Args:
            failure_threshold: Número de falhas antes de abrir o circuito
            recovery_timeout: Tempo (segundos) antes de tentar recuperar
            expected_exception: Tipo de exceção que conta como falha
            name: Nome do circuit breaker para logs
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.name = name
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED
        
        logger.info(f"Circuit Breaker '{name}' inicializado: "
                   f"threshold={failure_threshold}, timeout={recovery_timeout}s")
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Executa a função protegida pelo circuit breaker.
        
        Args:
            func: Função a ser executada
            *args, **kwargs: Argumentos da função
            
        Returns:
            Resultado da função
            
        Raises:
            CircuitBreakerError: Se o circuito estiver aberto
            Exception: Exceção original da função
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                logger.info(f"[{self.name}] Tentando recuperação (HALF_OPEN)")
                self.state = CircuitState.HALF_OPEN
            else:
                remaining = self._get_remaining_timeout()
                logger.warning(f"[{self.name}] Circuit OPEN - tentativa bloqueada "
                             f"(recuperação em {remaining}s)")
                raise CircuitBreakerError(
                    f"Circuit breaker '{self.name}' está aberto. "
                    f"Tente novamente em {remaining} segundos."
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Chamado quando a requisição tem sucesso"""
        self.failure_count = 0
        
        if self.state == CircuitState.HALF_OPEN:
            logger.info(f"[{self.name}] Recuperação bem-sucedida - CLOSED")
            self.state = CircuitState.CLOSED
            self.success_count += 1
    
    def _on_failure(self):
        """Chamado quando a requisição falha"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        logger.warning(f"[{self.name}] Falha {self.failure_count}/{self.failure_threshold}")
        
        if self.failure_count >= self.failure_threshold:
            logger.error(f"[{self.name}] Threshold atingido - Circuit OPEN por {self.recovery_timeout}s")
            self.state = CircuitState.OPEN
    
    def _should_attempt_reset(self) -> bool:
        """Verifica se deve tentar resetar o circuito"""
        if self.last_failure_time is None:
            return False
        
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout
    
    def _get_remaining_timeout(self) -> int:
        """Retorna tempo restante até tentativa de recuperação"""
        if self.last_failure_time is None:
            return 0
        
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        remaining = max(0, self.recovery_timeout - elapsed)
        return int(remaining)
    
    def reset(self):
        """Reseta o circuit breaker manualmente"""
        logger.info(f"[{self.name}] Reset manual - CLOSED")
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
    
    def get_stats(self) -> dict:
        """Retorna estatísticas do circuit breaker"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout,
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "remaining_timeout": self._get_remaining_timeout() if self.state == CircuitState.OPEN else 0
        }
