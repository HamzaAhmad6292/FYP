from supabase_client import supabase

data = {
    "user_name": "TestUser",
    "user_id": 1234  # Replace with your test user ID
}

# Perform insert operation
response = supabase.table("user").insert(data).execute()