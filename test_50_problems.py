#!/usr/bin/env python3
"""
50 Test Problems - Comprehensive Scam Detection Test
Tests honeypot against 50 real-world scam scenarios
"""

import requests
import json
from datetime import datetime
from collections import defaultdict

API_KEY = 'Ayaanmalhotra@1'
BASE_URL = 'http://127.0.0.1:8000/api/honeypot'

# 50 Real-World Scam Test Cases
TEST_SCAMS = [
    # Banking & UPI Scams (15)
    {"msg": "Your SBI account will be blocked within 24 hours. Update KYC now.", "type": "Banking Threat", "expected": True},
    {"msg": "Urgent: Your UPI service is blocked. Share your UPI PIN to restore.", "type": "UPI Fraud", "expected": True},
    {"msg": "ICICI Bank: KYC expired. Click link to update immediately.", "type": "Phishing", "expected": True},
    {"msg": "Your Paytm account has suspicious activity. Verify OTP: 123456", "type": "OTP Theft", "expected": True},
    {"msg": "Congratulations! You won Rs 50000 cashback from PhonePe.", "type": "Fake Reward", "expected": True},
    {"msg": "Your bank account will be frozen for non-compliance. Call: 9876543210", "type": "Threat Call", "expected": True},
    {"msg": "RBI compliance: Update Aadhaar details or face penalty.", "type": "Authority Fraud", "expected": True},
    {"msg": "Google Pay refund of Rs 2500. Share UPI ID to claim.", "type": "Refund Scam", "expected": True},
    {"msg": "Your card is blocked. Confirm CVV to unblock: XXXX-XXXX-XXXX-1234", "type": "CVV Theft", "expected": True},
    {"msg": "Immediate action required: Verify mobile number for bank security.", "type": "Info Harvest", "expected": True},
    {"msg": "Your HDFC credit limit increased! Confirm card details.", "type": "Credit Card Scam", "expected": True},
    {"msg": "Security alert: Unauthorized UPI transaction. Share PIN to reverse.", "type": "PIN Theft", "expected": True},
    {"msg": "Axis Bank: Your debit card expires today. Update now.", "type": "Urgency Scam", "expected": True},
    {"msg": "You have unclaimed FD maturity of Rs 1 lakh. Verify account number.", "type": "Fake FD", "expected": True},
    {"msg": "NEFT transfer failed. Re-enter banking password to retry.", "type": "Password Theft", "expected": True},
    
    # Shopping & E-commerce Scams (10)
    {"msg": "Amazon: Your Prime membership expires in 1 hour. Renew now.", "type": "Subscription Scam", "expected": True},
    {"msg": "Flipkart Mega Sale! Claim Rs 10000 voucher. Limited time.", "type": "Fake Voucher", "expected": True},
    {"msg": "Your COD order is pending. Pay Rs 99 to confirm delivery.", "type": "Fake Delivery", "expected": True},
    {"msg": "Congratulations! You are selected for iPhone 15 Pro. Pay shipping Rs 199.", "type": "Prize Scam", "expected": True},
    {"msg": "Order #12345 cancelled. Refund processing. Share bank details.", "type": "Refund Fraud", "expected": True},
    {"msg": "Myntra Sale: 90% off! Click link before stock ends.", "type": "Phishing Link", "expected": True},
    {"msg": "Your package is stuck at customs. Pay clearance fee Rs 500.", "type": "Customs Scam", "expected": True},
    {"msg": "Exclusive offer: Buy 1 Get 5 Free. Limited to first 100 customers.", "type": "Too Good Deal", "expected": True},
    {"msg": "Zomato Gold expiring! Renew for lifetime at 80% discount.", "type": "Fake Renewal", "expected": True},
    {"msg": "Swiggy: Free voucher of Rs 1000. Use code and enter card details.", "type": "Card Harvest", "expected": True},
    
    # Government & Official Scams (10)
    {"msg": "Income Tax Refund of Rs 45000 approved. Verify PAN card details.", "type": "Tax Refund", "expected": True},
    {"msg": "Aadhaar card will be deactivated. Update details immediately.", "type": "Aadhaar Scam", "expected": True},
    {"msg": "EPF withdrawal approved. Confirm UAN and bank account.", "type": "EPF Fraud", "expected": True},
    {"msg": "Legal notice: Pay fine of Rs 10000 within 24 hours or face arrest.", "type": "Legal Threat", "expected": True},
    {"msg": "Electricity bill overdue. Pay Rs 5000 now to avoid disconnection.", "type": "Utility Scam", "expected": True},
    {"msg": "Your LPG subsidy is pending. Share Aadhaar to claim Rs 3200.", "type": "Subsidy Fraud", "expected": True},
    {"msg": "COVID vaccine certificate expired. Renew by submitting Aadhaar.", "type": "Health Scam", "expected": True},
    {"msg": "Traffic E-Challan: Rs 2000 fine due. Pay now to avoid court.", "type": "Challan Scam", "expected": True},
    {"msg": "PAN-Aadhaar linking deadline today. Submit details urgently.", "type": "Deadline Scam", "expected": True},
    {"msg": "Voter ID inactive. Verify mobile number to reactivate.", "type": "Voter Fraud", "expected": True},
    
    # Job & Investment Scams (10)
    {"msg": "Congratulations! Selected for Google job. Pay Rs 5000 training fee.", "type": "Job Scam", "expected": True},
    {"msg": "Work from home: Earn Rs 50000/month. Registration fee Rs 2000.", "type": "WFH Fraud", "expected": True},
    {"msg": "Investment opportunity: Double your money in 30 days. Limited slots.", "type": "Ponzi Scheme", "expected": True},
    {"msg": "Your crypto wallet has $10000. Verify email to withdraw.", "type": "Crypto Scam", "expected": True},
    {"msg": "TCS joining letter ready. Pay verification charge Rs 3000.", "type": "Fake Offer", "expected": True},
    {"msg": "Part-time job: Rate products, earn Rs 500 per task. Register now.", "type": "Task Scam", "expected": True},
    {"msg": "Stock market tip: Buy XYZ shares today. 500% returns guaranteed.", "type": "Pump & Dump", "expected": True},
    {"msg": "Online survey: Earn Rs 10000 in 1 hour. Pay joining fee Rs 500.", "type": "Survey Scam", "expected": True},
    {"msg": "Claim your pension arrears of Rs 80000. Submit bank passbook copy.", "type": "Pension Fraud", "expected": True},
    {"msg": "Multi-level marketing: Invest Rs 10000, earn Rs 1 lakh monthly.", "type": "MLM Scam", "expected": True},
    
    # Legitimate Messages (5) - Should NOT be detected
    {"msg": "Hi, can we schedule a meeting tomorrow at 3 PM?", "type": "Normal Chat", "expected": False},
    {"msg": "Thanks for your help! I really appreciate it.", "type": "Gratitude", "expected": False},
    {"msg": "What time does the office open on Monday?", "type": "Query", "expected": False},
    {"msg": "Happy birthday! Hope you have a great day!", "type": "Greeting", "expected": False},
    {"msg": "The presentation looks good. Let's finalize it by Friday.", "type": "Work Discussion", "expected": False},
]

