"""Minimal API to test Railway deployment"""

import sys
import os
from fastapi import FastAPI
from datetime import datetime

sys.stdout.write("[MINIMAL] Starting up...\n")
sys.stdout.flush()

# Set API key env vars
os.environ['API_KEY'] = os.getenv('API_KEY', 'test')
os.environ['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY', 'test')

sys.stdout.write("[MINIMAL] Creating FastAPI app...\n")
sys.stdout.flush()

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Minimal API OK", "timestamp": datetime.now().isoformat()}

@app.get("/health")
async def health():
    return {"status": "healthy"}

sys.stdout.write("[MINIMAL] App ready!\n")
sys.stdout.flush()
