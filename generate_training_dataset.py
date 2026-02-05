#!/usr/bin/env python3
"""
Honeypot Agent Self-Test & Dataset Training Generator
Generates realistic scammer-victim conversations for fraud detection training
"""

import requests
import json
from datetime import datetime
from pathlib import Path
import csv

API_KEY = 'Ayaanmalhotra@1'
BASE_URL = 'http://127.0.0.1:8000/api/honeypot'

# Define multiple realistic scam scenarios
SCAM_SCENARIOS = {
    "UPI_KYC_Expiry": {
        "type": "KYC Expiry Scam",
        "description": "Scammer impersonates bank claiming KYC expired and UPI will be blocked",
        "channel": "whatsapp",
        "messages": [
            "Hello, this is SBI customer care. Your UPI service will be blocked in 24 hours.",
            "Your KYC details are expired. We need to update them immediately.",
            "Please share your registered Aadhaar number for verification.",
            "We need your OTP to confirm the update. You will receive an SMS.",
            "Great! Your KYC is being verified. This usually takes 2 hours.",
            "For security, please also confirm your UPI PIN.",
            "Perfect! Your service will be restored in 30 minutes.",
        ]
    },
    "Paytm_Cashback": {
        "type": "Cashback Reward Fraud",
        "description": "Scammer claims user won cashback but needs verification",
        "channel": "sms",
        "messages": [
            "Hello from Paytm Rewards! You have won Rs 5000 cashback.",
            "To claim your reward, we need to verify your Paytm account.",
            "Please provide your registered mobile number.",
            "Thank you. Now share your Paytm PIN for verification.",
            "We've sent a verification link via email. Please click to confirm.",
            "Your reward will be credited in 24 hours. Processing fee is Rs. 49.",
            "Payment received! Cashback will arrive by tomorrow.",
        ]
    },
    "PhonePe_Refund": {
        "type": "PhonePe Refund Fraud",
        "description": "Scammer claims PhonePe owes user a security refund",
        "channel": "whatsapp",
        "messages": [
            "Hi! This is PhonePe Security Team. A fraudulent transaction was detected.",
            "We found Rs 2000 in unauthorized transactions. We'll refund it.",
            "To process the refund, we need to verify your registered UPI.",
            "What is your UPI ID registered with PhonePe?",
            "Thank you. We need to access your account for verification.",
            "Please scan this QR code to authorize the refund.",
            "The refund has been initiated. Check your bank in 2 hours.",
        ]
    },
    "Amazon_Prime_Renewal": {
        "type": "Prime Subscription Fraud",
        "description": "Scammer impersonates Amazon Prime claiming auto-renewal failed",
        "channel": "email",
        "messages": [
            "Your Amazon Prime membership will expire in 1 day.",
            "We're having trouble with your payment method for renewal.",
            "Please verify your account to continue Prime benefits.",
            "We need your registered email address and password.",
            "Thank you! Now please confirm your card details.",
            "Your membership is now renewed for 1 year.",
        ]
    },
    "Bank_Account_Freeze": {
        "type": "Account Freeze Threat",
        "description": "Scammer threatens to freeze bank account for compliance",
        "channel": "sms",
        "messages": [
            "ALERT: Your account will be frozen for non-compliance with RBI rules.",
            "Update your KYC details immediately to avoid account suspension.",
            "Reply with your account number to begin verification.",
            "Please share your Aadhaar number for federal verification.",
            "We need your banking PIN to confirm your identity.",
            "Your account is now verified. You're all set.",
        ]
    }
}

