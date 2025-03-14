import os
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SERVICE_ROLE")
print("SUPABASE_URL",SUPABASE_URL)
print("SUPABASE_KEY",SUPABASE_KEY)



supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
