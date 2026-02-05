#!/usr/bin/env python3
"""
100 Test Cases - Comprehensive Scam Detection Test Suite
Tests honeypot against 100 real-world scam scenarios
"""

import requests
import json
from datetime import datetime
from collections import defaultdict
import time

API_KEY = 'Ayaanmalhotra@1'
BASE_URL = 'https://elegant-rejoicing-production-76b7.up.railway.app/api/honeypot'

# 100 Real-World Scam Test Cases
TEST_SCAMS = [
    # Banking & UPI Scams (20)
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
    {"msg": "Your account has limited tries left. Verify credentials now or account locked.", "type": "Account Lockout", "expected": True},
    {"msg": "New device detected. Please authenticate immediately to secure your account.", "type": "Device Auth Scam", "expected": True},
    {"msg": "Unusual activity on your bank account. Update security information urgently.", "type": "Security Scam", "expected": True},
    {"msg": "Claim your insurance settlement. Provide banking details for transfer.", "type": "Insurance Fraud", "expected": True},
    {"msg": "Your GST refund of Rs 15000 is ready. Confirm PAN to process.", "type": "Tax Fraud", "expected": True},
    
    # Shopping & E-commerce Scams (20)
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
    {"msg": "Nykaa Beauty: Exclusive access sale for loyal members. Verify account now.", "type": "E-commerce Phishing", "expected": True},
    {"msg": "Your recent purchase needs confirmation. Update payment method immediately.", "type": "Payment Verification", "expected": True},
    {"msg": "Free gift card worth Rs 5000 waiting for you. Claim now.", "type": "Gift Card Scam", "expected": True},
    {"msg": "URGENT: Your order needs additional verification. Click here to confirm.", "type": "Order Verification", "expected": True},
    {"msg": "Track your delivery package - enter your credentials to see status.", "type": "Tracking Phishing", "expected": True},
    {"msg": "You have a pending refund. Authorize the transaction to proceed.", "type": "Refund Authorization", "expected": True},
    {"msg": "Limited stock alert! Complete purchase within 10 minutes or lose deal.", "type": "Urgency Sale", "expected": True},
    {"msg": "Your wishlist items are on sale. Don't miss out - purchase now!", "type": "FOMO Scam", "expected": True},
    {"msg": "Free shipping voucher activated. Use code xyz at checkout.", "type": "Fake Code", "expected": True},
    {"msg": "Unlocked exclusive beta sale for VIP members. Early bird special pricing.", "type": "VIP Scam", "expected": True},
    
    # Government & Official Scams (20)
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
    {"msg": "Your passport requires urgent renewal. Complete verification to proceed.", "type": "Passport Scam", "expected": True},
    {"msg": "Property tax settlement approved. Provide Aadhaar for fund transfer.", "type": "Property Fraud", "expected": True},
    {"msg": "Driver's license renewal notice. Submit documents before deadline.", "type": "License Renewal", "expected": True},
    {"msg": "Loan pre-approval from government scheme. Register with contact details.", "type": "Loan Scam", "expected": True},
    {"msg": "DVAT notice: Settle outstanding dues within 7 days.", "type": "Tax Notice", "expected": True},
    {"msg": "Your insurance claim is approved. Verify policy details to claim.", "type": "Insurance Claim", "expected": True},
    {"msg": "Public service commission interview selected. Confirm participation urgently.", "type": "Job Selection Scam", "expected": True},
    {"msg": "Marriage registration approval pending. Submit documents for finalization.", "type": "Marriage Registration", "expected": True},
    {"msg": "Water bill pending. Pay immediately to avoid supply disconnection.", "type": "Utility Bill", "expected": True},
    {"msg": "Municipal property tax waiver available. Apply now with document verification.", "type": "Tax Waiver", "expected": True},
    
    # Job & Investment Scams (20)
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
    {"msg": "Forex trading opportunity: Easy money with expert guidance. Sign up now.", "type": "Forex Scam", "expected": True},
    {"msg": "Real estate investment: Guaranteed 200% returns in 6 months.", "type": "Real Estate Scam", "expected": True},
    {"msg": "You've been selected for internship program. Pay Rs 2000 registration.", "type": "Internship Fraud", "expected": True},
    {"msg": "Amazon/Flipkart hiring work from home. Register with credentials.", "type": "Fake Hiring", "expected": True},
    {"msg": "Earn money by completing online tasks. No investment required? Sign up!", "type": "Task Fraud", "expected": True},
    {"msg": "Forex signals group: Join now for exclusive trading tips. Limited members.", "type": "Signal Group", "expected": True},
    {"msg": "Cryptocurrency mining opportunity. Invest minimum Rs 10000 today.", "type": "Mining Scam", "expected": True},
    {"msg": "Binary options trading platform. Guaranteed profits every day.", "type": "Options Scam", "expected": True},
    {"msg": "Premium coaching: Learn to earn money online. Limited batch availability.", "type": "Coaching Scam", "expected": True},
    {"msg": "Startup investment opportunity. 400% return in 3 months or money back.", "type": "Startup Scam", "expected": True},
    
    # Legitimate Messages (20) - Should NOT be detected as scams
    {"msg": "Hi, can we schedule a meeting tomorrow at 3 PM?", "type": "Normal Chat", "expected": False},
    {"msg": "Thanks for your help! I really appreciate it.", "type": "Gratitude", "expected": False},
    {"msg": "What time does the office open on Monday?", "type": "Query", "expected": False},
    {"msg": "Happy birthday! Hope you have a great day!", "type": "Greeting", "expected": False},
    {"msg": "The presentation looks good. Let's finalize it by Friday.", "type": "Work Discussion", "expected": False},
    {"msg": "Can you send me the project files by end of day?", "type": "Work Request", "expected": False},
    {"msg": "Let me know if you need any clarification on the proposal.", "type": "Professional", "expected": False},
    {"msg": "I'm available for coffee this weekend. How about Saturday?", "type": "Social", "expected": False},
    {"msg": "Your reservation is confirmed for 2 persons at 7 PM.", "type": "Booking", "expected": False},
    {"msg": "We have received your order. Thank you for shopping with us.", "type": "Order Confirmation", "expected": False},
    {"msg": "The weather looks great today. Perfect for a picnic!", "type": "Casual Chat", "expected": False},
    {"msg": "I've completed the report you requested last week.", "type": "Completion Notice", "expected": False},
    {"msg": "See you at the team lunch tomorrow. Don't be late!", "type": "Reminder", "expected": False},
    {"msg": "Your account balance is Rs 50000. Have a great day!", "type": "Account Info", "expected": False},
    {"msg": "Feedback: Great customer service. Will recommend to friends.", "type": "Positive Review", "expected": False},
    {"msg": "Can I get your honest opinion on this product?", "type": "Feedback Request", "expected": False},
    {"msg": "Let's connect on LinkedIn. Looking forward to collaborating.", "type": "Networking", "expected": False},
    {"msg": "Just landed at the airport. Heading to the office.", "type": "Travel Update", "expected": False},
    {"msg": "Congratulations on your promotion! Well deserved.", "type": "Congratulations", "expected": False},
    {"msg": "The meeting scheduled for today has been postponed to next week.", "type": "Schedule Change", "expected": False},
]

