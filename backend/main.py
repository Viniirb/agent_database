import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.config.logging_config import setup_logging
from app.utils.logger import log_info, log_header, log_footer
from app.api import chat

# Desabilitar logs verbose do Uvicorn
logging.getLogger("uvicorn").disabled = True
logging.getLogger("uvicorn.access").disabled = True
logging.getLogger("uvicorn.error").disabled = True
logging.getLogger("uvicorn.server").disabled = True

# Inicializar logging
setup_logging()

log_header("🚀 Agent Database API")
log_info("Iniciando servidor...", emoji='rocket', module='STARTUP')

app = FastAPI(title="AI Agent Database API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

log_footer()
log_info("✨ Servidor pronto para receber requisições!", emoji='rocket', module='STARTUP')