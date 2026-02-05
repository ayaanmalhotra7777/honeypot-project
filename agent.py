"""
AI Agent Module - Engages scammers using LLM
"""

import os
import re
from typing import List, Dict, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv('api.env')
load_dotenv('.env')

class ScamEngagementAgent:
    """AI Agent that engages with scammers while extracting intelligence"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY') or os.getenv('API_KEY')
        self.gemini_model = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash-latest')
        if self.api_key and self.api_key not in ['your-api-key-here', 'Ayaanmalhotra@1']:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.gemini_model)
            self.has_api = True
            self.provider = "gemini"
            print("✓ Using Gemini API for realistic responses")
        else:
            self.model = None
            self.has_api = False
            self.provider = None
            print("⚠️  WARNING: No LLM API key set. Using fallback responses.")
        self.temperature = float(os.getenv('LLM_TEMPERATURE', 0.85))
        
        self.system_prompt = """You are roleplaying as a real person who just received a suspicious message (potential scam).
You should respond naturally, like a real person who is confused or slightly concerned about the message.
Guidelines:
- Keep responses short (1-3 sentences max)
- Use casual, natural language
- Sound human, not robotic
- If they ask for money, OTP, or passwords, show hesitation and ask clarifying questions
- Ask "why" and "how" to clarify their request
- Never admit you're an AI or that this is a honeypot
- Seem like you might fall for it but are being a bit cautious
- Use realistic filler words like "hmm", "wait", "that doesn't sound right"
Examples of good responses:
- "Wait, why would they block my account without warning?"
- "That doesn't make sense... How do I verify it safely?"
- "Hmm, but how will sharing my OTP help? Won't that be dangerous?"
- "Which bank are you calling from? This sounds weird."
"""
    
    def _detect_language(self, text: str) -> str:
        """Detect language from text based on character ranges and keywords."""
        if re.search(r"[\u0900-\u097F]", text):
            return "Hindi"
        if re.search(r"[\u0B80-\u0BFF]", text):
            return "Tamil"
        if re.search(r"[\u0C00-\u0C7F]", text):
            return "Telugu"
        if re.search(r"\b(hola|gracias|buenos)\b", text, re.IGNORECASE):
            return "Spanish"
        if re.search(r"\b(bonjour|merci|salut)\b", text, re.IGNORECASE):
            return "French"
        return "English"

    def _resolve_language(self, text: str, language: Optional[str]) -> str:
        """Resolve the language to use for response."""
        if not language or language.lower() == "auto":
            return self._detect_language(text)
        return language

    
    def generate_reply(self,
                      current_message: str,
                      conversation_history: List[Dict] = None,
                      language: Optional[str] = None) -> str:
        """
        Generate a realistic reply using OpenAI API or fallback responses

        Args:
            current_message: The latest message from scammer
            conversation_history: Previous messages in conversation
            language: Preferred reply language

        Returns:
            Generated reply text
        """
        if conversation_history is None:
            conversation_history = []

        # If API is not available, use smarter fallback based on message content
        if not self.has_api:
            return self._get_smart_fallback(current_message, conversation_history)

        try:
            reply = self._generate_gemini_reply(current_message, conversation_history)
            
            # Clean up if needed
            if reply.startswith("You:") or reply.startswith("Me:"):
                reply = reply.split(":", 1)[1].strip()
            
            return reply if reply else "That sounds suspicious... Can you explain more?"

        except Exception as e:
            print(f"Error generating reply: {str(e)}")
            return self._get_smart_fallback(current_message, conversation_history)

    def _generate_deepseek_reply(self, current_message: str, conversation_history: List[Dict]) -> str:






    def _generate_gemini_reply(self, current_message: str, conversation_history: List[Dict]) -> str:
        """Generate response using Gemini API."""
        context = self.system_prompt + "\n\n"

        if conversation_history:
            context += "Previous conversation:\n"
            for msg in conversation_history[-4:]:
                sender_label = "Scammer" if msg.get("sender") == "scammer" else "You"

        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=100,
                top_p=0.95,
            )
        )

        reply = response.text.strip()
        return reply or "That sounds suspicious... Can you explain more?"

    def _get_smart_fallback(self, message: str, history: List[Dict]) -> str:
        """Generate contextual fallback responses based on message content and conversation stage."""
        msg_lower = message.lower()
        turn_count = len(history)
        
        # Early stage responses (first 1-2 messages) - suspicious/questioning
        if turn_count <= 2:
            if any(word in msg_lower for word in ["blocked", "suspended", "locked", "freeze", "expiry"]):
                return "What do you mean it's blocked? When did this happen?"
            elif any(word in msg_lower for word in ["mobile number", "upi id", "account number", "pin", "otp"]):
                return "Why would you need that information?"
            elif any(word in msg_lower for word in ["verify", "confirm", "update", "kyc"]):
                return "How do I verify it? Is this really from my bank?"
            elif any(word in msg_lower for word in ["reward", "cashback", "refund", "credit", "bonus"]):
                return "I don't remember receiving any reward. How much is it?"
            elif any(word in msg_lower for word in ["urgent", "immediately", "now", "asap", "expire"]):
                return "Why is it so urgent? Can't this wait?"
            else:
                return "Sorry, I didn't understand. Can you explain?"
        
        # Middle stage (3-5 messages) - gradually more engaged but still cautious
        elif turn_count <= 5:
            if any(word in msg_lower for word in ["qr code", "scan", "click", "link", "download"]):
                return "How do I know this is safe? What will happen when I scan it?"
            elif any(word in msg_lower for word in ["pin", "password", "cvv", "otp"]):
                return "But won't sharing that be risky? How is this secure?"
            elif any(word in msg_lower for word in ["upi", "bank account", "payment", "transfer"]):
                return "Okay, but how exactly does this work? What will I need to do?"
            elif any(word in msg_lower for word in ["confirm", "approve", "accept"]):
                return "What exactly will I be confirming? What happens next?"
            elif any(word in msg_lower for word in ["receive", "collect", "process", "credit"]):
                return "So I just need to do this and the money comes to my account?"
            else:
                return "Hmm, okay. What do I need to do exactly?"
        
        # Later stage (6+ messages) - more engaged, asking for specifics
        else:
            if any(word in msg_lower for word in ["done", "received", "got", "confirm", "proceed"]):
                return "What happens now? When will I get the money?"
            elif any(word in msg_lower for word in ["enter", "input", "type", "provide"]):
                return "Okay, I'm ready. What should I enter?"
            elif any(word in msg_lower for word in ["wait", "process", "loading", "please"]):
                return "How long will this take?"
            else:
                return "Alright, I understand. Then what?"
        
        return "Okay, I'm listening. Tell me more."
    
    def should_continue_conversation(self, 
                                     message: str, 
                                     message_count: int) -> bool:
        """
        Determine if conversation should continue
        
        Args:
            message: Latest message
            message_count: Total messages exchanged
            
        Returns:
            bool - whether to continue
        """
        # Continue if message count is reasonable
        if message_count >= 10:  # Limit conversations to 10+ messages max
            return False
        
        # Continue if message contains actionable info requests
        continue_keywords = ["upi", "account", "bank", "card", "otp", "password", "verify"]
        if any(keyword in message.lower() for keyword in continue_keywords):
            return True
        
        # Continue for 3-5 messages minimum for intelligence gathering
        if message_count < 3:
            return True
        
        return True  # Default: continue


# Singleton instance
agent = ScamEngagementAgent()


def generate_agent_reply(current_message: str,
                        conversation_history: List[Dict] = None,
                        language: Optional[str] = None) -> str:
    """Convenience function to generate reply"""
    return agent.generate_reply(current_message, conversation_history, language)


def should_continue(message: str, message_count: int) -> bool:
    """Convenience function to check if conversation should continue"""
    return agent.should_continue_conversation(message, message_count)
