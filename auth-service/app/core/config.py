from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    encryption_key: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int = 30

    model_config = {
        "env_file": Path(__file__).parent.parent / ".env",  # Explicit path
        "extra": "ignore"
    }

settings = Settings()
# Add this to app/core/config.py
print("[DEBUG] SUPABASE_URL (raw):", repr(settings.supabase_url))
print("[DEBUG] SUPABASE_KEY (raw):", repr(settings.supabase_key))