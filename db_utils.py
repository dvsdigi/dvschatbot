import os
import json
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

supabase: Client = None

if url and key and "your-project" not in url:
    supabase = create_client(url, key)

def init_db():
    """
    Supabase handles table creation via the dashboard. 
    This is a placeholder to maintain compatibility with main.py.
    """
    if not supabase:
        print("Warning: Supabase credentials not configured correctly.")
    else:
        print("Supabase client initialized.")

def save_student_data(student_id, data):
    if not supabase:
        print("Error: Supabase client not initialized.")
        return
    
    try:
        # Using upsert to simplify logic
        supabase.table("student_cache").upsert({
            "student_id": student_id,
            "data_json": data # jsonb handles dicts directly
        }).execute()
        print(f"Saved data for student {student_id} to Supabase.")
    except Exception as e:
        print(f"Supabase Save Error: {e}")

def get_student_data(student_id):
    if not supabase:
        return None
    
    try:
        response = supabase.table("student_cache").select("data_json").eq("student_id", student_id).execute()
        if response.data:
            return response.data[0]["data_json"]
    except Exception as e:
        print(f"Supabase Fetch Error: {e}")
    
    return None

if __name__ == "__main__":
    init_db()
