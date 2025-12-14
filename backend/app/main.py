"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.api.routes import (
    documents,
    health,
    search,
    chat,
    osint,
    canvas,
    patterns,
    models,
    tts,
)
from app.utils.logger import logger
from app.middleware.security import RateLimitMiddleware, SecurityHeadersMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Research Tool API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Default embedding provider: {settings.DEFAULT_EMBEDDING_PROVIDER}")
    logger.info(f"Default LLM provider: {settings.DEFAULT_LLM_PROVIDER}")

    # Initialize database
    init_db()
    logger.info("Database initialized")

    yield

    # Shutdown
    logger.info("Shutting down Research Tool API...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Privacy-focused local research tool with AI-powered document analysis",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security middlewares
app.add_middleware(SecurityHeadersMiddleware)
# More relaxed rate limit for development (1000 requests per minute)
# For production, reduce this to 100 requests per minute
app.add_middleware(RateLimitMiddleware, calls=1000, period=60)

# Include routers
app.include_router(health.router)
app.include_router(documents.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(osint.router, prefix="/api")
app.include_router(canvas.router, prefix="/api")
app.include_router(patterns.router, prefix="/api")
app.include_router(models.router, prefix="/api")
app.include_router(tts.router, prefix="/api")


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Argus Intelligence Platform API",
        "version": "1.0.0",
        "tagline": "All-Seeing Intelligence",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
