from fastapi import FastAPI

from app.api.routes.admin import router as admin_router
from app.api.routes.gateway import router as gateway_router
from app.api.routes.health import router as health_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Enterprise AI Security Gateway MVP for Azure OpenAI / Azure AI Foundry",
)

app.include_router(health_router, tags=["health"])
app.include_router(gateway_router, prefix="/api/v1", tags=["gateway"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])
