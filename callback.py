"""
Callback Module - Sends final results to GUVI evaluation endpoint
"""

import os
import json
import requests
from typing import Dict
from dotenv import load_dotenv

load_dotenv('api.env')


class CallbackHandler:
    """Handles sending results back to GUVI endpoint"""
    
    def __init__(self):
        # GUVI evaluation endpoint
        self.guvi_endpoint = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
        # Fallback local file if needed
        self.output_file = os.getenv('LOCAL_CALLBACK_FILE', 'scammer.txt')
    
    def send_result(self, payload: Dict) -> Dict:
        """
        Send final result to GUVI endpoint
        
        Args:
            payload: Dict with sessionId, scamDetected, totalMessagesExchanged, 
                    extractedIntelligence, agentNotes
            
        Returns:
            Response dict with success status
        """
        try:
            # Send to GUVI endpoint
            print(f"[INFO] Sending result to GUVI endpoint: {self.guvi_endpoint}")
            print(f"[DEBUG] Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                self.guvi_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"[INFO] GUVI Response Status: {response.status_code}")
            print(f"[INFO] GUVI Response Body: {response.text}")
            
            if response.status_code in [200, 201]:
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response": response.json() if response.text else "Success",
                    "endpoint": self.guvi_endpoint,
                    "timestamp": __import__('datetime').datetime.now().isoformat()
                }
            else:
                # If GUVI fails, log locally as backup
                print(f"[WARNING] GUVI returned {response.status_code}, logging to file as backup")
                self._log_locally(payload)
                
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "response": response.text,
                    "endpoint": self.guvi_endpoint,
                    "backed_up_locally": True
                }

        except Exception as e:
            print(f"[ERROR] Failed to send to GUVI: {str(e)}")
            # Fallback: log locally
            print(f"[INFO] Logging result locally as fallback...")
            self._log_locally(payload)
            
            return {
                "success": False,
                "error": str(e),
                "status_code": None,
                "endpoint": self.guvi_endpoint,
                "backed_up_locally": True
            }
    
    def _log_locally(self, payload: Dict):
        """Log payload to local file as backup when GUVI endpoint fails"""
        try:
            with open(self.output_file, 'a', encoding='utf-8') as handle:
                handle.write(json.dumps(payload, ensure_ascii=True, indent=2))
                handle.write("\n" + "="*80 + "\n")
            print(f"[INFO] Logged to {self.output_file}")
        except Exception as e:
            print(f"[ERROR] Failed to log locally: {str(e)}")
    
        Determine if callback should be sent
        
        Args:
            session_data: Session dict from memory
            
        Returns:
            bool - whether callback should be sent
        """
        # Send callback only if:
        # 1. Scam was detected
        # 2. Sufficient messages were exchanged (at least 3)
        # 3. Intelligence was extracted
        # 4. Result hasn't already been sent
        
        scam_detected = session_data.get("scam_detected", False)
        message_count = session_data.get("message_count", 0)
        intelligence = session_data.get("extracted_intelligence", {})
        final_result_sent = session_data.get("final_result_sent", False)
        
        # Check if we have enough engagement
        has_intelligence = any([
            len(intelligence.get("bankAccounts", [])) > 0,
            len(intelligence.get("upiIds", [])) > 0,
            len(intelligence.get("phishingLinks", [])) > 0,
            len(intelligence.get("phoneNumbers", [])) > 0,
            len(intelligence.get("suspiciousKeywords", [])) > 3  # At least 3 keywords
        ])
        
        return (scam_detected and 
                message_count >= 3 and 
                has_intelligence and 
                not final_result_sent)
    
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
