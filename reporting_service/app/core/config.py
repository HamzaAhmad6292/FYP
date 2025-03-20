from pydantic_settings import BaseSettings
from groq import Groq

class Settings(BaseSettings):
    GROQ_API_KEY: str
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_FILE_TYPES: list = ['csv', 'xlsx', 'json']
    QDRANT_CLUSTER_URL: str
    MEM0_API_KEY: str
    QDRANT_API_KEY: str
    SEGMIND_API_KEY: str
    
    @property
    def GROQ_LLM(self):
        return Groq(api_key=self.GROQ_API_KEY)
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()