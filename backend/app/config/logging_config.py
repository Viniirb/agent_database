import logging
import logging.handlers
from pathlib import Path
from datetime import datetime

LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"
FILE_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
CONSOLE_LOG_FORMAT = '%(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

EMOJI_MAP = {
    'INFO': '✓',
    'WARNING': '⚠️',
    'ERROR': '❌',
    'DEBUG': '🔍',
    'CRITICAL': '🔴'
}

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'
    }
    
    def format(self, record):
        levelname = record.levelname
        emoji = EMOJI_MAP.get(levelname, '')
        color = self.COLORS.get(levelname, '')
        
        # Format: emoji levelname - message
        record.msg = f"{emoji} {record.getMessage()}"
        formatted = f"{color}{levelname}{self.COLORS['RESET']} - {record.msg}"
        return formatted


def setup_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # File handler (detailed)
    file_formatter = logging.Formatter(FILE_LOG_FORMAT, datefmt=DATE_FORMAT)
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler (simplified with colors)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(ColoredFormatter())
    root_logger.addHandler(console_handler)
    
    # Set app loggers
    for logger_name in ['app', 'app.api', 'app.services']:
        logging.getLogger(logger_name).setLevel(logging.INFO)
    
    # Suppress verbose third-party logs
    for logger_name in ['chromadb', 'sentence_transformers', 'uvicorn.access', 'uvicorn', 'uvicorn.error', 'uvicorn.server']:
        logging.getLogger(logger_name).setLevel(logging.CRITICAL)


setup_logging()