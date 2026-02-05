"""
Callback Module - Logs scam results to file
"""

import os
import json
from typing import Dict
from dotenv import load_dotenv

load_dotenv('api.env')


class CallbackHandler:
    """Handles logging results to file"""
    
    def __init__(self):
        self.output_file = os.getenv('LOCAL_CALLBACK_FILE', 'scammer.txt')
    
    def send_result(self, payload: Dict) -> Dict:
        """
        Log result to file
        
        Args:
            payload: Dict with sessionId, scamDetected, totalMessagesExchanged, 
                    extractedIntelligence, agentNotes
            
        Returns:
            Response dict with success status
        """
        try:
            with open(self.output_file, 'a', encoding='utf-8') as handle:
                handle.write(json.dumps(payload, ensure_ascii=True, indent=2))
                handle.write("\n" + "="*80 + "\n")

            return {
                "success": True,
                "status_code": 200,
                "response": f"Logged to {self.output_file}",
                "timestamp": __import__('datetime').datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": None
            }
    
    def should_send_callback(self, session_data: Dict) -> bool:
        """
        Determine if callback should be sent
        
        Args:
            session_data: Session dict from memory
            
        Returns:
            bool - whether callback should be sent
        """
        # Always return False - don't interrupt chat
        return False
    
    def prepare_payload(self, session_data: Dict) -> Dict:
        """
        Prepare final payload for callback
        
        Args:
            session_data: Session dict from memory
            
        Returns:
            Formatted payload
        """
        return {
            "sessionId": session_data.get("sessionId"),
            "scamDetected": session_data.get("scam_detected", False),
            "totalMessagesExchanged": session_data.get("message_count", 0),
            "extractedIntelligence": session_data.get("extracted_intelligence", {}),
            "agentNotes": session_data.get("agent_notes", "")
        }


# Singleton instance
callback_handler = CallbackHandler()


def send_final_result(payload: Dict) -> Dict:
    """Convenience function to send result"""
    return callback_handler.send_result(payload)


def should_send_callback(session_data: Dict) -> bool:
    """Convenience function to check if callback should be sent"""
    return callback_handler.should_send_callback(session_data)
