"""
Configuração customizada para Uvicorn - Remove logs verbose
"""
import logging

# Disable all uvicorn loggers
logging.getLogger("uvicorn").disabled = True
logging.getLogger("uvicorn.access").disabled = True
logging.getLogger("uvicorn.error").disabled = True
logging.getLogger("uvicorn.server").disabled = True

# Config dict para passar ao uvicorn
log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.NullHandler",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "CRITICAL", "propagate": False},
        "uvicorn.access": {"handlers": ["default"], "level": "CRITICAL", "propagate": False},
        "uvicorn.error": {"handlers": ["default"], "level": "CRITICAL", "propagate": False},
        "uvicorn.server": {"handlers": ["default"], "level": "CRITICAL", "propagate": False},
    },
}
