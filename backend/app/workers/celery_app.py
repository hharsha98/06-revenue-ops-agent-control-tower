from celery import Celery

from backend.app.core.config import settings

celery_app = Celery(
    "revenueops",
    broker=settings.redis_url,
    backend=settings.redis_url,
)


@celery_app.task(name="revenueops.healthcheck")
def healthcheck() -> str:
    return "ok"

