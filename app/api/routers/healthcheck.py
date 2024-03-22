from fastapi import APIRouter

from app.api.models.healthcheck import HealthCheck
from app.config import settings

health_check_router = APIRouter(prefix="/healthcheck", tags=["Healthcheck"])


@health_check_router.get("/")
def get_health_check() -> HealthCheck:
    """
    Запрос статуса сервиса
    """
    return HealthCheck(
        version=settings.VERSION,
        service=settings.NAME,
        status=True,
    )
