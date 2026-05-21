from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.db.models import TaskStatus


class TaskCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    status: TaskStatus = TaskStatus.TODO


class TaskUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    status: Optional[TaskStatus] = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    assigned_to: Optional[int]

    created_at: datetime
    updated_at: datetime