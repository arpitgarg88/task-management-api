from fastapi import FastAPI

from app.api.routes import router
from app.db.database import AsyncSessionLocal
from app.db.seed import seed_data

app = FastAPI(
    title="Task Management API",
    version="1.0.0"
)

app.include_router(router)


@app.on_event("startup")
async def startup():

    async with AsyncSessionLocal() as session:
        await seed_data(session)


@app.get("/")
def root():
    return {"message": "API running"}