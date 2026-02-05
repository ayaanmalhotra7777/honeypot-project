"""
Main API Server - FastAPI-based REST API for Honeypot System
"""

import sys
from pathlib import Path

# Add project root to path  
sys.path.insert(0, str(Path(__file__).parent))

print("[DEBUG] Starting application initialization...")
print(f"[DEBUG] Python version: {sys.version}")
  
  
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Dict, Optional

# Load environment variables FIRST before any module imports
try:
    result = load_dotenv('api.env')
    print(f"[DEBUG] load_dotenv result: {result}")
except Exception as e:
    print(f"[DEBUG] Warning: Failed to load api.env: {e}")

# Set up API keys in environment BEFORE importing modules that use them
print(f"[DEBUG] Checking environment variables...")
api_key_1 = os.getenv('API_KEY')
api_key_2 = os.getenv('GEMINI_API_KEY')
print(f"[DEBUG] API_KEY from env: {api_key_1[:20] if api_key_1 else 'None'}...")
print(f"[DEBUG] GEMINI_API_KEY from env: {api_key_2[:20] if api_key_2 else 'None'}...")

GEMINI_API_KEY = api_key_1 or api_key_2 or 'Ayaanmalhotra@1'
os.environ['API_KEY'] = GEMINI_API_KEY
os.environ['GEMINI_API_KEY'] = GEMINI_API_KEY
print(f"[DEBUG] Set both env vars to: {GEMINI_API_KEY[:20]}...")

print(f"[DEBUG] About to import FastAPI...")
# NOW import other modules after environment is configured
from fastapi import FastAPI, Header, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel

print(f"[DEBUG] About to import custom modules...")
# Import our modules (these now have proper environment variables set)
from scam_detector import detect_scam
print(f"[DEBUG] Imported detect_scam")
from agent import generate_agent_reply, should_continue
print(f"[DEBUG] Imported agent")
from memory import create_session, get_session, memory
print(f"[DEBUG] Imported memory")
from extractor import extract_intelligence, get_tactics_summary
print(f"[DEBUG] Imported extractor")
from callback import send_final_result, should_send_callback
print(f"[DEBUG] Imported callback")
from db import init_db, persist_intelligence, persist_message, persist_session
print(f"[DEBUG] Imported db")
from logger import log_event
print(f"[DEBUG] Imported logger")

# Create scam conversations directory
try:
    os.makedirs('scam_conversations', exist_ok=True)
    print(f"[DEBUG] Created scam_conversations directory")
except Exception as e:
    print(f"[DEBUG] Warning: Failed to create scam_conversations: {e}")

# Initialize FastAPI app
print(f"[DEBUG] Creating FastAPI app...")
app = FastAPI(
    title="Agentic Honeypot for Scam Detection",
    description="AI-powered scam detection and intelligence extraction system",
    version="1.0.0"
)
print(f"[DEBUG] FastAPI app created successfully")

# Initialize persistence
print(f"[DEBUG] Initializing database...")
try:
    init_db()
    print(f"[DEBUG] Database initialized successfully")
except Exception as e:
    print(f"[DEBUG] ERROR initializing database: {e}")
    import traceback
    traceback.print_exc()

print(f"[DEBUG] Application initialization complete!")


def save_scam_conversation_to_txt(session_id: str, session: dict, last_message: str, last_reply: str, confidence: float):
    """Save detected scam conversation to a txt file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"scam_conversations/scam_{session_id}_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("SCAM CONVERSATION DETECTED\n")
        f.write("="*80 + "\n\n")
        f.write(f"Session ID: {session_id}\n")
        f.write(f"Detection Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Scam Confidence: {confidence:.2%}\n")
        f.write(f"Total Messages: {session.get('message_count', 0)}\n")
        f.write(f"Channel: {session.get('metadata', {}).get('channel', 'Unknown')}\n")
        f.write(f"Language: {session.get('metadata', {}).get('language', 'Unknown')}\n")
        f.write("\n" + "-"*80 + "\n")
        f.write("CONVERSATION HISTORY\n")
        f.write("-"*80 + "\n\n")
        
        # Get conversation history
        conv_history = memory.get_conversation_history(session_id)
        for idx, msg in enumerate(conv_history, 1):
            sender_label = "[SCAMMER]" if msg['sender'] == 'scammer' else "[VICTIM]"
            f.write(f"{sender_label} Message {idx}:\n")
            f.write(f"{msg['text']}\n\n")
        
        # Add intelligence
        f.write("\n" + "-"*80 + "\n")
        f.write("EXTRACTED INTELLIGENCE\n")
        f.write("-"*80 + "\n\n")
        intelligence = session.get('extracted_intelligence', {})
        for key, value in intelligence.items():
            if value:
                f.write(f"{key.replace('_', ' ').title()}: {value}\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("END OF CONVERSATION\n")
        f.write("="*80 + "\n")
    
    print(f"💾 Scam conversation saved to: {filename}")


# ============ Request/Response Models ============

class MessageModel(BaseModel):
    """Individual message in conversation"""
    sender: str  # "scammer" or "user"
    text: str
    timestamp: str


class MetadataModel(BaseModel):
    """Request metadata"""
    channel: Optional[str] = "SMS"  # SMS, WhatsApp, Email, Chat
    language: Optional[str] = "English"
    locale: Optional[str] = "IN"


class HoneypotRequest(BaseModel):
    """Main API request model"""
    sessionId: str
    message: MessageModel
    conversationHistory: Optional[List[MessageModel]] = []
    metadata: Optional[MetadataModel] = None


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

def verify_api_key(x_api_key: str = Header(...)) -> str:
    """Verify API key in request header"""
    if x_api_key != GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return x_api_key


# ============ Main API Endpoint ============

@app.post("/api/honeypot", response_model=HoneypotResponse)
async def honeypot_endpoint(
    request: HoneypotRequest,
    api_key: str = Header(..., alias="x-api-key")
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
    if api_key != GEMINI_API_KEY:
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

    # Step 8: Save scam conversation to txt file if detected
    if is_scam:
        save_scam_conversation_to_txt(session_id, session, current_message, agent_reply, confidence)
    
    # Step 9: Persist session snapshot and log event
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
