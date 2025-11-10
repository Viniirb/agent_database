"""
Helper de logging com prints customizados e coloridos.
Substitui logger.info/error por prints mais bonitos.
"""
from datetime import datetime
from typing import Optional

# Cores ANSI
COLORS = {
    'RESET': '\033[0m',
    'BOLD': '\033[1m',
    'DIM': '\033[2m',
    'CYAN': '\033[36m',
    'GREEN': '\033[32m',
    'YELLOW': '\033[33m',
    'RED': '\033[31m',
    'MAGENTA': '\033[35m',
    'BLUE': '\033[34m',
}

EMOJIS = {
    'info': '✓',
    'success': '✅',
    'warning': '⚠️',
    'error': '❌',
    'debug': '🔍',
    'critical': '🔴',
    'database': '🗄️',
    'cache': '💾',
    'api': '🔌',
    'ai': '🤖',
    'rocket': '🚀',
}


def _get_timestamp() -> str:
    """Retorna timestamp formatado."""
    return datetime.now().strftime('%H:%M:%S')


def log_info(message: str, emoji: str = 'info', module: Optional[str] = None):
    """Log de informação."""
    ts = _get_timestamp()
    emoji_str = EMOJIS.get(emoji, '✓')
    print(f"{COLORS['GREEN']}{emoji_str}{COLORS['RESET']} {message} às {COLORS['DIM']}{ts}{COLORS['RESET']}")


def log_success(message: str, module: Optional[str] = None):
    """Log de sucesso."""
    ts = _get_timestamp()
    print(f"{COLORS['GREEN']}✅{COLORS['RESET']} {message} às {COLORS['DIM']}{ts}{COLORS['RESET']}")


def log_warning(message: str, module: Optional[str] = None):
    """Log de aviso."""
    ts = _get_timestamp()
    print(f"{COLORS['YELLOW']}⚠️{COLORS['RESET']}  {message} às {COLORS['DIM']}{ts}{COLORS['RESET']}")


def log_error(message: str, module: Optional[str] = None):
    """Log de erro."""
    ts = _get_timestamp()
    print(f"{COLORS['RED']}❌{COLORS['RESET']} {message} às {COLORS['DIM']}{ts}{COLORS['RESET']}")


def log_debug(message: str, module: Optional[str] = None):
    """Log de debug."""
    ts = _get_timestamp()
    print(f"{COLORS['BLUE']}🔍{COLORS['RESET']} {message} às {COLORS['DIM']}{ts}{COLORS['RESET']}")


def log_separator(char: str = "─", length: int = 50):
    """Printa um separador."""
    print(f"{COLORS['DIM']}{char * length}{COLORS['RESET']}")


def log_header(title: str):
    """Printa um header."""
    print(f"\n{COLORS['BOLD']}{COLORS['CYAN']}╔ {title}{COLORS['RESET']}\n")


def log_footer():
    """Printa um footer."""
    print(f"\n{COLORS['DIM']}{'─' * 50}{COLORS['RESET']}\n")

