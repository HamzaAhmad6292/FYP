from cryptography.fernet import Fernet
from app.core.config import settings

def encrypt_data(data: str) -> str:
    fernet = Fernet(settings.encryption_key.encode())
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    fernet = Fernet(settings.encryption_key.encode())
    return fernet.decrypt(encrypted_data.encode()).decode()