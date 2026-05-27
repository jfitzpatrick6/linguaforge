from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings

# Routers (currently stub implementations — real endpoints added in Phase 4)
from app.routers import (
    profile_router,
    lesson_router,
    curriculum_router,
    chat_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"[LinguaForge] Starting with model: {settings.AI_MODEL} @ {settings.AI_BASE_URL}")
    yield
    # Shutdown (future: close any pooled clients, etc.)


app = FastAPI(
    title="LinguaForge",
    description="Local-first AI Language Learning Tool",
    version="0.1.0",
    lifespan=lifespan,
)

# Mount routers
app.include_router(profile_router, prefix="/api", tags=["profile"])
app.include_router(lesson_router, prefix="/api", tags=["lessons"])
app.include_router(curriculum_router, prefix="/api", tags=["curriculum"])
app.include_router(chat_router, prefix="/api", tags=["chat"])


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "ai_model": settings.AI_MODEL,
        "ai_base_url": settings.AI_BASE_URL,
        "db_path": settings.DB_PATH,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)