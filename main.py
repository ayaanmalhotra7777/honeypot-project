"""Honeypot API - Minimal working version"""

import os
import sys
from fastapi import FastAPI
from datetime import datetime

# Set API key env vars
os.environ['API_KEY'] = os.getenv('API_KEY', 'test')
os.environ['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY', 'test')

print("Creating FastAPI app...")
sys.stdout.flush()

app = FastAPI(title="Honeypot API")

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Honeypot",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "Honeypot",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/honeypot")
def honeypot_test():
    return {
        "message": "API is working",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/honeypot")
def honeypot_post(data: dict = None):
    return {
        "message": "POST received",
        "data": data,
        "timestamp": datetime.now().isoformat()
    }

print("App initialized!")
sys.stdout.flush()
