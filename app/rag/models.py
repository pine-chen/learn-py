from pydantic import BaseModel

class Document(BaseModel):
    content: str
    source: str
    file_type: str
    module_type: str = "unknown"
    distance: float | None = None