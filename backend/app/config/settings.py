from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    google_api_key: str
    
    sql_server_host: str
    sql_server_database: str
    sql_server_use_windows_auth: bool = False
    sql_server_user: Optional[str] = None
    sql_server_password: Optional[str] = None
    sql_server_trust_certificate: bool = True
    
    chroma_persist_directory: str = str(BASE_DIR / "db_migration" / "chroma_db")
    embedding_model: str = "all-MiniLM-L6-v2"

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chroma_persist_directory = str(BASE_DIR / "db_migration" / "chroma_db")

_env_keys = ['GOOGLE_API_KEY', 'SQL_SERVER_HOST', 'SQL_SERVER_DATABASE']
for key in _env_keys:
    if key in os.environ:
        del os.environ[key]

settings = Settings()
