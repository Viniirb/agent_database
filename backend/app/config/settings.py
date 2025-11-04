from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os
from pathlib import Path

# Encontra o diretório raiz do projeto (onde está o .env)
# Sobe 3 níveis: backend/app/config -> backend/app -> backend -> raiz
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    # Google Gemini API Configuration
    google_api_key: str

    # SQL Server Configuration
    sql_server_host: str
    sql_server_database: str
    sql_server_use_windows_auth: bool = False
    sql_server_user: Optional[str] = None
    sql_server_password: Optional[str] = None
    sql_server_trust_certificate: bool = True

    # ChromaDB Configuration  
    chroma_persist_directory: str = str(BASE_DIR / "db_migration" / "chroma_db")
    embedding_model: str = "all-MiniLM-L6-v2"

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding='utf-8',
        case_sensitive=False,
        # IMPORTANTE: Desabilita leitura de variáveis de ambiente do sistema
        # para forçar uso apenas do arquivo .env
        extra='ignore'
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # FORÇA o caminho correto do ChromaDB independente do .env
        self.chroma_persist_directory = str(BASE_DIR / "db_migration" / "chroma_db")

# Limpa variáveis de ambiente que podem conflitar
# para garantir que apenas o .env seja usado
_env_keys = ['GOOGLE_API_KEY', 'SQL_SERVER_HOST', 'SQL_SERVER_DATABASE']
for key in _env_keys:
    if key in os.environ:
        del os.environ[key]

settings = Settings()
