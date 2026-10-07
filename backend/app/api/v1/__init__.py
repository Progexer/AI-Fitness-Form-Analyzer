"""
AI-Powered Fitness Coach — API v1 Router Aggregator
"""

from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.videos import router as videos_router
from app.api.v1.analysis import router as analysis_router
from app.api.v1.models import router as models_router
from app.api.v1.reports import router as reports_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(videos_router)
api_v1_router.include_router(analysis_router)
api_v1_router.include_router(models_router)
api_v1_router.include_router(reports_router)

__all__ = ["api_v1_router"]
