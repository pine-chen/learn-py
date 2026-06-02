from pathlib import Path
from fastapi import APIRouter, HTTPException

from app.services.project_scanner import (get_vue_files, get_js_files, classify_files)

from app.schemas.project import (ProjectScanRequest)

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
)

@router.post("/scan")
def scan_project(request: ProjectScanRequest):

    if not Path(request.project_root).exists():
        raise HTTPException(
            status_code=404,
            detail="项目路径不存在"
        )
    """
    扫描项目
    """
    vue_files = get_vue_files(request.project_root)
    js_files = get_js_files(request.project_root)

    all_files = vue_files + js_files

    result = classify_files(all_files)
    return result
