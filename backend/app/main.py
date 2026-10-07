"""
AI-Powered Fitness Coach — FastAPI Backend Application Main Entry Point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.api.v1 import api_v1_router
from app.services.supabase_client import get_db

setup_logging()
logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: test database connection
    logger.info("Initializing AI-Powered Fitness Coach Backend...")
    db = get_db()
    logger.info("Database client initialized successfully.")
    yield
    # Shutdown
    logger.info("Shutting down backend...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Real-time Computer Vision & Deep Learning Fitness Form Analysis and Telemetry Engine.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for React Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    return response


# Include API v1 routes
app.include_router(api_v1_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0"
    }


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "AI-Powered Fitness Coach API is running.",
        "docs": "/docs",
        "health": "/health",
        "api_v1": "/api/v1"
    }
