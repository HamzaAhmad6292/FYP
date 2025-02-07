from supabase import Client
from app.schemas.user import UserCreate
from app.utils.encryption import encrypt_data
from app.core.config import settings

class User:
    @staticmethod
    def create_user(supabase: Client, user_data: UserCreate):
        """Create a new user in Supabase"""
        try:
            # Encrypt business name before storage
            encrypted_business = encrypt_data(user_data.business_name)
            
            return supabase.table("users").insert({
                "username": user_data.username,
                "email": user_data.email,
                "business_name": encrypted_business
            }).execute()
        except Exception as e:
            raise ValueError(f"Error creating user: {str(e)}")

    @staticmethod
    def get_user_by_email(supabase: Client, email: str):
        """Retrieve user by email"""
        try:
            return supabase.table("users")\
                .select("*")\
                .eq("email", email)\
                .execute()
        except Exception as e:
            raise ValueError(f"Error fetching user: {str(e)}")

    @staticmethod
    def get_user_by_id(supabase: Client, user_id: str):
        """Retrieve user by ID"""
        try:
            return supabase.table("users")\
                .select("*")\
                .eq("id", user_id)\
                .execute()
        except Exception as e:
            raise ValueError(f"Error fetching user: {str(e)}")