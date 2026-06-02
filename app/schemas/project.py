from pydantic import BaseModel

class ProjectScanRequest(BaseModel):
    project_root: str