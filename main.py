from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core import database
from app.routers import api_router
from app.core.config import settings  # Updated import

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB
    await database.init_db()
    yield
    # Shutdown: Clean up
    await database.close_db()

app = FastAPI(
    title="LinguaForge",
    description="Local-first AI Language Learning Tool",
    version="0.1.0",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to LinguaForge!"}

@app.get("/health")
async def health():
    return {"status": "healthy", "model": settings.AI_MODEL}

