"""
Rate Limiter para controlar requisições aos modelos Gemini
Evita ultrapassar os limites do tier gratuito
"""
import time
import asyncio
from collections import deque
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate Limiter simples baseado em janela deslizante
    Controla quantas requisições podem ser feitas por minuto
    """

    def __init__(self, requests_per_minute: int = 10):
        """
        Args:
            requests_per_minute: Número máximo de requisições por minuto
        """
        self.requests_per_minute = requests_per_minute
        self.request_times: deque = deque()
        self.lock = asyncio.Lock()

    async def acquire(self):
        """
        Aguarda até que seja seguro fazer uma nova requisição.
        Implementa janela deslizante de 60 segundos.
        """
        async with self.lock:
            current_time = time.time()

            # Remove requisições antigas (fora da janela de 1 minuto)
            while self.request_times and current_time - self.request_times[0] > 60:
                self.request_times.popleft()

            # Se atingiu o limite, aguarda
            if len(self.request_times) >= self.requests_per_minute:
                oldest_request = self.request_times[0]
                wait_time = 60 - (current_time - oldest_request)

                if wait_time > 0:
                    logger.warning(f"⏳ Rate limit atingido. Aguardando {wait_time:.2f}s antes da próxima requisição...")
                    await asyncio.sleep(wait_time)

                    # Remove a requisição mais antiga após aguardar
                    self.request_times.popleft()

            # Registra a nova requisição
            self.request_times.append(time.time())
            logger.debug(f"✓ Requisição permitida ({len(self.request_times)}/{self.requests_per_minute} no último minuto)")


class MultiModelRateLimiter:
    """
    Gerencia rate limiters para múltiplos modelos
    Cada modelo pode ter seu próprio limite
    """

    def __init__(self):
        self.limiters: Dict[str, RateLimiter] = {}

        # Configuração dos limites por modelo (tier gratuito)
        # Usamos 80% do limite real para ter margem de segurança
        self.model_limits = {
            "gemini-2.0-flash-lite": 12,  # Real: 15 RPM
            "gemini-2.5-flash": 12,       # Real: 15 RPM
            "gemini-2.0-flash": 12,       # Real: 15 RPM
            "gemini-2.5-pro": 1,          # Real: 2 RPM (muito baixo!)
        }

        # Inicializa limiters para cada modelo
        for model_name, limit in self.model_limits.items():
            self.limiters[model_name] = RateLimiter(requests_per_minute=limit)
            logger.info(f"Rate limiter configurado para {model_name}: {limit} RPM")

    async def acquire(self, model_name: str):
        """
        Aguarda até que seja seguro fazer requisição para o modelo especificado

        Args:
            model_name: Nome do modelo Gemini
        """
        # Se o modelo não está na lista, usa um limiter padrão conservador
        if model_name not in self.limiters:
            logger.warning(f"Modelo {model_name} não configurado. Usando limite padrão de 5 RPM")
            self.limiters[model_name] = RateLimiter(requests_per_minute=5)

        await self.limiters[model_name].acquire()


# Instância global do rate limiter
rate_limiter = MultiModelRateLimiter()
