from fastapi import APIRouter

from app.schemas.code_location import CodeLocateResponse, CodeLocateRequest
from app.services.code_locator import locate_code

router = APIRouter(
    prefix="/code",
    tags=["code"],
)

@router.post("/locate", response_model=CodeLocateResponse)

def locate_code_api(request: CodeLocateRequest):
    files = locate_code(
        query=request.query,
        limit=request.limit,
    )

    return {
        "query": request.query,
        "total_files": len(files),
        "files": files,
    }