from app.services.execution_service import create_execution_tasks, list_execution_tasks, get_execution_task, \
    update_execution_task_status
from app.services.workflow_service import create_workflow_run, approve_workflow_run


def test_create_execution_tasks() -> None:
    run = create_workflow_run("订单页面增加费用字段", limit=10)

    approve_workflow_run(run.id, "方案确认，可以执行")

    tasks = create_execution_tasks(run.id)

    assert tasks is not None
    assert len(tasks) > 0

    first_task = tasks[0]
    assert first_task.status == "pending"
    assert first_task.run_id == run.id
    assert first_task.step_no >= 1
    assert first_task.title

def test_create_execution_tasks_is_idempotent() -> None:
    run = create_workflow_run("订单页面增加费用字段", limit=10)
    approve_workflow_run(run.id, "方案确认，可以执行")
    tasks = create_execution_tasks(run.id)
    tasks_again = create_execution_tasks(run.id)
    assert tasks == tasks_again
    assert tasks[0].id == tasks_again[0].id

def test_list_execution_tasks() -> None:
    run = create_workflow_run("订单页面增加费用字段", limit=10)
    approve_workflow_run(run.id, "方案确认，可以执行")
    tasks = create_execution_tasks(run.id)
    tasks_list = list_execution_tasks(run.id)

    assert tasks is not None
    assert tasks_list is not None
    assert len(tasks) == len(tasks_list)

def test_get_execution_task() -> None:
    run = create_workflow_run("订单页面增加费用字段", limit=10)
    approve_workflow_run(run.id, "方案确认，可以执行")
    tasks = create_execution_tasks(run.id)

    assert tasks is not None
    first_task = tasks[0]
    found = get_execution_task(first_task.id)

    assert found is not None
    assert found.id == first_task.id
    assert found.run_id == run.id

def test_update_execution_task_status() -> None:
    run = create_workflow_run("订单页面增加费用字段", limit=10)
    approve_workflow_run(run.id, "方案确认，可以执行")
    tasks = create_execution_tasks(run.id)

    assert tasks is not None

    first_task = tasks[0]
    updated = update_execution_task_status(
        task_id=first_task.id,
        status="running",
        note="开始执行任务"
    )

    assert updated is not None
    assert updated.id == first_task.id
    assert updated.status == "running"
    assert updated.note == "开始执行任务"

def test_update_missing_execution_task_returns_none() -> None:
    updated = update_execution_task_status(
        task_id="not-exist",
        status="running",
        note="不存在",
    )
    assert updated is None