def test_honeypot(test_cases):
    """Run all test cases through honeypot"""
    headers = {'x-api-key': API_KEY, 'Content-Type': 'application/json'}
    results = {
        'total': len(test_cases),
        'correct': 0,
        'false_positives': 0,
        'false_negatives': 0,
        'true_positives': 0,
        'true_negatives': 0,
        'by_type': defaultdict(lambda: {'total': 0, 'correct': 0, 'accuracy': 0}),
        'details': [],
        'timestamp': datetime.now().isoformat(),
        'test_duration': 0
    }
    
    print("\n" + "="*90)
    print("  🚨 HONEYPOT SCAM DETECTION - 100 TEST CASES 🚨")
    print("="*90 + "\n")
    
    start_time = time.time()
    
    for idx, test in enumerate(test_cases, 1):
        msg = test['msg']
        expected = test['expected']
        scam_type = test['type']
        
        # Track by type
        results['by_type'][scam_type]['total'] += 1
        
        payload = {
            'sessionId': f'test-{idx}',
            'message': {
                'sender': 'scammer' if expected else 'user',
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
            resp = requests.post(BASE_URL, json=payload, headers=headers, timeout=10)
            if resp.status_code == 200:
                result = resp.json()
                detected = result.get('scam_detected', False)
                confidence = result.get('confidence', 0.0)
                
                # Determine correctness
                correct = (detected == expected)
                if correct:
                    results['correct'] += 1
                    results['by_type'][scam_type]['correct'] += 1
                    if expected:
                        results['true_positives'] += 1
                        status = "✓ TP"
                        color_code = "\033[92m"  # Green
                    else:
                        results['true_negatives'] += 1
                        status = "✓ TN"
                        color_code = "\033[92m"  # Green
                else:
                    if detected and not expected:
                        results['false_positives'] += 1
                        status = "✗ FP"
                        color_code = "\033[91m"  # Red
                    else:
                        results['false_negatives'] += 1
                        status = "✗ FN"
                        color_code = "\033[93m"  # Yellow
                
                # Store details
                results['details'].append({
                    'test_num': idx,
                    'type': scam_type,
                    'message': msg[:60] + "..." if len(msg) > 60 else msg,
                    'expected': expected,
                    'detected': detected,
                    'confidence': round(confidence, 3),
                    'correct': correct,
                    'status': status
                })
                
                # Print progress
                msg_preview = msg[:40].replace('\n', ' ')
                print(f"[{idx:3d}/100] {status} | Conf: {confidence:.2f} | Type: {scam_type:<25} | \"{msg_preview}\"")
                
            else:
                print(f"[{idx:3d}/100] ERROR: HTTP {resp.status_code}")
                
        except Exception as e:
            print(f"[{idx:3d}/100] ERROR: {str(e)[:50]}")
    
    # Calculate metrics
    end_time = time.time()
    results['test_duration'] = round(end_time - start_time, 2)
    
    for scam_type, stats in results['by_type'].items():
        if stats['total'] > 0:
            stats['accuracy'] = round((stats['correct'] / stats['total']) * 100, 1)
    
    return results

def calculate_metrics(results):
    """Calculate additional metrics"""
    tp = results['true_positives']
    tn = results['true_negatives']
    fp = results['false_positives']
    fn = results['false_negatives']
    
    # Precision: of all positive predictions, how many were correct
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    
    # Recall: of all actual positives, how many did we detect
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    
    # F1 Score
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        'accuracy': (results['correct'] / results['total']) * 100,
        'precision': precision * 100,
        'recall': recall * 100,
        'f1_score': f1 * 100
    }

def print_summary(results):
    """Print detailed test summary"""
    metrics = calculate_metrics(results)
    
    print("\n\n" + "="*90)
    print("  📊 TEST RESULTS SUMMARY - 100 CASES")
    print("="*90 + "\n")
    
    # Overall Statistics
    print(f"⏱️  Test Duration: {results['test_duration']} seconds\n")
    
    print(f"📈 Overall Performance:")
    print(f"   Total Tests:        {results['total']}")
    print(f"   Correct:            {results['correct']}")
    print(f"   Incorrect:          {results['total'] - results['correct']}")
    print(f"\n   True Positives:     {results['true_positives']} (Correctly detected scams)")
    print(f"   True Negatives:     {results['true_negatives']} (Correctly passed legitimate)")
    print(f"   False Positives:    {results['false_positives']} (Wrongly flagged legitimate)")
    print(f"   False Negatives:    {results['false_negatives']} (Missed scams)")
    
    # Metrics
    print(f"\n📊 Performance Metrics:")
    print(f"   Accuracy:           {metrics['accuracy']:.2f}%")
    print(f"   Precision:          {metrics['precision']:.2f}%")
    print(f"   Recall (Sensitivity): {metrics['recall']:.2f}%")
    print(f"   F1 Score:           {metrics['f1_score']:.2f}%")
    
    # Performance by Category
    print(f"\n📋 Performance by Category:")
    print("-" * 90)
    print(f"{'Category':<30} {'Correct':<10} {'Total':<10} {'Accuracy':<15} {'Bar':<20}")
    print("-" * 90)
    for scam_type, stats in sorted(results['by_type'].items(), key=lambda x: x[1]['accuracy'], reverse=True):
        accuracy_bar = "█" * int(stats['accuracy'] / 5)  # 20 chars max
        print(f"{scam_type:<30} {stats['correct']:<10} {stats['total']:<10} {stats['accuracy']:>6.1f}%        {accuracy_bar:<20}")
    
    # Failed Tests
    failed = [d for d in results['details'] if not d['correct']]
    if failed:
        print(f"\n⚠️  Failed Tests ({len(failed)}):")
        print("-" * 90)
        for fail in failed[:20]:  # Show first 20 failures
            print(f"   [{fail['test_num']:3d}] {fail['status']:<5} | Expected: {str(fail['expected']):<5} | Got: {str(fail['detected']):<5} | Conf: {fail['confidence']:.2f}")
            print(f"        Type: {fail['type']:<25} | Message: \"{fail['message']}\"")
        if len(failed) > 20:
            print(f"   ... and {len(failed) - 20} more failures")
    
    # Grade
    print("\n" + "="*90)
    accuracy = metrics['accuracy']
    if accuracy >= 95:
        grade = "A++ OUTSTANDING"
        emoji = "🏆"
    elif accuracy >= 90:
        grade = "A+ EXCELLENT"
        emoji = "🥇"
    elif accuracy >= 85:
        grade = "A  VERY GOOD"
        emoji = "🥈"
    elif accuracy >= 80:
        grade = "B  GOOD"
        emoji = "🥉"
    elif accuracy >= 70:
        grade = "C  ACCEPTABLE"
        emoji = "👍"
    else:
        grade = "F  NEEDS IMPROVEMENT"
        emoji = "⚠️"
    
    print(f"\n{emoji}  FINAL GRADE: {grade}")
    print(f"    Overall Accuracy: {accuracy:.2f}%")
    print("="*90 + "\n")
    
    return metrics

if __name__ == "__main__":
    print("Starting 100-case honeypot test suite...\n")
    print("Make sure the FastAPI server is running on http://127.0.0.1:8000/api/honeypot\n")
    
    results = test_honeypot(TEST_SCAMS)
    metrics = print_summary(results)
    
    # Save detailed results
    with open('test_results_100.json', 'w') as f:
        json.dump({
            'results': results,
            'metrics': metrics
        }, f, indent=2)
    
    print(f"💾 Detailed results saved to: test_results_100.json\n")
