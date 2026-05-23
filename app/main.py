import logging
from fastapi import FastAPI
from app.api.routes import router
from app.core.redis import init_redis

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

app = FastAPI(title="Task Management API")
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    await init_redis()
    logging.getLogger("task_status").info("[LOGGER INIT] Task status logger ready")


@app.get("/")
async def root():
    return {"message": "API running"}