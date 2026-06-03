from pydantic import BaseModel, Field


class RagIngestRequest(BaseModel):
    project_root: str = Field(description="项目根目录")

class RagIngestResponse(BaseModel):
    files: int
    documents: int
    chunks: int


class RagSearchRequest(BaseModel):
    query: str = Field(description="搜索关键词")
    limit: int = Field(default=10, ge=1, le=50)


class RagSearchItem(BaseModel):
    content: str
    source: str
    file_type: str
    module_type: str
    distance: float | None = None


class RagSearchResponse(BaseModel):
    query: str
    total: int
    results: list[RagSearchItem]