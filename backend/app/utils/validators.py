"""
Validadores de input para segurança e integridade de dados.
Previne injection attacks e garante dados válidos.
"""

import re
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)


# Padrões de segurança
SAFE_COLLECTION_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\.]+$')
SQL_INJECTION_PATTERNS = [
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
    r"(;|\-\-|\/\*|\*\/|xp_|sp_)",
    r"(\bOR\b.*=.*|\bAND\b.*=.*)",
    r"(\'|\"|`)",
]
XSS_PATTERNS = [
    r"<script[^>]*>.*?</script>",
    r"javascript:",
    r"on\w+\s*=",
    r"<iframe",
    r"<embed",
    r"<object"
]


class InputValidator:
    """Classe para validação de inputs"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """
        Sanitiza uma string removendo caracteres perigosos.
        
        Args:
            value: String a ser sanitizada
            max_length: Tamanho máximo permitido
            
        Returns:
            String sanitizada
        """
        if not value:
            return ""
        
        # Limita tamanho
        value = value[:max_length]
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Remove caracteres de controle exceto \n, \r, \t
        value = ''.join(char for char in value if ord(char) >= 32 or char in ['\n', '\r', '\t'])
        
        return value.strip()
    
    @staticmethod
    def is_safe_collection_name(name: str) -> bool:
        """
        Verifica se o nome da collection é seguro.
        
        Args:
            name: Nome da collection
            
        Returns:
            True se seguro, False caso contrário
        """
        if not name or len(name) > 255:
            return False
        
        return bool(SAFE_COLLECTION_NAME_PATTERN.match(name))
    
    @staticmethod
    def check_sql_injection(text: str) -> bool:
        """
        Verifica se o texto contém padrões de SQL injection.
        
        Args:
            text: Texto a ser verificado
            
        Returns:
            True se detectar padrão suspeito, False caso contrário
        """
        text_upper = text.upper()
        
        for pattern in SQL_INJECTION_PATTERNS:
            if re.search(pattern, text_upper, re.IGNORECASE):
                logger.warning(f"Possível SQL injection detectado: {pattern}")
                return True
        
        return False
    
    @staticmethod
    def check_xss(text: str) -> bool:
        """
        Verifica se o texto contém padrões de XSS.
        
        Args:
            text: Texto a ser verificado
            
        Returns:
            True se detectar padrão suspeito, False caso contrário
        """
        for pattern in XSS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Possível XSS detectado: {pattern}")
                return True
        
        return False
    
    @staticmethod
    def validate_chat_message(message: str, max_length: int = 10000) -> tuple[bool, Optional[str]]:
        """
        Valida uma mensagem de chat.
        
        Args:
            message: Mensagem a validar
            max_length: Tamanho máximo
            
        Returns:
            Tupla (is_valid, error_message)
        """
        if not message or not message.strip():
            return False, "Mensagem vazia"
        
        if len(message) > max_length:
            return False, f"Mensagem muito longa (máximo {max_length} caracteres)"
        
        # Verifica SQL injection
        if InputValidator.check_sql_injection(message):
            return False, "Mensagem contém padrões suspeitos"
        
        # Verifica XSS
        if InputValidator.check_xss(message):
            return False, "Mensagem contém padrões suspeitos"
        
        return True, None
    
    @staticmethod
    def validate_conversation_id(conv_id: str) -> tuple[bool, Optional[str]]:
        """
        Valida um ID de conversa.
        
        Args:
            conv_id: ID a validar
            
        Returns:
            Tupla (is_valid, error_message)
        """
        if not conv_id:
            return False, "ID vazio"
        
        # UUID v4 pattern
        uuid_pattern = re.compile(
            r'^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$',
            re.IGNORECASE
        )
        
        if not uuid_pattern.match(conv_id):
            return False, "ID inválido (deve ser UUID v4)"
        
        return True, None
    
    @staticmethod
    def validate_pagination(page: int, page_size: int, max_page_size: int = 100) -> tuple[bool, Optional[str]]:
        """
        Valida parâmetros de paginação.
        
        Args:
            page: Número da página (1-indexed)
            page_size: Tamanho da página
            max_page_size: Tamanho máximo permitido
            
        Returns:
            Tupla (is_valid, error_message)
        """
        if page < 1:
            return False, "Página deve ser >= 1"
        
        if page_size < 1:
            return False, "Tamanho da página deve ser >= 1"
        
        if page_size > max_page_size:
            return False, f"Tamanho máximo da página é {max_page_size}"
        
        return True, None
