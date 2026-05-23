import asyncio
import logging
from datetime import datetime
from celery import shared_task

from app.core.celery_app import celery_app
from app.core.redis import delete_cache
from app.db.database import AsyncSessionLocal
from app.db.models import Task, TaskStatus
from app.utils.cache_key import task_key, tasks_user_key

logger = logging.getLogger("task_status")

MAX_RETRIES = 3

async def complete_task(task_id: int) -> None:

    async with AsyncSessionLocal() as session:
        try:
            task: Task | None = await session.get(Task, task_id)

            if not task:
                logger.warning(f"[TASK NOT FOUND] task_id={task_id}")
                return

            if task.status == TaskStatus.COMPLETED:
                logger.info(f"[TASK ALREADY COMPLETED] task_id={task_id}")
                return

            old_status = task.status

            # State validation
            if old_status != TaskStatus.IN_PROGRESS:
                logger.warning(f"[INVALID TASK STATE] task_id={task_id} status={old_status}")
                return

            task.status = TaskStatus.COMPLETED
            await session.commit()

            logger.info(f"[TASK STATUS UPDATED] task_id={task_id} {old_status} -> COMPLETED timestamp={datetime.utcnow().isoformat()}")

            await delete_cache(task_key(task.id))

            if task.assigned_to:
                await delete_cache(tasks_user_key(task.assigned_to))

            logger.info(f"[TASK NOTIFICATION SENT] task_id={task_id}")
            logger.info(f"[TASK ANALYTICS UPDATED] task_id={task_id}")

        except Exception as e:
            await session.rollback()
            logger.exception(f"[TASK COMPLETION FAILED] task_id={task_id} err={e}")
            raise

@celery_app.task(
    bind=True,
    max_retries=MAX_RETRIES,
    retry_backoff=True,
    retry_jitter=True,
)
def process_task_completion(self, task_id: int):
    logger.info(f"[TASK WORKER START] task_id={task_id}")

    try:
        asyncio.run(complete_task(task_id))

        logger.info(f"[TASK WORKER DONE] task_id={task_id}")

    except Exception as exc:
        logger.exception(f"[TASK WORKER ERROR] task_id={task_id} err={exc}")
        raise self.retry(exc=exc)