"""API v1 router."""

from fastapi import APIRouter

from src.api.v1.endpoints.debug import router as debug_router
from src.api.v1.endpoints.genome import router as genome_router
from src.api.v1.endpoints.health import router as health_router

api_v1_router = APIRouter()
api_v1_router.include_router(health_router)
api_v1_router.include_router(genome_router)
api_v1_router.include_router(debug_router)
