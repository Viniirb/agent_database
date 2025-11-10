"""
Módulo de exceções customizadas e tratamento de erros.
Fornece classes específicas para diferentes tipos de erro na aplicação.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ApplicationError(Exception):
    """Exceção base para erros da aplicação."""
    
    def __init__(self, message: str, error_code: str = "APP_ERROR", status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)
    
    def to_dict(self):
        """Converte para dicionário para resposta HTTP."""
        return {
            "error": self.error_code,
            "message": self.message,
            "status_code": self.status_code
        }


class AIModelError(ApplicationError):
    """Erro ao chamar modelo de IA."""
    
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message, "AI_MODEL_ERROR", status_code)


class RateLimitError(AIModelError):
    """Erro de limite de taxa (rate limit) da API."""
    
    def __init__(self, message: str = "Limite de requisições atingido"):
        super().__init__(message, 429)


class DatabaseError(ApplicationError):
    """Erro ao acessar banco de dados."""
    
    def __init__(self, message: str):
        super().__init__(message, "DATABASE_ERROR", 500)


class CacheError(ApplicationError):
    """Erro ao acessar cache."""
    
    def __init__(self, message: str):
        super().__init__(message, "CACHE_ERROR", 500)


class ValidationError(ApplicationError):
    """Erro de validação de entrada."""
    
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR", 400)


class CircuitBreakerError(ApplicationError):
    """Erro do circuit breaker (serviço indisponível)."""
    
    def __init__(self, message: str = "Serviço temporariamente indisponível"):
        super().__init__(message, "CIRCUIT_BREAKER_ERROR", 503)


class RetryExhaustedError(ApplicationError):
    """Erro após esgotar todas as tentativas de retry."""
    
    def __init__(self, message: str = "Máximo de tentativas excedido"):
        super().__init__(message, "RETRY_EXHAUSTED", 503)


class CircuitBreaker:
    """
    Implementação do padrão Circuit Breaker.
    Evita requisições a serviços indisponíveis.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        """
        Inicializa o circuit breaker.
        
        Args:
            failure_threshold: Número de falhas antes de abrir o circuito
            recovery_timeout: Tempo em segundos antes de tentar recuperar
            expected_exception: Tipo de exceção esperada
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        """
        Executa uma função com proteção de circuit breaker.
        
        Args:
            func: Função a executar
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados
            
        Returns:
            Resultado da função
            
        Raises:
            CircuitBreakerError: Se circuito está aberto
        """
        import time
        
        if self.state == "OPEN":
            # Verificar se pode transicionar para HALF_OPEN
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker em HALF_OPEN, tentando recuperar")
            else:
                raise CircuitBreakerError(
                    f"Circuit breaker aberto. Tente novamente em "
                    f"{int(self.recovery_timeout - (time.time() - self.last_failure_time))} segundos"
                )
        
        try:
            result = func(*args, **kwargs)
            
            # Sucesso - resetar
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
                logger.info("Circuit breaker recuperado, voltando ao estado CLOSED")
            
            return result
            
        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.error(
                    f"Circuit breaker aberto após {self.failure_count} falhas. "
                    f"Serviço indisponível por {self.recovery_timeout}s"
                )
                raise CircuitBreakerError(str(e))
            
            raise


class RetryConfig:
    """Configuração de retry."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True
    ):
        """
        Inicializa configuração de retry.
        
        Args:
            max_attempts: Número máximo de tentativas
            initial_delay: Delay inicial em segundos
            max_delay: Delay máximo em segundos
            backoff_factor: Multiplicador exponencial
            jitter: Adicionar aleatoriedade ao delay
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter


def retry_with_backoff(
    func,
    config: Optional[RetryConfig] = None,
    expected_exceptions: tuple = (Exception,)
):
    """
    Executa uma função com retry e backoff exponencial.
    
    Args:
        func: Função a executar
        config: Configuração de retry
        expected_exceptions: Exceções que acionam retry
        
    Returns:
        Resultado da função
        
    Raises:
        RetryExhaustedError: Se todas as tentativas falharem
    """
    import time
    import random
    
    config = config or RetryConfig()
    
    for attempt in range(1, config.max_attempts + 1):
        try:
            logger.debug(f"Tentativa {attempt}/{config.max_attempts}")
            return func()
            
        except expected_exceptions as e:
            if attempt == config.max_attempts:
                logger.error(f"Todas as {config.max_attempts} tentativas falharam")
                raise RetryExhaustedError(str(e))
            
            # Calcular delay
            delay = min(
                config.initial_delay * (config.backoff_factor ** (attempt - 1)),
                config.max_delay
            )
            
            # Adicionar jitter
            if config.jitter:
                delay = delay * (0.5 + random.random())
            
            logger.warning(
                f"Tentativa {attempt} falhou. Aguardando {delay:.2f}s "
                f"antes da próxima tentativa. Erro: {str(e)}"
            )
            
            time.sleep(delay)
    
    raise RetryExhaustedError("Erro ao executar função com retry")


# Circuit breakers globais para serviços críticos
gemini_circuit_breaker = CircuitBreaker(
    failure_threshold=3,
    recovery_timeout=30,
    expected_exception=(AIModelError, RateLimitError)
)

chroma_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=DatabaseError
)

redis_circuit_breaker = CircuitBreaker(
    failure_threshold=3,
    recovery_timeout=30,
    expected_exception=CacheError
)
