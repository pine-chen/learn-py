from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ExecutionTaskStatus = Literal[
    "pending",
    "running",
    "completed",
    "failed",
]

class ExecutionTask(BaseModel):
    id: str
    run_id: str
    step_no: int
    title: str
    description: str
    target_files: list[str]
    status: ExecutionTaskStatus
    note: str | None = None
    created_at: datetime
    updated_at: datetime


class ExecutionTaskCreateResponse(BaseModel):
    run_id: str
    total_tasks: int
    tasks: list["ExecutionTask"]

class ExecutionTaskUpdateRequest(BaseModel):
    note: str | None = Field(default=None, description="执行备注")
