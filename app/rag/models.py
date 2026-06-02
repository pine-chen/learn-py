from pydantic import BaseModel

class Document(BaseModel):
    content: str
    source: str
    file_type: str