import logging
import time

from celery import shared_task

logger = logging.getLogger("task_worker")

"""
Celery background workers for asynchronous task processing.

Contains long-running or non-blocking workflows triggered
after task lifecycle events.
"""

MAX_RETRIES = 3

@shared_task(
    bind=True,
    max_retries=MAX_RETRIES,
    retry_backoff=True,
    retry_jitter=True,
)
def process_task_completion(self, task_id: int):
    """
    Background workflow executed after a task is completed.

    Simulates:
    - notification dispatch
    - analytics processing
    - activity feed updates
    - search indexing

    Retries automatically on failure using Celery retry policies.

    Args:
        task_id (int): ID of completed task.
    """
    logger.info(f"[TASK WORKER START] task_id={task_id}")
    try:
        logger.info(f"[TASK NOTIFICATION PROCESSING] task_id={task_id}")
        time.sleep(1)

        logger.info(f"[TASK ANALYTICS PROCESSING] task_id={task_id}")
        time.sleep(1)

        logger.info(f"[TASK ACTIVITY FEED UPDATED] task_id={task_id}")
        time.sleep(1)

        logger.info(f"[TASK SEARCH INDEX UPDATED] task_id={task_id}")

        logger.info(f"[TASK WORKER DONE] task_id={task_id}")

    except Exception as exc:
        logger.exception(f"[TASK WORKER ERROR] task_id={task_id} err={exc}")
        raise self.retry(exc=exc)