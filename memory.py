"""
Memory Management Module - Tracks sessions and conversation state
"""

from typing import Dict, List, Optional
from datetime import datetime

class SessionMemory:
    """Manages conversation state and intelligence extraction per session"""
    
    def __init__(self):
        # Store sessions: {sessionId: session_data}
        self.sessions: Dict[str, Dict] = {}
    
    def create_session(self, session_id: str, metadata: Dict = None) -> Dict:
        """
        Create or retrieve a session
        
        Args:
            session_id: Unique session identifier
            metadata: Optional metadata (channel, language, locale)
            
        Returns:
            Session object
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "sessionId": session_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "conversation_history": [],
                "metadata": metadata or {},
                "scam_detected": False,
                "confidence": 0.0,
                "extracted_intelligence": {
                    "bankAccounts": [],
                    "upiIds": [],
                    "phishingLinks": [],
                    "phoneNumbers": [],
                    "suspiciousKeywords": []
                },
                "agent_notes": "",
                "message_count": 0,
                "final_result_sent": False
            }
        
        return self.sessions[session_id]
    
    def add_message(self, session_id: str, sender: str, text: str, timestamp: str):
        """
        Add a message to conversation history
        
        Args:
            session_id: Session ID
            sender: "scammer" or "user" (our agent)
            text: Message text
            timestamp: ISO format timestamp
        """
        if session_id not in self.sessions:
            self.create_session(session_id)
        
        message = {
            "sender": sender,
            "text": text,
            "timestamp": timestamp
        }
        
        self.sessions[session_id]["conversation_history"].append(message)
        self.sessions[session_id]["message_count"] += 1
    
    def update_scam_detection(self, session_id: str, is_scam: bool, confidence: float):
        """Update scam detection status"""
        if session_id in self.sessions:
            self.sessions[session_id]["scam_detected"] = is_scam
            self.sessions[session_id]["confidence"] = confidence
    
    def update_intelligence(self, session_id: str, intelligence: Dict):
        """
        Update extracted intelligence
        
        Args:
            session_id: Session ID
            intelligence: Dict with keys for bankAccounts, upiIds, etc.
        """
        if session_id in self.sessions:
            for key, value in intelligence.items():
                if key in self.sessions[session_id]["extracted_intelligence"]:
                    existing = self.sessions[session_id]["extracted_intelligence"][key]
                    if isinstance(value, list):
                        # Add new items not already present
                        for item in value:
                            if item not in existing:
                                existing.append(item)
    
    def update_notes(self, session_id: str, notes: str):
        """Update agent notes"""
        if session_id in self.sessions:
            self.sessions[session_id]["agent_notes"] = notes
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Retrieve session data"""
        return self.sessions.get(session_id)
    
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session"""
        session = self.get_session(session_id)
        return session.get("conversation_history", []) if session else []
    
    def mark_result_sent(self, session_id: str):
        """Mark final result as sent"""
        if session_id in self.sessions:
            self.sessions[session_id]["final_result_sent"] = True
    
    def get_payload_for_callback(self, session_id: str) -> Dict:
        """
        Get the payload ready for GUVI callback
        
        Args:
            session_id: Session ID
            
        Returns:
            Formatted payload for callback
        """
        session = self.get_session(session_id)
        if not session:
            return None
        
        return {
            "sessionId": session["sessionId"],
            "scamDetected": session["scam_detected"],
            "totalMessagesExchanged": session["message_count"],
            "extractedIntelligence": session["extracted_intelligence"],
            "agentNotes": session["agent_notes"]
        }
    
    def delete_session(self, session_id: str):
        """Delete session (cleanup)"""
        if session_id in self.sessions:
            del self.sessions[session_id]


# Singleton instance
memory = SessionMemory()


def create_session(session_id: str, metadata: Dict = None) -> Dict:
    """Convenience function"""
    return memory.create_session(session_id, metadata)


def get_session(session_id: str) -> Optional[Dict]:
    """Convenience function"""
    return memory.get_session(session_id)


def get_conversation_history(session_id: str) -> List[Dict]:
    """Convenience function"""
    return memory.get_conversation_history(session_id)
