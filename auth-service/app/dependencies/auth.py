from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from supabase import Client
from app.core.config import settings
from jose import JWTError, jwt
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_supabase() -> Client:
    from supabase import create_client
    
    # Temporary hardcoded values
    import os
    

# Access environment variables
  # Debugging purpose

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY") # From Supabase dashboard
    
    # print("[HARDCODED] URL:", url)
    # print("[HARDCODED] Key:", key[:10] + "...")
    
    return create_client(url, key)

# Updated current user dependency
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    supabase: Client = Depends(get_supabase)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Get user from Supabase auth
        user = supabase.auth.get_user(token)
        if not user:
            raise credentials_exception
        return user
    except Exception as e:
        raise credentials_exception