from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import Optional

from backend.memory.session_store import memory_store
from backend.chat.handler import handle_chat_message
from backend.safety.moderator import pre_llm_check, post_llm_check
from backend.image.generator import generate_image

app = FastAPI(title="Christian AI Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    denomination: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

class ImageRequest(BaseModel):
    intent: str
    style: str = "renaissance"

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    session_id = memory_store.get_or_create_session(req.session_id)
    
    if req.denomination:
        memory_store.set_denomination(session_id, req.denomination)
        
    # Phase 1 — Pre-LLM Input Classifier
    pre_check = pre_llm_check(req.message)
    if not pre_check["passed"]:
        return ChatResponse(response=pre_check["message"], session_id=session_id)
    
    response_text = handle_chat_message(session_id, req.message)
    
    # Phase 2 — Post-generation Output Check
    post_check = post_llm_check(response_text)
    final_response = post_check["response"]
    
    return ChatResponse(response=final_response, session_id=session_id)

@app.post("/api/image")
async def image_endpoint(req: ImageRequest):
    result = generate_image(req.intent, req.style)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

@app.get("/frontend/{filename}")
async def serve_frontend_file(filename: str):
    for path in [f"frontend/{filename}", f"d:/Trentiums/Assignment/christian-ai-assistant/frontend/{filename}"]:
        if os.path.exists(path):
            return FileResponse(path)
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/")
async def read_index():
    try:
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        try:
            with open("d:/Trentiums/Assignment/christian-ai-assistant/frontend/index.html", "r", encoding="utf-8") as f:
                content = f.read()
            return HTMLResponse(content=content)
        except Exception as e2:
            return HTMLResponse(content=f"Error loading index.html: {str(e2)}", status_code=500)