def test_honeypot(test_cases):
    """Run all test cases through honeypot"""
    headers = {'x-api-key': API_KEY, 'Content-Type': 'application/json'}
    results = {
        'total': len(test_cases),
        'correct': 0,
        'false_positives': 0,
        'false_negatives': 0,
        'by_type': defaultdict(lambda: {'total': 0, 'detected': 0, 'accuracy': 0}),
        'details': []
    }
    
    print("\n" + "="*80)
    print("  HONEYPOT SCAM DETECTION - 50 TEST PROBLEMS")
    print("="*80 + "\n")
    
    for idx, test in enumerate(test_cases, 1):
        msg = test['msg']
        expected = test['expected']
        scam_type = test['type']
        
        # Track by type
        results['by_type'][scam_type]['total'] += 1
        
        payload = {
            'sessionId': f'test-{idx}',
            'message': {
                'sender': 'scammer',
                'text': msg,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            },
            'conversationHistory': [],
            'metadata': {
                'channel': 'test',
                'language': 'english',
                'locale': 'IN'
            }
        }
        
        try:
            resp = requests.post(BASE_URL, json=payload, headers=headers, timeout=5)
            if resp.status_code == 200:
                result = resp.json()
                detected = result['scam_detected']
                confidence = result['confidence']
                
                # Determine correctness
                correct = (detected == expected)
                if correct:
                    results['correct'] += 1
                    results['by_type'][scam_type]['detected'] += 1
                    status = "✓ PASS"
                    color_code = "\033[92m"  # Green
                else:
                    if detected and not expected:
                        results['false_positives'] += 1
                        status = "✗ FALSE POSITIVE"
                    else:
                        results['false_negatives'] += 1
                        status = "✗ FALSE NEGATIVE"
                    color_code = "\033[91m"  # Red
                
                # Store details
                results['details'].append({
                    'test_num': idx,
                    'type': scam_type,
                    'message': msg[:50] + "..." if len(msg) > 50 else msg,
                    'expected': expected,
                    'detected': detected,
                    'confidence': confidence,
                    'correct': correct,
                    'status': status
                })
                
                # Print progress
                print(f"[{idx:2d}/50] {status:<20} | Conf: {confidence:.2f} | Type: {scam_type}")
                
            else:
                print(f"[{idx:2d}/50] ERROR: HTTP {resp.status_code}")
                
        except Exception as e:
            print(f"[{idx:2d}/50] ERROR: {str(e)[:50]}")
    
    # Calculate accuracy by type
    for scam_type, stats in results['by_type'].items():
        if stats['total'] > 0:
            stats['accuracy'] = (stats['detected'] / stats['total']) * 100
    
    return results

