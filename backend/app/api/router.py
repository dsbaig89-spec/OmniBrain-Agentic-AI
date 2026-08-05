from fastapi import APIRouter
from backend.app.api.routes import health, upload ,search

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(upload.router)
api_router.include_router(search.router)