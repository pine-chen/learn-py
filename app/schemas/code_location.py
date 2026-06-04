from pydantic import BaseModel, Field


class CodeLocateRequest(BaseModel):
    query: str = Field(description="需求或问题描述")
    limit: int = Field(default=10, ge=1, le=50)


class CodeEvidence(BaseModel):
    content: str
    distance: float | None = None


class CodeLocationItem(BaseModel):
    source: str
    file_type: str
    module_type: str
    hit_count: int
    best_distance: float | None = None
    reason: str
    evidences: list[CodeEvidence]


class CodeLocateResponse(BaseModel):
    query: str
    total_files: int
    files: list[CodeLocationItem]