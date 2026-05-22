from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(
    title="LinguaForge",
    description="Local-first AI Language Learning Tool",
    version="0.1.0"
)

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "ai_model": settings.AI_MODEL
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)