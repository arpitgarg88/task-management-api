from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import TaskStatus
from app.schemas.schemas import (
    BulkStatusUpdateRequest,
    BulkStatusUpdateResponse,
    BulkTaskCreateRequest,
    BulkTaskCreateResponse,
    SortOrder,
    TaskCreateRequest,
    TaskResponse,
    TaskSortBy,
    TaskUpdateRequest,
)
from app.services.service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create(
    payload: TaskCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    return await TaskService.create(db, payload)


@router.post(
    "/bulk",
    response_model=BulkTaskCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def bulk_create(
    payload: BulkTaskCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    return await TaskService.bulk_create(db, payload)


@router.put(
    "/bulk/status",
    response_model=BulkStatusUpdateResponse,
)
async def bulk_update_status(
    payload: BulkStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    return await TaskService.bulk_update_status(db, payload)


@router.get(
    "",
    response_model=list[TaskResponse],
)
async def list_tasks(
    status: TaskStatus | None = Query(default=None),
    assigned_to: int | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    sort_by: TaskSortBy = Query(default=TaskSortBy.CREATED_AT),
    order: SortOrder = Query(default=SortOrder.DESC),
    db: AsyncSession = Depends(get_db),
):
    return await TaskService.list(
        session=db,
        status=status,
        assigned_to=assigned_to,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        order=order,
    )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
)
async def get(
    task_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await TaskService.get(db, task_id)


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
)
async def update(
    task_id: int,
    payload: TaskUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    return await TaskService.update(db, task_id, payload)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete(
    task_id: int,
    db: AsyncSession = Depends(get_db),
):
    await TaskService.delete(db, task_id)
    return Response(status_code=204)


@router.post(
    "/{task_id}/assign",
    response_model=TaskResponse,
)
async def assign_task(
    task_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await TaskService.assign_task_to_user(
        db,
        task_id,
        user_id,
    )