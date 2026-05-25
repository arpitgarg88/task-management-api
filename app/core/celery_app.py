from celery import Celery
from app.core.config import settings

"""
Celery application configuration.

Defines:
- Redis broker/backend
- task routing
- queue configuration
- worker rate limits
"""

celery_app = Celery(
    "task_manager",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.task_routes = {
    "app.tasks.process_task_completion": {"queue": "task_completion_queue"},
}

celery_app.conf.task_annotations = {
    "*": {"rate_limit": "10/s"}
}