from pydantic import BaseModel, Field


class PlanGenerateRequest(BaseModel):
    query: str = Field(description="需求或问题描述")
    limit: int = Field(default=10, ge=1, le=50)

class PlanTargetFile(BaseModel):
    source: str
    file_type: str
    module_type: str
    reason: str
    hit_count: int
    best_distance: float | None = None

class PlanStep(BaseModel):
    step_no: int
    title: str
    description: str
    target_files: list[str]

class PlanGenerateResponse(BaseModel):
    query: str
    summary: str
    target_files: list[PlanTargetFile]
    steps: list[PlanStep]
    risks: list[str]