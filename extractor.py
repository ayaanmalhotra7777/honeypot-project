"""
Intelligence Extraction Module - Parses scam-related data from messages
"""

import re
from typing import Dict, List

class IntelligenceExtractor:
    """Extracts structured intelligence from scam conversations"""
    
    def __init__(self):
        # Regex patterns for different data types
        self.patterns = {
            "phoneNumbers": r'\+91\d{10}|\b91\d{10}|(\()?(\d{3})(-)?(\d{3})(-)?(\d{4})\)?',
            "bankAccounts": r'[A-Z]{2}\d{10,}|\d{4}[\s-]\d{4}[\s-]\d{4}[\s-]\d{4}',
            "upiIds": r'[\w.-]+@[a-zA-Z]{3,}|[a-zA-Z0-9._-]+@(upi|okaxis|ibl|okhdfcbank)',
            "phishingLinks": r'https?://[^\s]+|www\.[^\s]+',
            "emails": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        }
        
        # Suspicious keywords that indicate scam tactics
        self.suspicious_keywords = {
            "urgency": ["urgent", "immediately", "now", "quickly", "asap", "don't delay"],
            "threats": ["blocked", "suspended", "locked", "freeze", "legal action", "arrest", "fine"],
            "verification": ["verify", "confirm", "validate", "authenticate", "confirm identity"],
            "payment": ["upi", "bank transfer", "credit card", "debit card", "payment"],
            "personal_info": ["otp", "pin", "password", "cvv", "account number"],
            "phishing": ["click link", "download app", "visit site", "open attachment"]
        }
    
    def extract_intelligence(self, conversation_history: List[Dict]) -> Dict:
        """
        Extract all intelligence from conversation
        
        Args:
            conversation_history: List of message dicts from memory
            
        Returns:
            Dict with extracted intelligence
        """
        intelligence = {
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": [],
            "tactics_used": []
        }
        
        # Combine all messages
        full_text = " ".join([msg.get("text", "") for msg in conversation_history])
        
        # Extract phone numbers
        phone_matches = re.findall(self.patterns["phoneNumbers"], full_text)
        for match in phone_matches:
            if isinstance(match, tuple):
                # Handle tuple returns from complex patterns
                phone = ''.join(filter(None, match))
            else:
                phone = match
            if phone and phone not in intelligence["phoneNumbers"]:
                intelligence["phoneNumbers"].append(phone)
        
        # Extract UPI IDs
        upi_matches = re.findall(self.patterns["upiIds"], full_text)
        for upi in set(upi_matches):
            if upi and upi not in intelligence["upiIds"]:
                intelligence["upiIds"].append(upi)
        
        # Extract bank accounts
        bank_matches = re.findall(self.patterns["bankAccounts"], full_text)
        for bank in set(bank_matches):
            if bank and bank not in intelligence["bankAccounts"]:
                intelligence["bankAccounts"].append(bank)
        
        # Extract phishing links
        link_matches = re.findall(self.patterns["phishingLinks"], full_text)
        for link in set(link_matches):
            if link and link not in intelligence["phishingLinks"]:
                intelligence["phishingLinks"].append(link)
        
        # Extract suspicious keywords
        detected_keywords = set()
        full_text_lower = full_text.lower()
        
        for category, keywords in self.suspicious_keywords.items():
            for keyword in keywords:
                if keyword.lower() in full_text_lower:
                    detected_keywords.add(keyword)
                    if category not in [t["category"] for t in intelligence.get("tactics_used", [])]:
                        intelligence["tactics_used"].append({"category": category, "keyword": keyword})
        
        intelligence["suspiciousKeywords"] = list(detected_keywords)
        
        return intelligence
    
    def extract_from_message(self, message: str) -> Dict:
        """
        Extract intelligence from single message
        
        Args:
            message: Single message text
            
        Returns:
            Dict with extracted data from this message
        """
        return self.extract_intelligence([{"text": message}])
    
    def get_scammer_tactics(self, intelligence: Dict) -> str:
        """
        Generate summary of scammer tactics
        
        Args:
            intelligence: Extracted intelligence dict
            
        Returns:
            String description of tactics
        """
        tactics = []
        
        if intelligence.get("phoneNumbers"):
            tactics.append("Requested phone number sharing")
        
        if intelligence.get("upiIds"):
            tactics.append("Solicited UPI IDs")
        
        if intelligence.get("bankAccounts"):
            tactics.append("Attempted to collect bank account details")
        
        if intelligence.get("phishingLinks"):
            tactics.append("Shared suspicious links for phishing")
        
        keywords = intelligence.get("suspiciousKeywords", [])
        if any(kw in keywords for kw in ["urgent", "immediately", "now"]):
            tactics.append("Used urgency tactics")
        
        if any(kw in keywords for kw in ["blocked", "suspended", "locked"]):
            tactics.append("Threatened account suspension/blocking")
        
        if any(kw in keywords for kw in ["legal action", "arrest", "fine"]):
            tactics.append("Used threat of legal consequences")
        
        return " | ".join(tactics) if tactics else "Suspicious message detected"


# Singleton instance
extractor = IntelligenceExtractor()


def extract_intelligence(conversation_history: List[Dict]) -> Dict:
    """Convenience function"""
    return extractor.extract_intelligence(conversation_history)


def get_tactics_summary(intelligence: Dict) -> str:
    """Convenience function"""
    return extractor.get_scammer_tactics(intelligence)