def test_scam_conversation(session_id, scenario_name, scenario_data):
    """Test a single scam scenario"""
    print(f"\n{'='*70}")
    print(f"Scenario: {scenario_data['type']}")
    print(f"Description: {scenario_data['description']}")
    print(f"Channel: {scenario_data['channel']}")
    print(f"{'='*70}\n")
    
    headers = {'x-api-key': API_KEY, 'Content-Type': 'application/json'}
    conversation_history = []
    conversation_data = {
        'scenario': scenario_name,
        'type': scenario_data['type'],
        'channel': scenario_data['channel'],
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'turns': []
    }
    
    for turn, msg in enumerate(scenario_data['messages'], 1):
        print(f"[Turn {turn}] Scammer: \"{msg}\"")
        
        payload = {
            'sessionId': session_id,
            'message': {
                'sender': 'scammer',
                'text': msg,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            },
            'conversationHistory': conversation_history,
            'metadata': {
                'channel': scenario_data['channel'],
                'language': 'english',
                'locale': 'IN'
            }
        }
        
        try:
            resp = requests.post(BASE_URL, json=payload, headers=headers, timeout=8)
            if resp.status_code == 200:
                result = resp.json()
                victim_reply = result['reply']
                is_scam = result['scam_detected']
                confidence = result['confidence']
                
                print(f"         Victim: \"{victim_reply}\"")
                print(f"         [Scam Detected: {is_scam} | Confidence: {confidence:.2f}]\n")
                
                # Record turn data
                conversation_data['turns'].append({
                    'turn': turn,
                    'scammer_msg': msg,
                    'victim_reply': victim_reply,
                    'scam_detected': is_scam,
                    'confidence': confidence
                })
                
                # Update conversation history
                conversation_history.append({
                    'sender': 'scammer',
                    'text': msg,
                    'timestamp': payload['message']['timestamp']
                })
                conversation_history.append({
                    'sender': 'user',
                    'text': victim_reply,
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                })
            else:
                print(f"         ERROR: HTTP {resp.status_code}")
                # Continue to next scenario on error
                break
                
        except requests.exceptions.Timeout:
            print(f"         TIMEOUT: Request took too long, skipping this turn")
            break
        except Exception as e:
            print(f"         ERROR: {str(e)}")
            break
    
    return conversation_data

def main():
    """Run full agent self-test and dataset generation"""
    print("\n" + "="*70)
    print("  HONEYPOT AGENT SELF-TEST & DATASET TRAINING GENERATOR")
    print("="*70)
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print(f"API Endpoint: {BASE_URL}")
    print(f"Scenarios: {len(SCAM_SCENARIOS)}")
    print("="*70)
    
    # Store all conversations
    all_conversations = []
    
    # Test each scenario
    for scenario_name, scenario_data in SCAM_SCENARIOS.items():
        session_id = f"{scenario_name}-{datetime.utcnow().timestamp()}"
        conversation = test_scam_conversation(session_id, scenario_name, scenario_data)
        all_conversations.append(conversation)
    
    # Save dataset as JSON
    dataset_file = Path("training_dataset.json")
    with open(dataset_file, 'w', encoding='utf-8') as f:
        json.dump(all_conversations, f, indent=2, ensure_ascii=False)
    
    # Save dataset as CSV for analytics
    csv_file = Path("training_dataset.csv")
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Scenario', 'Type', 'Channel', 'Turn', 
            'Scammer Message', 'Victim Response', 
            'Scam Detected', 'Confidence Score'
        ])
        
        for conv in all_conversations:
            for turn in conv['turns']:
                writer.writerow([
                    conv['scenario'],
                    conv['type'],
                    conv['channel'],
                    turn['turn'],
                    turn['scammer_msg'],
                    turn['victim_reply'],
                    turn['scam_detected'],
                    turn['confidence']
                ])
    
    # Print summary statistics
    print(f"\n{'='*70}")
    print("  DATASET GENERATION COMPLETE")
    print(f"{'='*70}")
    
    total_turns = sum(len(conv['turns']) for conv in all_conversations)
    total_scams_detected = sum(
        1 for conv in all_conversations 
        for turn in conv['turns'] 
        if turn['scam_detected']
    )
    avg_confidence = sum(
        turn['confidence'] for conv in all_conversations 
        for turn in conv['turns']
    ) / total_turns if total_turns > 0 else 0
    
    print(f"\nScenarios Tested: {len(all_conversations)}")
    print(f"Total Conversation Turns: {total_turns}")
    print(f"Scams Detected: {total_scams_detected}")
    print(f"Detection Rate: {(total_scams_detected/total_turns*100):.1f}%")
    print(f"Average Confidence Score: {avg_confidence:.3f}")
    
    print(f"\nDatasets Created:")
    if dataset_file.exists():
        print(f"  ✓ JSON Format: {dataset_file.name} ({dataset_file.stat().st_size:,} bytes)")
    else:
        print(f"  ✗ JSON Format: {dataset_file.name} (failed)")
        
    if csv_file.exists():
        print(f"  ✓ CSV Format: {csv_file.name} ({csv_file.stat().st_size:,} bytes)")
    else:
        print(f"  ✗ CSV Format: {csv_file.name} (failed)")
    
    print(f"\n{'='*70}")
    print("Dataset processing complete!")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
