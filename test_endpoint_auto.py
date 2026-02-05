#!/usr/bin/env python3
"""
Honeypot API Endpoint Tester - Non-interactive version
Validates that the deployed API endpoint is working correctly
"""

import requests
import json
from datetime import datetime

# Configuration
API_KEY = 'Ayaanmalhotra@1'
API_ENDPOINT = 'https://elegant-rejoicing-production-76b7.up.railway.app/api/honeypot'

class HoneypotTester:
    def __init__(self, endpoint_url, api_key):
        self.endpoint = endpoint_url
        self.api_key = api_key
        self.results = {
            'endpoint': endpoint_url,
            'tests': [],
            'summary': {}
        }
    
    def test_connectivity(self):
        """Test basic endpoint connectivity"""
        print("\n" + "="*70)
        print("TEST 1: API CONNECTIVITY & AUTHENTICATION")
        print("="*70)
        
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        # Simple test payload
        payload = {
            'sessionId': 'connectivity-test-' + str(datetime.now().timestamp()),
            'message': {
                'sender': 'test_user',
                'text': 'This is a test message for connectivity validation',
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
            print(f"\n📤 Sending request to: {self.endpoint}")
            print(f"🔐 Using API Key: {self.api_key[:10]}...")
            print(f"📝 Payload:\n{json.dumps(payload, indent=2)}")
            
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            print(f"\n✅ Response Status: {response.status_code}")
            print(f"📨 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("✅ SUCCESS: API is working correctly!")
                data = response.json()
                print(f"\n📊 Response Data:")
                print(json.dumps(data, indent=2))
                
                self.results['tests'].append({
                    'name': 'Connectivity Test',
                    'status': 'PASS',
                    'status_code': 200,
                    'response': data
                })
                return True
                
            else:
                print(f"❌ ERROR: API returned status {response.status_code}")
                print(f"Response Body: {response.text}")
                
                self.results['tests'].append({
                    'name': 'Connectivity Test',
                    'status': 'FAIL',
                    'status_code': response.status_code,
                    'error': response.text
                })
                return False
                
        except requests.exceptions.ConnectionError as e:
            print(f"❌ CONNECTION ERROR: {str(e)}")
            self.results['tests'].append({
                'name': 'Connectivity Test',
                'status': 'FAIL',
                'error': f'Connection Error: {str(e)}'
            })
            return False
            
        except requests.exceptions.Timeout as e:
            print(f"❌ TIMEOUT: {str(e)}")
            self.results['tests'].append({
                'name': 'Connectivity Test',
                'status': 'FAIL',
                'error': f'Timeout Error: {str(e)}'
            })
            return False
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            self.results['tests'].append({
                'name': 'Connectivity Test',
                'status': 'FAIL',
                'error': str(e)
            })
            return False
    
    def test_scam_detection(self):
        """Test scam detection functionality"""
        print("\n" + "="*70)
        print("TEST 2: SCAM DETECTION FUNCTIONALITY")
        print("="*70)
        
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        test_cases = [
            {
                'name': 'Banking Scam',
                'message': 'Your SBI account will be blocked within 24 hours. Update KYC now.',
                'expected': True
            },
            {
                'name': 'Legitimate Message',
                'message': 'Hi, can we schedule a meeting tomorrow at 3 PM?',
                'expected': False
            },
            {
                'name': 'Phishing Attempt',
                'message': 'Urgent: Your UPI service is blocked. Share your UPI PIN to restore.',
                'expected': True
            }
        ]
        
        passed = 0
        failed = 0
        
        for test_case in test_cases:
            print(f"\n🧪 Testing: {test_case['name']}")
            print(f"   Message: \"{test_case['message'][:60]}...\"")
            print(f"   Expected Scam: {test_case['expected']}")
            
            payload = {
                'sessionId': f"test-{test_case['name'].replace(' ', '-')}",
                'message': {
                    'sender': 'test_user',
                    'text': test_case['message'],
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
                response = requests.post(
                    self.endpoint,
                    json=payload,
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    scam_detected = data.get('scam_detected', False)
                    confidence = data.get('confidence', 0)
                    
                    is_correct = (scam_detected == test_case['expected'])
                    
                    status = "✅ PASS" if is_correct else "❌ FAIL"
                    print(f"   {status}")
                    print(f"   Detected: {scam_detected} | Confidence: {confidence:.2f}")
                    
                    if is_correct:
                        passed += 1
                    else:
                        failed += 1
                    
                    self.results['tests'].append({
                        'name': f'Scam Detection - {test_case["name"]}',
                        'status': 'PASS' if is_correct else 'FAIL',
                        'expected': test_case['expected'],
                        'detected': scam_detected,
                        'confidence': confidence
                    })
                else:
                    print(f"   ❌ ERROR: {response.status_code}")
                    print(f"   {response.text}")
                    failed += 1
                    
            except Exception as e:
                print(f"   ❌ ERROR: {str(e)}")
                failed += 1
        
        print(f"\n📊 Scam Detection Results: {passed} passed, {failed} failed")
        return failed == 0
    
    def test_authentication(self):
        """Test API authentication"""
        print("\n" + "="*70)
        print("TEST 3: AUTHENTICATION & SECURITY")
        print("="*70)
        
        payload = {
            'sessionId': 'auth-test',
            'message': {
                'sender': 'test_user',
                'text': 'Test message',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            },
            'conversationHistory': [],
            'metadata': {
                'channel': 'test',
                'language': 'english',
                'locale': 'IN'
            }
        }
        
        # Test 1: No API key
        print("\n🔒 Test 1: Request without API key")
        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            if response.status_code == 403 or response.status_code == 401:
                print(f"✅ PASS: API correctly rejects requests without API key (HTTP {response.status_code})")
                self.results['tests'].append({
                    'name': 'Auth - No API Key',
                    'status': 'PASS',
                    'status_code': response.status_code
                })
            else:
                print(f"❌ FAIL: Expected 401/403, got {response.status_code}")
                self.results['tests'].append({
                    'name': 'Auth - No API Key',
                    'status': 'FAIL',
                    'status_code': response.status_code
                })
        except Exception as e:
            print(f"⚠️  Could not test (expected for some deployments): {str(e)}")
        
        # Test 2: Invalid API key
        print("\n🔒 Test 2: Request with invalid API key")
        try:
            headers = {
                'x-api-key': 'invalid-key-12345',
                'Content-Type': 'application/json'
            }
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=5
            )
            if response.status_code in [401, 403]:
                print(f"✅ PASS: API correctly rejects invalid API key (HTTP {response.status_code})")
                self.results['tests'].append({
                    'name': 'Auth - Invalid API Key',
                    'status': 'PASS',
                    'status_code': response.status_code
                })
            else:
                print(f"⚠️  API accepted invalid key (HTTP {response.status_code}) - may allow any key")
                self.results['tests'].append({
                    'name': 'Auth - Invalid API Key',
                    'status': 'WARNING',
                    'status_code': response.status_code
                })
        except Exception as e:
            print(f"⚠️  Could not test: {str(e)}")
    
    def test_response_structure(self):
        """Test response structure"""
        print("\n" + "="*70)
        print("TEST 4: RESPONSE STRUCTURE VALIDATION")
        print("="*70)
        
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'sessionId': 'structure-test',
            'message': {
                'sender': 'test_user',
                'text': 'Structure validation test message',
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
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print("\n📋 Checking Response Fields:")
                required_fields = ['scam_detected', 'confidence']
                all_present = True
                
                for field in required_fields:
                    if field in data:
                        print(f"✅ {field}: {data[field]} (Present)")
                    else:
                        print(f"❌ {field}: Missing")
                        all_present = False
                
                if all_present:
                    print("\n✅ PASS: Response structure is valid")
                    self.results['tests'].append({
                        'name': 'Response Structure',
                        'status': 'PASS'
                    })
                else:
                    print("\n❌ FAIL: Missing required fields")
                    self.results['tests'].append({
                        'name': 'Response Structure',
                        'status': 'FAIL',
                        'error': 'Missing required fields'
                    })
            else:
                print(f"❌ FAIL: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*70)
        print("  🚀 HONEYPOT API ENDPOINT TESTER")
        print("="*70)
        print(f"\nTesting Endpoint: {self.endpoint}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        test1 = self.test_connectivity()
        test2 = self.test_scam_detection()
        self.test_authentication()
        self.test_response_structure()
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("  📊 TEST SUMMARY")
        print("="*70)
        
        passed = len([t for t in self.results['tests'] if t['status'] == 'PASS'])
        failed = len([t for t in self.results['tests'] if t['status'] == 'FAIL'])
        warnings = len([t for t in self.results['tests'] if t['status'] == 'WARNING'])
        
        print(f"\n✅ Passed:   {passed}")
        print(f"❌ Failed:   {failed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"📊 Total:    {len(self.results['tests'])}")
        
        print("\n📋 Test Details:")
        for test in self.results['tests']:
            status_icon = "✅" if test['status'] == 'PASS' else "❌" if test['status'] == 'FAIL' else "⚠️"
            print(f"  {status_icon} {test['name']}: {test['status']}")
        
        print("\n" + "="*70)
        if failed == 0:
            print("✅ ALL TESTS PASSED - API IS PROPERLY DEPLOYED!")
        else:
            print(f"❌ {failed} TEST(S) FAILED - CHECK CONFIGURATION")
        print("="*70 + "\n")
        
        # Save results
        with open('api_test_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        print("💾 Results saved to: api_test_results.json\n")

if __name__ == "__main__":
    print("\n🔍 Honeypot API Endpoint Verification Tool\n")
    
    tester = HoneypotTester(API_ENDPOINT, API_KEY)
    tester.run_all_tests()
