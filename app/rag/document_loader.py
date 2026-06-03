from pathlib import Path
from app.rag.models import Document



def detect_module_type(file_path: str) -> str:
    normalized = file_path.replace("\\", "/")

    if "/src/views/" in normalized or normalized.startswith("src/views/"):
        return "views"

    if "/src/api/" in normalized or normalized.startswith("src/api/"):
        return "apis"

    if "/src/apis/" in normalized or normalized.startswith("src/apis/"):
        return "apis"

    if "/src/store/" in normalized or normalized.startswith("src/store/"):
        return "stores"

    if "/src/stores/" in normalized or normalized.startswith("src/stores/"):
        return "stores"

    if "/src/router/" in normalized or normalized.startswith("src/router/"):
        return "routers"

    if "/src/components/" in normalized or normalized.startswith("src/components/"):
        return "components"

    if "/src/utils/" in normalized or normalized.startswith("src/utils/"):
        return "utils"

    if "/src/layout/" in normalized or normalized.startswith("src/layout/"):
        return "layout"

    if "/tests/" in normalized:
        return "tests"

    return "unknown"

def load_file(file_path: str) -> Document:
    path = Path(file_path)

    content = path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    return Document(
        content = content,
        source = str(path),
        file_type = path.suffix,
        module_type=detect_module_type(str(path)),
    )