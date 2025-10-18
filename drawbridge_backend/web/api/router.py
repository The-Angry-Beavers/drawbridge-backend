from fastapi.routing import APIRouter

from drawbridge_backend.web.api import monitoring, users, tables

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(users.router)
api_router.include_router(tables.router)
