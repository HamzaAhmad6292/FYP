from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from app.schemas.user import UserCreate, UserLogin, UserOut
from app.dependencies.auth import get_supabase
from app.utils.encryption import encrypt_data, decrypt_data
from app.dependencies.auth import get_supabase, get_current_user  # Updated import


router = APIRouter()

@router.post("/signup")
async def signup(user_data: UserCreate, supabase: Client = Depends(get_supabase)):
    try:
        # Create user in Supabase Auth only
        auth_response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "username": user_data.username,
                    "business_name": user_data.business_name
                }
            }
        })
        
        return {"message": "User created successfully"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/login")
async def login(credentials: UserLogin, supabase: Client = Depends(get_supabase)):
    try:
        print("Login attempt for:", credentials.email)  # Debug log
        
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email.strip(),
            "password": credentials.password.strip()
        })
        
        return {
            "access_token": response.session.access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        print("Login error:", str(e))  # Detailed error logging
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@router.get("/login/google")
async def login_with_google(supabase: Client = Depends(get_supabase)):
    try:
        response = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": "http://localhost:8000/auth/callback"
            }
        })
        return {"auth_url": response.url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/me", response_model=UserOut)
async def get_me(
    user = Depends(get_current_user),  # Now properly imported
    supabase: Client = Depends(get_supabase)
):
    try:
        # Get user details from public.users table
        db_user = supabase.table("users").select("*").eq("id", user.user.id).execute().data[0]
        return {
            "username": db_user["username"],
            "email": user.user.email,
            "business_name": decrypt_data(db_user["business_name"])
        }
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in database"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )