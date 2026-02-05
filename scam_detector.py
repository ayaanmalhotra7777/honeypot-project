"""
Scam Detection Module - Identifies scam intent in messages
"""

import re
from typing import Dict, Tuple

class ScamDetector:
    """Detects scam intent using keyword analysis and pattern matching"""
    
    def __init__(self):
        # High-confidence scam keywords (increased weights for better detection)
        self.scam_keywords = {
            # Urgency tactics
            "urgent": 2.5,
            "immediately": 2.5,
            "now": 1.8,
            "quickly": 1.8,
            "asap": 2.5,
            "expire": 2.2,
            "expires": 2.2,
            "limited time": 2.5,
            "today": 1.6,
            "24 hours": 2.0,
            
            # Account threats
            "blocked": 2.8,
            "suspended": 2.8,
            "locked": 2.8,
            "deactivated": 2.5,
            "freeze": 2.5,
            "expiry": 2.5,
            "will be blocked": 3.0,
            
            # Verification requests
            "verify": 2.2,
            "verification": 2.2,
            "confirm": 1.8,
            "validate": 1.8,
            "authenticate": 2.0,
            "kyc": 2.5,
            "update kyc": 3.0,
            "kyc expired": 3.0,
            
            # Payment methods
            "upi": 2.0,
            "upi id": 2.5,
            "bank account": 2.5,
            "card": 1.6,
            "credit card": 2.5,
            "debit card": 2.5,
            "transfer": 1.8,
            "paytm": 1.8,
            "phonepe": 1.8,
            "gpay": 1.8,
            
            # Personal info requests
            "mobile number": 2.2,
            "phone number": 2.2,
            "otp": 2.8,
            "pin": 2.5,
            "password": 2.5,
            "cvv": 3.0,
            "aadhaar": 2.5,
            "pan card": 2.5,
            
            # Phishing indicators
            "link": 1.8,
            "click here": 2.5,
            "download": 2.0,
            "qr code": 2.5,
            "scan": 2.0,
            "approval": 1.8,
            "authorize": 2.2,
            
            # Fake rewards
            "reward": 1.8,
            "cashback": 1.8,
            "refund": 2.0,
            "bonus": 1.8,
            "credit": 1.6,
            "won": 2.2,
            "claim": 2.0,
            "eligible": 1.8,
            
            # Threat language
            "action required": 2.8,
            "legal action": 2.5,
            "fine": 2.0,
            "penalty": 2.0,
            "arrest": 2.8,
            "compliance": 2.0,
            "rbi": 2.2,
            
            # Customer service impersonation
            "customer care": 2.0,
            "support team": 2.0,
            "security team": 2.2,
            "customer service": 2.0,
            
            # E-commerce/Shopping scams
            "order": 1.5,
            "delivery": 1.5,
            "cod": 2.0,
            "cash on delivery": 2.5,
            "package": 1.8,
            "parcel": 1.8,
            "customs": 2.2,
            "clearance fee": 2.8,
            "shipping": 1.6,
            "shipping fee": 2.5,
            "sale": 1.5,
            "discount": 1.5,
            "90% off": 2.5,
            "80% off": 2.5,
            "stock": 1.6,
            "voucher": 1.8,
            "coupon": 1.6,
            "offer": 1.5,
            "limited": 1.8,
            "exclusive": 1.8,
            "free": 1.6,
            "renewal": 1.8,
            "renew": 1.8,
            "subscription": 1.6,
            "membership": 1.6,
            
            # Job/Investment scams
            "job": 1.8,
            "work from home": 2.5,
            "wfh": 2.5,
            "earn": 2.0,
            "salary": 1.6,
            "per month": 1.6,
            "registration fee": 2.8,
            "training fee": 2.8,
            "registration": 2.0,
            "investment": 2.2,
            "invest": 2.0,
            "profit": 2.0,
            "returns": 1.8,
            "guaranteed": 2.5,
            "double your money": 3.0,
            "crypto": 2.0,
            "cryptocurrency": 2.0,
            "wallet": 1.8,
            "bitcoin": 1.8,
            "stock market": 2.0,
            "stocks": 1.8,
            "shares": 1.8,
            "survey": 1.8,
            "part-time": 1.6,
            "mlm": 2.5,
            "multi-level": 2.5,
            "withdraw": 1.8,
            "joining fee": 2.8,
            "arrears": 2.0,
            "pension": 1.6,
        }
        
        # Patterns for dangerous requests
        self.danger_patterns = [
            r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',  # Email
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',  # URL
            r'\b\d{10,}\b',  # Phone numbers
            r'[A-Z]{2}\d{10}',  # Bank account pattern
            r'\b[\w.-]+@[\w.-]+\.\w+\b',  # Email pattern
        ]
    
    def detect(self, message: str) -> Dict:
        """
        Detect scam intent in a message
        
        Args:
            message: The message text to analyze
            
        Returns:
            Dict with keys:
            - is_scam: bool
            - confidence: float (0-1)
            - detected_keywords: list
            - risk_level: str (low/medium/high/critical)
        """
        message_lower = message.lower()
        score = 0.0
        detected_keywords = []
        
        # Check for scam keywords
        for keyword, weight in self.scam_keywords.items():
            if keyword in message_lower:
                score += weight
                detected_keywords.append(keyword)
        
        # Check for dangerous patterns
        pattern_count = 0
        for pattern in self.danger_patterns:
            if re.search(pattern, message):
                pattern_count += 1
                score += 1.5
        
        # Check for ALL CAPS (urgency indicator)
        caps_count = sum(1 for c in message if c.isupper())
        if len(message) > 0 and caps_count / len(message) > 0.3:
            score += 1.5
            detected_keywords.append("excessive_caps")
        
        # Normalize score to 0-1 range (adjusted for better sensitivity)
        confidence = min(score / 8.0, 1.0)  # Lowered from 10.0 to 8.0 for better detection
        
        # Determine risk level
        if confidence >= 0.7:
            risk_level = "critical"
        elif confidence >= 0.5:
            risk_level = "high"
        elif confidence >= 0.3:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "is_scam": confidence >= 0.3,  # Lowered threshold from 0.5 to 0.3 for better detection
            "confidence": round(confidence, 2),
            "detected_keywords": detected_keywords,
            "risk_level": risk_level,
            "score": score
        }


# Singleton instance
detector = ScamDetector()


def detect_scam(message: str) -> Dict:
    """Convenience function to detect scam"""
    return detector.detect(message)
