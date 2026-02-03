import os
import jwt
import requests
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import db_utils
import llm_utils
import json

load_dotenv()
db_utils.init_db()

app = FastAPI(title="Parent Bot AI")

# Enable CORS for integration into existing website
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EXTERNAL_API_BASE_URL = os.getenv("EXTERNAL_API_BASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET", "secret") # Shared with the main website

# Serve static files (JS, CSS, images) from the current directory
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def read_index():
    return FileResponse("index.html")

def get_parent_id_from_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Token missing")
    
    try:
        token = authorization.split(" ")[1] if " " in authorization else authorization
        payload = jwt.decode(token, options={"verify_signature": False})
        
        user_obj = payload.get("user", {})
        parent_id = user_obj.get("parentId") or user_obj.get("_id")
        
        if not parent_id:
            raise HTTPException(status_code=400, detail="Parent ID not found in token")
        
        return parent_id
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

@app.get("/api/parent/sync")
async def sync_parent_data(
    parent_id: str = Depends(get_parent_id_from_token),
    authorization: str = Header(None)
):
    """
    Fetches comprehensive parent-child data from the new POST API.
    Caches the entire response in Supabase.
    """
    # 1. Check Cache
    cached_data = db_utils.get_student_data(parent_id)
    if cached_data:
        print(f"Serving parent {parent_id} from cache.")
        return cached_data

    # 2. Fetch from New API
    new_api_url = "https://dvsserver-d7fk.onrender.com/api/v1/dvs/chatbot/parent-child-details"
    payload = {"parentId": parent_id}
    # Pass the parent's authorization token to the new API as well
    headers = {"Authorization": authorization} if authorization else {}
    
    print(f"Fetching family data for {parent_id} from {new_api_url}...")
    
    try:
        response = requests.post(new_api_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("success"):
            return {"error": "API returned failure status."}
            
        # 3. Save to Cache (using parent_id as the key)
        db_utils.save_student_data(parent_id, data)
        return data

    except Exception as e:
        print(f"New API Sync Error: {e}")
        return {"error": f"Failed to sync family data: {str(e)}"}

# Note: Keeping the old endpoint name for widget compatibility, but updating logic
@app.get("/api/student/details")
async def get_student_details(
    parent_id: str = Depends(get_parent_id_from_token),
    authorization: str = Header(None)
):
    """
    Backwards compatibility: Returns basic info about the first child.
    """
    data = await sync_parent_data(parent_id, authorization)
    if "error" in data:
        return data
        
    children = data.get("children", [])
    if not children:
        return {"error": "No children found for this parent."}
        
    child = children[0]["profile"]
    return {
        "name": child.get("studentName"),
        "id": child.get("studentId"),
        "class": child.get("class"),
        "school": child.get("schoolName")
    }

@app.post("/api/chat")
async def chat_with_parent(
    message: dict, 
    parent_id: str = Depends(get_parent_id_from_token),
    authorization: str = Header(None)
):
    """
    LLM-powered chatbot to answer parent questions using holistic context.
    """
    user_msg = message.get("text", "")
    
    # 1. Fetch full data (cached)
    full_data = await sync_parent_data(parent_id, authorization)
    
    if "error" in full_data:
        return {"reply": "I'm sorry, I'm having trouble retrieving your record right now."}

    # 2. Generate AI response using rich context
    response = llm_utils.generate_bot_response(user_msg, full_data)
    
    return {"reply": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
