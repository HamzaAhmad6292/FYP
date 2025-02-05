import os
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SERVICE_ROLE")




supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
data = {"id": 1}

response = supabase.table("Mapped_Dataset").insert(data).execute()
print(response)
