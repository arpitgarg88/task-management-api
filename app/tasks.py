import asyncio
import logging

from app.core.celery_app import celery_app
from app.db.database import AsyncSessionLocal
from app.db.models import Task, TaskStatus

logger = logging.getLogger("task_status")

MAX_RETRIES = 3


async def complete_task(task_id: int) -> None:
    """
    Async workflow for task completion.
    """

    async with AsyncSessionLocal() as session:
        try:
            task: Task | None = await session.get(Task, task_id)

            if not task:
                logger.warning(f"[TASK NOT FOUND] task_id={task_id}")
                return

            # Idempotent operation
            if task.status != TaskStatus.COMPLETED:
                task.status = TaskStatus.COMPLETED

                await session.commit()

                logger.info(
                    f"[TASK STATUS UPDATED] "
                    f"task_id={task_id} -> COMPLETED"
                )

            # Mock side effects
            logger.info(
                f"[TASK NOTIFICATION SENT] task_id={task_id}"
            )

            logger.info(
                f"[TASK ANALYTICS UPDATED] task_id={task_id}"
            )

        except Exception:
            await session.rollback()
            raise

        finally:
            await session.close()


@celery_app.task(
    bind=True,
    max_retries=MAX_RETRIES,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
)
def process_task_completion(self, task_id: int):
    """
    Celery worker entrypoint.
    """

    logger.info(f"[TASK WORKER START] task_id={task_id}")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(
            complete_task(task_id)
        )

        logger.info(
            f"[TASK WORKER DONE] task_id={task_id}"
        )

    finally:
        loop.close()