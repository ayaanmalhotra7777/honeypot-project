"""Minimal test application to diagnose Railway 502 error"""

from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/")
async def root():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "message": "Test app working"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("test_app:app", host="0.0.0.0", port=8000, reload=False)
