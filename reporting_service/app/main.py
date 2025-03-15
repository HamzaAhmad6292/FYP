from fastapi import FastAPI
from routers import analysis
from core.config import settings
from fastapi.middleware.cors import CORSMiddleware
import logging
from routers import chat  # Add this import


logging.basicConfig(level=logging.INFO)
app = FastAPI(title="AI Business Analyst")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}