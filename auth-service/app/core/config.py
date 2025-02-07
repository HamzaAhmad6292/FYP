from pydantic_settings import BaseSettings
from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    supabase_url: str = os.getenv("supabase_url")
    supabase_key: str = os.getenv("supabase_key")
    encryption_key: str = os.getenv("encryption_key")
    secret_key: str = os.getenv("secret_key")
    algorithm: str = os.getenv("algorithm")
    access_token_expire_minutes: int = int(os.getenv("access_token_expire_minutes", 30))
    
settings = Settings()

print("[DEBUG] SUPABASE_URL:", settings.supabase_url)
print("[DEBUG] SUPABASE_KEY:", settings.supabase_key)
print("[DEBUG] SECRET_KEY:", settings.secret_key)
