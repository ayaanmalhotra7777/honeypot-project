"""
Main API Server - FastAPI-based REST API for Honeypot System
"""




import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))
  
  
from fastapi import FastAPI, Header, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

# Import our modules
from scam_detector import detect_scam
from agent import generate_agent_reply, should_continue
from memory import create_session, get_session, memory
from extractor import extract_intelligence, get_tactics_summary
from callback import send_final_result, should_send_callback
from db import init_db, persist_intelligence, persist_message, persist_session
from logger import log_event

load_dotenv('api.env')

# Initialize persistence
init_db()

# Initialize FastAPI app
app = FastAPI(
    title="Agentic Honeypot for Scam Detection",
    description="AI-powered scam detection and intelligence extraction system",
    version="1.0.0"
)

# API Key from environment
GEMINI_API_KEY = os.getenv('API_KEY', 'Ayaanmalhotra@1')


# ============ Request/Response Models ============

class MessageModel(BaseModel):
    """Individual message in conversation"""
    sender: Optional[str] = "scammer"  # "scammer" or "user"
    text: str
    timestamp: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_message(cls, values):
        if isinstance(values, dict):
            if "text" not in values:
                if "message" in values:
                    values["text"] = values.get("message")
                elif "content" in values:
                    values["text"] = values.get("content")
        return values


class MetadataModel(BaseModel):
    """Request metadata"""
    channel: Optional[str] = "SMS"  # SMS, WhatsApp, Email, Chat
    language: Optional[str] = "English"
    locale: Optional[str] = "IN"


class HoneypotRequest(BaseModel):
    """Main API request model"""
    sessionId: str = Field(alias="session_id")
    message: MessageModel
    conversationHistory: Optional[List[MessageModel]] = Field(default_factory=list, alias="conversation_history")
    metadata: Optional[MetadataModel] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_payload(cls, values):
        """Normalize payloads that send message as a string or omit fields."""
        if isinstance(values, dict):
            if "sessionId" not in values:
                if "session_id" in values:
                    values["sessionId"] = values.get("session_id")
                elif "sessionID" in values:
                    values["sessionId"] = values.get("sessionID")
                elif "requestId" in values:
                    values["sessionId"] = values.get("requestId")
                elif "request_id" in values:
                    values["sessionId"] = values.get("request_id")

            message = values.get("message")
            if isinstance(message, str):
                values["message"] = {
                    "sender": "scammer",
                    "text": message,
                    "timestamp": datetime.now().isoformat() + "Z"
                }
            elif isinstance(message, dict):
                message.setdefault("sender", "scammer")
                message.setdefault("timestamp", datetime.now().isoformat() + "Z")
            if values.get("conversationHistory") is None and values.get("conversation_history") is None:
                values["conversationHistory"] = []
        return values


class AgentResponse(BaseModel):
    """Agent response model"""
    status: str  # "success" or "failure"
    reply: str
    scam_detected: bool = True
    confidence: float = 0.0
    intelligence_extracted: Dict = {}


class HoneypotResponse(BaseModel):
    """Final API response"""
    status: str
    reply: str
    scam_detected: bool
    confidence: float
    extracted_intelligence: Dict
    message_count: int
    callback_sent: bool = False


# ============ Authentication ============

