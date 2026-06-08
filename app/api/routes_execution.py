from fastapi import APIRouter, HTTPException

from app.schemas.execution import ExecutionTaskCreateResponse, ExecutionTask, ExecutionTaskUpdateRequest
from app.services.execution_service import create_execution_tasks, list_execution_tasks, update_execution_task_status
from app.services.workflow_service import get_workflow_run

router = APIRouter(
    tags=["execution"],
)

@router.post("/workflow/runs/{run_id}/execution-tasks", response_model=ExecutionTaskCreateResponse)
def create_execution_tasks_api(run_id: str):
    run = get_workflow_run(run_id)

    if run is None:
        raise HTTPException(status_code=404, detail="Workflow run not found")

    if  run.status != "approved":
        raise HTTPException(status_code=400, detail="Workflow run is not approved")

    tasks = create_execution_tasks(run_id)

    if tasks is None:
        raise HTTPException(status_code=404, detail="Failed to create execution tasks")

    return {
        "run_id": run.id,
        "total_tasks": len(tasks),
        "tasks": tasks
    }

@router.get("/workflow/runs/{run_id}/execution-tasks", response_model=list[ExecutionTask])
def get_execution_tasks_api(run_id: str):
    task = list_execution_tasks(run_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Workflow run not found")
    return task

@router.post("/execution/tasks/{task_id}/start", response_model=ExecutionTask)
def start_execution_task_api(task_id: str, request: ExecutionTaskUpdateRequest):
    task = update_execution_task_status(
        task_id = task_id,
        note = request.note,
        status = "running"
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Execution task not found")

    return  task

@router.post("/execution/tasks/{task_id}/complete", response_model=ExecutionTask)
def complete_execution_task_api(task_id: str, request: ExecutionTaskUpdateRequest):
    task = update_execution_task_status(
        task_id = task_id,
        note = request.note,
        status = "completed"
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Execution task not found")

    return  task

@router.post("/execution/tasks/{task_id}/fail", response_model=ExecutionTask)
def fail_execution_task_api(task_id: str, request: ExecutionTaskUpdateRequest):
    task = update_execution_task_status(
        task_id = task_id,
        note = request.note,
        status = "failed"
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Execution task not found")

    return  task