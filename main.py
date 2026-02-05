"""Honeypot API - Full version with scam detection"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Set up environment FIRST before any imports
from dotenv import load_dotenv
load_dotenv('api.env')

# Configure API keys before importing modules that use them
GEMINI_API_KEY = os.getenv('API_KEY') or os.getenv('GEMINI_API_KEY') or 'Ayaanmalhotra@1'
os.environ['API_KEY'] = GEMINI_API_KEY
os.environ['GEMINI_API_KEY'] = GEMINI_API_KEY

# NOW import FastAPI and other modules
from fastapi import FastAPI, Header, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import our modules (they now have env vars set)
try:
    from scam_detector import detect_scam
    from agent import generate_agent_reply, should_continue
    from memory import create_session, get_session, memory
    from extractor import extract_intelligence, get_tactics_summary
    from callback import send_final_result, should_send_callback
    from db import init_db, persist_intelligence, persist_message, persist_session
    from logger import log_event
    MODULES_LOADED = True
except Exception as e:
    print(f"Warning: Could not load all modules: {e}")
    MODULES_LOADED = False

# Create scam conversations directory
os.makedirs('scam_conversations', exist_ok=True)

# Initialize FastAPI app
app = FastAPI(
    title="Agentic Honeypot for Scam Detection",
    description="AI-powered scam detection and intelligence extraction system",
    version="1.0.0"
)

# Add CORS middleware to allow requests from all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Initialize persistence if modules loaded
if MODULES_LOADED:
    try:
        init_db()
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")


# ============ Request/Response Models ============

class MessageModel(BaseModel):
    """Individual message in conversation"""
    sender: str
    text: str
    timestamp: str


class MetadataModel(BaseModel):
    """Request metadata"""
    channel: Optional[str] = "SMS"
    language: Optional[str] = "English"
    locale: Optional[str] = "IN"


class HoneypotRequest(BaseModel):
    """Main API request model"""
    sessionId: str
    message: MessageModel
    conversationHistory: Optional[List[MessageModel]] = []
    metadata: Optional[MetadataModel] = None


class HoneypotResponse(BaseModel):
    """Final API response"""
    status: str
    reply: str
    scam_detected: bool
    confidence: float
    extracted_intelligence: Dict
    message_count: int
    callback_sent: bool = False


# ============ Main Honeypot Endpoint ============

@app.post("/api/honeypot", response_model=HoneypotResponse)
async def honeypot_endpoint(
    request: HoneypotRequest,
    api_key: str = Header(None, alias="x-api-key")
):
    """Main honeypot endpoint - detects scams and engages with scammers"""
    
    # Check if modules are loaded
    if not MODULES_LOADED:
        return HoneypotResponse(
            status="error",
            reply="Service not fully initialized",
            scam_detected=False,
            confidence=0.0,
            extracted_intelligence={},
            message_count=0,
            callback_sent=False
        )
    
    # Verify API key if provided
    if api_key and api_key != GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    try:
        session_id = request.sessionId
        current_message = request.message.text
        metadata = request.metadata.dict() if request.metadata else {}
        
        # Initialize or retrieve session
        session = create_session(session_id, metadata)
        
        # Add current message to history
        memory.add_message(session_id, "scammer", current_message, request.message.timestamp)
        persist_message(session_id, "scammer", current_message, request.message.timestamp)
        
        # Detect scam intent
        scam_result = detect_scam(current_message)
        is_scam = scam_result["is_scam"]
        confidence = scam_result["confidence"]
        
        # Update session with scam detection
        memory.update_scam_detection(session_id, is_scam, confidence)
        
        # Generate agent reply
        conv_history = memory.get_conversation_history(session_id)
        try:
            agent_reply = generate_agent_reply(current_message, conv_history, metadata.get("language"))
        except Exception as e:
            agent_reply = "I'm confused by your message. Can you explain more?"
        
        # Add agent reply to history
        agent_timestamp = datetime.now().isoformat() + "Z"
        memory.add_message(session_id, "user", agent_reply, agent_timestamp)
        persist_message(session_id, "user", agent_reply, agent_timestamp)
        
        # Extract intelligence from conversation
        conv_history = memory.get_conversation_history(session_id)
        intelligence = extract_intelligence(conv_history)
        
        # Update session with intelligence
        memory.update_intelligence(session_id, intelligence)
        persist_intelligence(session_id, intelligence)
        
        # Send callback result
        callback_sent = False
        payload = {
            "sessionId": session_id,
            "scamDetected": session["scam_detected"],
            "totalMessagesExchanged": session["message_count"],
            "extractedIntelligence": session["extracted_intelligence"],
            "agentNotes": session["agent_notes"]
        }
        try:
            result = send_final_result(payload)
            callback_sent = result.get("success", False)
        except Exception as e:
            pass
        
        # Persist session and log event
        session["updated_at"] = datetime.now().isoformat()
        persist_session(session)
        log_event(session_id, current_message, agent_reply, is_scam, confidence, session["message_count"], callback_sent, intelligence, metadata)
        
        # Return response
        return HoneypotResponse(
            status="success",
            reply=agent_reply,
            scam_detected=is_scam,
            confidence=confidence,
            extracted_intelligence=intelligence,
            message_count=session["message_count"],
            callback_sent=callback_sent
        )
    except Exception as e:
        print(f"Error in honeypot_endpoint: {e}")
        return HoneypotResponse(
            status="error",
            reply="An error occurred processing your message",
            scam_detected=False,
            confidence=0.0,
            extracted_intelligence={},
            message_count=0,
            callback_sent=False
        )


# ============ Health Check ============

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Agentic Honeypot",
        "timestamp": datetime.now().isoformat()
    }


# ============ Root Endpoint ============

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "status": "ok",
        "service": "Honeypot",
        "timestamp": datetime.now().isoformat()
    }


# ============ Chat UI Endpoint ============

@app.get("/chat")
def chat_ui():
    """Simple web UI for simulating chat sessions"""
    try:
        html_path = Path(__file__).parent / "static" / "chat.html"
        return FileResponse(html_path, media_type="text/html")
    except Exception as e:
        return {"error": str(e)}


# ============ API Tester Endpoint ============

@app.get("/tester")
def api_tester():
    """API Endpoint Tester for validating honeypot deployment"""
    try:
        html_path = Path(__file__).parent / "static" / "api_tester.html"
        return FileResponse(html_path, media_type="text/html")
    except Exception as e:
        return {"error": str(e)}

