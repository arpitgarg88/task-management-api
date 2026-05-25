import logging
from fastapi import FastAPI
from app.api.routes import router
from app.core.redis import init_redis

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

"""
Application entrypoint for the Task Management API.

Initializes:
- FastAPI application
- API route registration
- Redis cache connection
- Structured logging

This module acts as the bootstrap layer for the entire backend service.
"""

app = FastAPI(title="Task Management API")
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """
    Application startup hook.

    Initializes Redis connection pool and prepares
    system-wide logging for task lifecycle monitoring.
    """
    await init_redis()
    logging.getLogger("task_status").info("[LOGGER INIT] Task status logger ready")


@app.get("/")
async def root():
    """
    Health-check endpoint.

    Returns:
        dict: API availability confirmation.
    """
    return {"message": "API running"}