from fastapi import APIRouter, HTTPException

from app.schemas.trace import TraceEvent, TraceCreateRequest
from app.services.execution_service import get_execution_task
from app.services.trace_service import list_trace_events_by_run, list_trace_events_by_task, add_trace_event
from app.services.workflow_service import get_workflow_run

router = APIRouter(
    tags=["trace"],
)

@router.get("/workflow/runs/{run_id}/traces", response_model=list[TraceEvent])
def list_run_traces_api(run_id: str):
    run = get_workflow_run(run_id)

    if run is None:
        raise HTTPException(status_code=404, detail="Workflow run not found")

    return list_trace_events_by_run(run_id)


@router.get("/execution/tasks/{task_id}/traces", response_model=list[TraceEvent])
def list_task_traces_api(task_id: str):
    task = get_execution_task(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Execution task not found")

    return list_trace_events_by_task(task_id)

@router.post("/workflow/runs/{run_id}/traces", response_model=TraceEvent)
def create_run_trace_api(run_id: str, request: TraceCreateRequest):
    run = get_workflow_run(run_id)

    if run is None:
        raise HTTPException(status_code=404, detail="Workflow run not found")

    if request.task_id is not None:
        task = get_execution_task(request.task_id)

        if task is None:
            raise HTTPException(status_code=404, detail="Execution task not found")

        if task.run_id != run_id:
            raise HTTPException(status_code=400, detail="Task does not belong to the workflow run")

    return add_trace_event(
        run_id=run_id,
        task_id=request.task_id,
        event_type="note",
        title=request.title,
        message=request.message,
        payload=request.payload
    )