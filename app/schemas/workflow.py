from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.plan import PlanGenerateResponse

WorkflowRunStatus = Literal[
    "plan_generated",
    "approved",
    "rejected",
]

class WorkflowRunCreateRequest(BaseModel):
    query: str = Field(description="需求或问题描述")
    limit: int = Field(default=10, ge=1, le=50)

class WorkflowReviewRequest(BaseModel):
    comment: str |  None = Field(default= None, description="审核意见")

class WorkflowRun(BaseModel):
    id: str
    query: str
    status: WorkflowRunStatus
    plan: PlanGenerateResponse
    review_comment: str | None = None
    created_at: datetime
    updated_at: datetime