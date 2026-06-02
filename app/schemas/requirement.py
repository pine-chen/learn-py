from pydantic import BaseModel, Field

class RequirementSpec(BaseModel):
    title: str = Field(description="需求标题")
    background: str = Field(default="", description="需求背景")
    requirements: list[str] = Field(default_factory=[], description="需求点")
    acceptance: list[str] = Field(default_factory=[], description="验收要点")

class RequirementParseRequest(BaseModel):
    content: str