from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.db.models import TaskStatus


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class TaskSortBy(str, Enum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    TITLE = "title"


class TaskCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    assigned_to: Optional[int] = None


class TaskUpdateRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    assigned_to: Optional[int] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    assigned_to: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BulkTaskCreateRequest(BaseModel):
    tasks: List[TaskCreateRequest]


class BulkTaskCreateItemResponse(BaseModel):
    success: bool
    data: Optional[TaskResponse] = None
    error: Optional[str] = None


class BulkTaskCreateResponse(BaseModel):
    results: List[BulkTaskCreateItemResponse]


class BulkStatusUpdateItem(BaseModel):
    task_id: int
    status: TaskStatus


class BulkStatusUpdateRequest(BaseModel):
    tasks: List[BulkStatusUpdateItem]


class BulkStatusUpdateItemResponse(BaseModel):
    task_id: int
    success: bool
    data: Optional[TaskResponse] = None
    error: Optional[str] = None


class BulkStatusUpdateResponse(BaseModel):
    results: List[BulkStatusUpdateItemResponse]