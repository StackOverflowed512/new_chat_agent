from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Any
import time
import json
import os

from app.models import SessionLocal, init_db, User, ChatSession, Message
from app.services import agent
from app.core import config

app = FastAPI(title="Highly Configurable Chat Agent")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse('static/index.html')

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    init_db()

# Pydantic Models for API
class ChatRequest(BaseModel):
    session_id: Optional[int] = None
    message: str

class ConfigUpdate(BaseModel):
    company_name: Optional[str] = None
    ceo_email: Optional[str] = None
    agent_name: Optional[str] = None
    system_prompt: Optional[str] = None
    extra_config: Optional[dict] = {} 

class ChatResponse(BaseModel):
    response: str
    session_id: int
    tool_executed: Optional[str] = None

class PresetSelect(BaseModel):
    preset_id: str

# API Routes

@app.get("/api/presets")
def get_presets():
    """Returns the list of available domain presets."""
    preset_path = os.path.join("data", "domain_presets.json")
    if os.path.exists(preset_path):
        with open(preset_path, "r") as f:
            return json.load(f)
    return []

@app.post("/api/presets/apply")
def apply_preset(selection: PresetSelect):
    """Applies a selected preset to the main configuration."""
    preset_path = os.path.join("data", "domain_presets.json")
    if not os.path.exists(preset_path):
        raise HTTPException(status_code=404, detail="Presets not found")
        
    with open(preset_path, "r") as f:
        presets = json.load(f)
    
    selected = next((p for p in presets if p["id"] == selection.preset_id), None)
    if not selected:
        raise HTTPException(status_code=404, detail="Preset ID not found")
    
    # Construct new config
    new_config = {
        "company_name": selected["company_name"],
        "ceo_email": selected["ceo_email"],
        "agent_name": f"{selected['company_name']} Assistant",
        # Auto-generated prompt handled by agent.py reading these values
        "products": selected.get("sample_data", [])
    }
    
    # Save it
    config.save_config(new_config)
    return {"status": "success", "message": f"Applied preset: {selected['company_name']}"}

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    if not request.session_id:
        user = User(name="Anonymous")
        db.add(user)
        db.commit()
        chat_session = ChatSession(user_id=user.id)
        db.add(chat_session)
        db.commit()
        session_id = chat_session.id
    else:
        session_id = request.session_id
        chat_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not chat_session:
            raise HTTPException(status_code=404, detail="Session not found")
            
    history_msgs = db.query(Message).filter(Message.session_id == session_id).order_by(Message.id).all()
    history = [{"role": ("user" if m.sender == "user" else "assistant"), "content": m.content} for m in history_msgs]
    
    # Save User Msg
    db.add(Message(session_id=session_id, sender="user", content=request.message))
    db.commit()
    
    # Process
    bot_reply, tool_result = agent.process_user_message(request.message, history)
    
    # Save Bot Msg
    db.add(Message(session_id=session_id, sender="bot", content=bot_reply))
    
    # Update Session Duration
    if chat_session:
        chat_session.end_time = datetime.utcnow()
        start = chat_session.start_time
        now = datetime.utcnow()
        duration_params = (now - start).total_seconds() / 60
        chat_session.duration_minutes = int(duration_params)
        
    db.commit()
    
    return {
        "response": bot_reply,
        "session_id": session_id,
        "tool_executed": tool_result
    }

@app.get("/api/config")
def get_configuration():
    return config.load_config()

@app.post("/api/config")
def update_configuration(update: ConfigUpdate):
    current = config.load_config()
    
    if update.company_name: current["company_name"] = update.company_name
    if update.ceo_email: current["ceo_email"] = update.ceo_email
    if update.agent_name: current["agent_name"] = update.agent_name
    if update.system_prompt: current["system_prompt"] = update.system_prompt
    
    if update.extra_config:
        for k, v in update.extra_config.items():
            current[k] = v
            
    config.save_config(current)
    return {"status": "Configuration updated", "config": current}

@app.get("/api/analytics")
def get_analytics(db: Session = Depends(get_db)):
    total_sessions = db.query(ChatSession).count()
    users = db.query(User).all()
    
    sessions = db.query(ChatSession).all()
    total_min = sum([s.duration_minutes for s in sessions])
    avg_duration = total_min / total_sessions if total_sessions > 0 else 0
    
    user_data = []
    for u in users:
        last_sess = db.query(ChatSession).filter(ChatSession.user_id == u.id).order_by(ChatSession.start_time.desc()).first()
        topic = last_sess.topic if last_sess else "N/A"
        user_data.append({
            "name": u.name,
            "email": u.email,
            "mobile": u.mobile,
            "last_topic": topic
        })
        
    return {
        "total_sessions": total_sessions,
        "average_duration_minutes": avg_duration,
        "users": user_data
    }

from datetime import datetime
