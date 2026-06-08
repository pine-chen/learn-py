from datetime import datetime
from typing import Literal, Any

from pydantic import BaseModel, Field

TraceEventType = Literal[
    "workflow_created",
    "plan_generated",
    "workflow_approved",
    "workflow_rejected",
    "execution_tasks_created",
    "task_started",
    "task_completed",
    "task_failed",
    "note",
]

class TraceEvent(BaseModel):
    id: str
    run_id: str
    task_id: str | None = None
    event_type: TraceEventType
    title: str
    message: str
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

class TraceCreateRequest(BaseModel):
    title: str
    message: str
    task_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)