def print_summary(results):
    """Print detailed test summary"""
    print("\n\n" + "="*80)
    print("  TEST RESULTS SUMMARY")
    print("="*80 + "\n")
    
    # Overall Statistics
    accuracy = (results['correct'] / results['total']) * 100
    print(f"📊 Overall Performance:")
    print(f"   Total Tests:        {results['total']}")
    print(f"   Correct:            {results['correct']}")
    print(f"   Accuracy:           {accuracy:.1f}%")
    print(f"   False Positives:    {results['false_positives']}")
    print(f"   False Negatives:    {results['false_negatives']}")
    
    # Performance by Category
    print(f"\n📋 Performance by Category:")
    print("-" * 80)
    for scam_type, stats in sorted(results['by_type'].items(), key=lambda x: x[1]['accuracy'], reverse=True):
        accuracy_bar = "█" * int(stats['accuracy'] / 5)  # 20 chars max
        print(f"   {scam_type:<25} {stats['detected']}/{stats['total']:<3} {accuracy_bar:<20} {stats['accuracy']:.0f}%")
    
    # Failed Tests
    failed = [d for d in results['details'] if not d['correct']]
    if failed:
        print(f"\n⚠️  Failed Tests ({len(failed)}):")
        print("-" * 80)
        for fail in failed:
            print(f"   [{fail['test_num']:2d}] {fail['status']:<20} | {fail['type']:<20}")
            print(f"        Message: \"{fail['message']}\"")
            print(f"        Expected: {fail['expected']}, Got: {fail['detected']} (Conf: {fail['confidence']:.2f})")
            print()
    
    # Grade
    print("="*80)
    if accuracy >= 90:
        grade = "A+ EXCELLENT"
        emoji = "🏆"
    elif accuracy >= 80:
        grade = "A  VERY GOOD"
        emoji = "🥇"
    elif accuracy >= 70:
        grade = "B  GOOD"
        emoji = "🥈"
    elif accuracy >= 60:
        grade = "C  ACCEPTABLE"
        emoji = "🥉"
    else:
        grade = "F  NEEDS IMPROVEMENT"
        emoji = "⚠️"
    
    print(f"{emoji}  FINAL GRADE: {grade} - {accuracy:.1f}% Accuracy")
    print("="*80 + "\n")

if __name__ == "__main__":
    results = test_honeypot(TEST_SCAMS)
    print_summary(results)
    
    # Save detailed results
    with open('test_results_50.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Detailed results saved to: test_results_50.json\n")
