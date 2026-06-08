from fastapi import APIRouter, HTTPException

from app.schemas.workflow_detail import WorkflowRunDetail
from app.services.workflow_detail_service import get_workflow_run_detail

router = APIRouter(
    tags=["workflow"],
)

@router.get("/workflow/runs/{run_id}/detail", response_model=WorkflowRunDetail)
def get_workflow_run_detail_api(run_id: str):
    detail = get_workflow_run_detail(run_id)

    if detail is None:
        raise HTTPException(status_code=404, detail="Workflow run not found")
    return detail