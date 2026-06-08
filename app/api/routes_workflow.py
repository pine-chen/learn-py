from fastapi import APIRouter, HTTPException
from pygments.styles.dracula import comment

from app.schemas.workflow import WorkflowRun, WorkflowRunCreateRequest, WorkflowReviewRequest
from app.services.workflow_service import create_workflow_run, get_workflow_run, list_workflow_runs, \
    approve_workflow_run, reject_workflow_run

router = APIRouter(
    prefix="/workflow",
    tags=["workflow"],
)

@router.post("/runs", response_model=WorkflowRun)
def create_run_api(request: WorkflowRunCreateRequest):
    return create_workflow_run(
        query=request.query,
        limit=request.limit
    )

@router.get("/runs", response_model=list[WorkflowRun])
def get_runs_api():
    return list_workflow_runs()

@router.get("/run/{run_id}", response_model=WorkflowRun)
def get_run_api(run_id: str):
    run =  get_workflow_run(run_id)

    if run is None:
        raise HTTPException(status_code=404, detail="Workflow run not found")

    return  run

@router.post("/run/{run_id}/approve", response_model=WorkflowRun)
def approve_run_api(run_id: str, request: WorkflowReviewRequest):
    run = approve_workflow_run(
        run_id = run_id,
        comment = request.comment
    )

    if run is None:
        raise HTTPException(status_code=404, detail="Workflow run not found")

    return  run

@router.post("/run/{run_id}/reject", response_model=WorkflowRun)
def reject_run_api(run_id: str, request: WorkflowReviewRequest):
    run =  reject_workflow_run(
        run_id = run_id,
        comment = request.comment
    )

    if run is None:
        raise HTTPException(status_code=404, detail="Workflow run not found")

    return  run