from supabase import create_client
from supabase import create_client

url = "https://awkkgalofmsbuuwzrphf.supabase.co"
key = """eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF3a2tnYWxvZm1zYnV1d3pycGhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzgzNTUyMjIsImV4cCI6MjA1MzkzMTIyMn0.IYGzp1I5YcZxwEUFeHE9Me34wwt9iDhaXVdjVVM_NhE"""


supabase = create_client(url, key)

try:
    # Test signup
    user = supabase.auth.sign_up({
        "email": "test3@egmail.com",
        "password": "securepass123",
        "options": {
            "data": {
                "username": "testuseur",
                "business_name": "Test1 Business"
            }
        }
    })
    
    print("Auth user created:", user.user.id)
    
    # Check public.users
    db_user = supabase.table("users")\
        .select("*")\
        .eq("id", user.user.id)\
        .execute()
    
    print("Public user record:", db_user.data)

except Exception as e:
    print("Error:", e)
finally:
    if 'user' in locals():
        supabase.auth.admin.delete_user(user.user.id)