def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Verify API key in request header"""
    if not x_api_key or x_api_key != GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return x_api_key


# ============ Main API Endpoint ============

@app.get("/api/honeypot")
async def honeypot_get():
    """GET endpoint - returns endpoint documentation"""
    return {
        "status": "error",
        "error": "Method not allowed. Use POST instead.",
        "endpoint": "POST /api/honeypot",
        "required_headers": {
            "x-api-key": "your-api-key",
            "Content-Type": "application/json"
        }
    }

@app.post("/api/honeypot", response_model=HoneypotResponse)
async def honeypot_endpoint(
    request: HoneypotRequest,
    api_key: Optional[str] = Header(None, alias="x-api-key")
):
    """
    Main honeypot endpoint - detects scams and engages with scammers
    
    Args:
        request: HoneypotRequest with message and conversation history
        api_key: API key in x-api-key header
        
    Returns:
        HoneypotResponse with agent reply and extracted intelligence
    """
    
    # Verify API key
    if not api_key or api_key != GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    session_id = request.sessionId
    current_message = request.message.text
    metadata = request.metadata.dict() if request.metadata else {}
    
    # Step 1: Initialize or retrieve session
    session = create_session(session_id, metadata)
    
    # Step 2: Add current message to history
    memory.add_message(
        session_id,
        "scammer",
        current_message,
        request.message.timestamp
    )
    persist_message(session_id, "scammer", current_message, request.message.timestamp)
    
    # Step 3: Detect scam intent
    scam_result = detect_scam(current_message)
    is_scam = scam_result["is_scam"]
    confidence = scam_result["confidence"]
    
    # Update session with scam detection
    memory.update_scam_detection(session_id, is_scam, confidence)
    
    # Step 4: Generate agent reply
    agent_reply = ""
    
    # Always generate agent reply (whether scam or not)
    conv_history = memory.get_conversation_history(session_id)
    
    # Generate reply using agent
    try:
        agent_reply = generate_agent_reply(
            current_message,
            conv_history,
            metadata.get("language")
        )
    except Exception as e:
        print(f"Agent error: {str(e)}")
        agent_reply = "I'm confused by your message. Can you explain more?"
    
    # Add agent reply to history
    agent_timestamp = datetime.now().isoformat() + "Z"
    memory.add_message(
        session_id,
        "user",
        agent_reply,
        agent_timestamp
    )
    persist_message(session_id, "user", agent_reply, agent_timestamp)
    
    # Step 5: Extract intelligence from conversation
    conv_history = memory.get_conversation_history(session_id)
    intelligence = extract_intelligence(conv_history)
    
    # Update session with intelligence
    memory.update_intelligence(session_id, intelligence)
    persist_intelligence(session_id, intelligence)
    
    # Step 6: Generate agent notes
    if is_scam:
        tactics = get_tactics_summary(intelligence)
        notes = f"Scam detected with confidence {confidence:.2%}. Tactics: {tactics}"
        memory.update_notes(session_id, notes)
    
    # Step 7: Always write out the current result
    callback_sent = False
    payload = {
        "sessionId": session_id,
        "scamDetected": session["scam_detected"],
        "totalMessagesExchanged": session["message_count"],
        "extractedIntelligence": session["extracted_intelligence"],
        "agentNotes": session["agent_notes"]
    }

    result = send_final_result(payload)
    callback_sent = result.get("success", False)

    # Step 8: Persist session snapshot and log event
    session["updated_at"] = datetime.now().isoformat()
    persist_session(session)
    log_event(
        session_id=session_id,
        sender_text=current_message,
        agent_reply=agent_reply,
        scam_detected=is_scam,
        confidence=confidence,
        message_count=session["message_count"],
        callback_sent=callback_sent,
        intelligence=intelligence,
        metadata=metadata
    )
    
    # Step 10: Return response
    return HoneypotResponse(
        status="success",
        reply=agent_reply,
        scam_detected=is_scam,
        confidence=confidence,
        extracted_intelligence=intelligence,
        message_count=session["message_count"],
        callback_sent=callback_sent
    )


# ============ Health Check Endpoint ============

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Agentic Honeypot",
        "timestamp": datetime.now().isoformat()
    }


# ============ Status Endpoint ============

@app.get("/api/session/{session_id}")
async def get_session_status(
    session_id: str,
    api_key: str = Header(..., alias="x-api-key")
):
    """Get status of a session"""
    
    if api_key != GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    session = get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    return {
        "sessionId": session_id,
        "scam_detected": session["scam_detected"],
        "confidence": session["confidence"],
        "message_count": session["message_count"],
        "extracted_intelligence": session["extracted_intelligence"],
        "final_result_sent": session["final_result_sent"]
    }


# ============ Root Endpoint ============

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Agentic Honeypot API",
        "docs": "/docs",
        "health": "/health",
        "chat_ui": "/chat",
        "api_tester": "/tester",
        "main_endpoint": "POST /api/honeypot"
    }


# ============ Chat UI Endpoint ============

@app.get("/chat")
async def chat_ui():
    """Simple web UI for simulating chat sessions"""
    html_path = Path(__file__).parent / "static" / "chat.html"
    return FileResponse(html_path, media_type="text/html")


# ============ API Tester Endpoint ============

@app.get("/tester")
async def api_tester():
    """API Endpoint Tester for validating honeypot deployment"""
    html_path = Path(__file__).parent / "static" / "api_tester.html"
    return FileResponse(html_path, media_type="text/html")


# ============ Error Handlers ============

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return {
        "status": "error",
        "message": str(exc),
        "timestamp": datetime.now().isoformat()
    }


# ============ Server Configuration ============

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 8000))
    
    print(f"\n🚀 Starting Agentic Honeypot API...")
    print(f"📍 Server: http://{host}:{port}")
    print(f"📖 Docs: http://{host}:{port}/docs")
    print(f"❤️  Health: http://{host}:{port}/health\n")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
