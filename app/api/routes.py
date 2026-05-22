from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import Response

from app.db.database import get_db
from app.schemas.schemas import (
    TaskCreateRequest,
    TaskUpdateRequest,
    TaskResponse,
)
from app.services.service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create(payload: TaskCreateRequest, db: AsyncSession = Depends(get_db)):
    return await TaskService.create(db, payload)


@router.get(
    "",
    response_model=list[TaskResponse],
)
async def list_tasks(user_id: int, db: AsyncSession = Depends(get_db)):
    return await TaskService.list(db, user_id)


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
)
async def get(task_id: int, db: AsyncSession = Depends(get_db)):
    return await TaskService.get(db, task_id)


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
)
async def update(task_id: int, payload: TaskUpdateRequest, db: AsyncSession = Depends(get_db)):
    return await TaskService.update(db, task_id, payload)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete(task_id: int, db: AsyncSession = Depends(get_db)):
    await TaskService.delete(db, task_id)
    return Response(status_code=204)