# Honeypot Scam Detection API

AI-powered honeypot system for detecting and analyzing scam conversations with 96% accuracy.

## 🎯 Features

- **High-Accuracy Scam Detection** (96% on 50-test suite)
- **Gemini Pro AI Integration** (Free tier, no quotas)
- **Real-time Conversation Analysis**
- **Auto-Stop on Scam Detection**
- **Automatic TXT File Export** of detected scams
- **Web Chat Interface**
- **SQLite + CSV Persistence**
- **Intelligence Extraction** (phone numbers, links, tactics)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Gemini API Key (free from Google AI Studio)

### Installation

```bash
# Clone repository
git clone https://github.com/ayaanmalhotra7777/honeypotscam.git
cd honeypotscam

# Install dependencies
pip install -r requirements.txt

# Configure API key
# Create api.env file with:
API_KEY=your_gemini_api_key_here

# Run server
python main.py
```

### Access Points

- **Web Chat UI**: http://127.0.0.1:8000/chat
- **API Endpoint**: http://127.0.0.1:8000/api/honeypot
- **Health Check**: http://127.0.0.1:8000/health

## 📊 Performance

**Test Results (50 Problems)**:
- **Accuracy**: 96.0% (A+ Grade)
- **Scam Detection**: 48/50
- **False Positives**: 0
- **False Negatives**: 2

**Detection Categories (100% accuracy)**:
- Banking/UPI scams (KYC, blocked accounts, OTP theft)
- E-commerce scams (COD delivery, customs, fake vouchers)
- Job/Investment scams (WFH fraud, crypto, MLM, Ponzi schemes)
- Government scams (tax refund, Aadhaar, legal threats)

## 🔧 API Usage

### Request Format

```bash
curl -X POST http://127.0.0.1:8000/api/honeypot \
  -H "Content-Type: application/json" \
  -H "x-api-key: Ayaanmalhotra@1" \
  -d '{
    "sessionId": "test-session-1",
    "message": {
      "sender": "scammer",
      "text": "Your UPI will be blocked in 24 hours. Update KYC now.",
      "timestamp": "2026-02-05T10:00:00Z"
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'
```

### Response Format

```json
{
  "status": "success",
  "reply": "Oh no! What do I need to do?",
  "scam_detected": true,
  "confidence": 1.0,
  "extracted_intelligence": {
    "phone_numbers": [],
    "links": [],
    "bank_accounts": [],
    "tactics": ["urgency", "account_threat", "kyc_verification"]
  },
  "message_count": 1,
  "callback_sent": true
}
```

## 🗂️ Project Structure

```
honeypotscam/
├── main.py                 # FastAPI server & orchestration
├── agent.py                # Gemini AI agent for victim responses
├── scam_detector.py        # 90+ keyword detection engine
├── memory.py               # In-memory session management
├── db.py                   # SQLite persistence
├── logger.py               # CSV event logging
├── extractor.py            # Intelligence extraction
├── callback.py             # Callback notifications
├── generate_training_dataset.py  # Test scenario generator
├── test_50_problems.py     # Comprehensive test suite
├── requirements.txt        # Python dependencies
├── api.env                 # API key configuration
├── static/
│   └── chat.html          # Web chat interface
├── data/
│   └── honeypot.db        # SQLite database
├── logs/
│   └── honeypot_events.csv  # Event logs
└── scam_conversations/    # Auto-saved scam TXT files
```

## 🎨 Web Chat Interface

The web UI automatically:
1. Detects scam messages with confidence scoring
2. Stops the chat when scam is confirmed
3. Saves conversation to `scam_conversations/` folder
4. Displays detection results in real-time

## 🧪 Testing

Run the 50-problem test suite:

```bash
python test_50_problems.py
```

Generate training dataset:

```bash
python generate_training_dataset.py
```

## 🔐 Security

- API key authentication via `x-api-key` header
- No sensitive data in git repository (.gitignore configured)
- Session isolation
- Automatic scam conversation archival

## 📝 Configuration

Edit `api.env`:

```env
API_KEY=your_gemini_api_key_here
```

## 🛠️ Tech Stack

- **FastAPI** - REST API framework
- **Google Gemini Pro** - AI language model (free tier)
- **SQLite** - Persistence layer
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

## 📈 Scam Detection Weights

The detector uses 90+ weighted keywords:
- **Critical** (3.0): "will be blocked", "update kyc", "cvv", "double your money"
- **High** (2.5-2.8): "blocked", "otp", "kyc", "aadhaar", "registration fee"
- **Medium** (2.0-2.5): "urgent", "verify", "refund", "invest"
- **Low** (1.5-2.0): "order", "delivery", "earn", "discount"

Detection threshold: **30% confidence**

## 🎯 Use Cases

- **Training Data Generation** for ML models
- **Scam Pattern Analysis** for research
- **Real-time Fraud Detection** systems
- **Security Awareness Training** scenarios
- **Academic Research** in cybersecurity

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional scam categories (romance, tech support, lottery)
- Multi-language support expansion
- ML-based confidence scoring
- Real-time dashboard analytics

## 📄 License

MIT License - See LICENSE file for details

## 👤 Author

**Ayaan Malhotra**
- GitHub: [@ayaanmalhotra7777](https://github.com/ayaanmalhotra7777)

## 🙏 Acknowledgments

- Google Gemini AI for free tier API access
- FastAPI community for excellent documentation
- VS Code Copilot for development assistance

---

**⚠️ Disclaimer**: This honeypot is for educational and research purposes only. Use responsibly and comply with all applicable laws and regulations.
