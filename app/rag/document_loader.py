from pathlib import Path
from app.rag.models import Document

def load_file(file_path: str) -> Document:
    path = Path(file_path)

    content = path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    return Document(
        content = content,
        source = str(path),
        file_type = path.suffix
    )

doc = load_file("app/main.py")
print(doc)