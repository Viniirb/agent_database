from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    anthropic_api_key: str
    sql_server_host: str
    sql_server_database: str
    sql_server_user: str
    sql_server_password: str
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
