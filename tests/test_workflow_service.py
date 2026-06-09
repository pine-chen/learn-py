from app.services.workflow_service import create_workflow_run, list_workflow_runs, get_workflow_run, \
    approve_workflow_run, reject_workflow_run


def test_workflow_service() -> None:
    run = create_workflow_run("订单页面增加费用字段", 10)

    assert run.id
    assert run.query == "订单页面增加费用字段"
    assert run.status == "plan_generated"
    assert run.plan is not None
    assert run.review_comment is None
    assert run.created_at is not None
    assert run.updated_at is not None

def test_list_workflow_runs():
    runs = list_workflow_runs()
    assert len(runs) > 0

def test_get_workflow_run() -> None:
    run = create_workflow_run("订单页面增加费用字段", 10)

    retrieved_run = get_workflow_run(run.id)
    assert retrieved_run is not None
    assert retrieved_run.id == run.id
    assert retrieved_run.query == "订单页面增加费用字段"

def test_approve_workflow_run() -> None:
    run = create_workflow_run("订单页面增加费用字段", 10)
    run_id = run.id

    assert run_id is not None

    approved_run = approve_workflow_run(run_id=run_id, comment="方案确认，可以执行")
    assert approved_run is not None
    assert approved_run.id == run_id
    assert approved_run.status == "approved"
    assert approved_run.review_comment == "方案确认，可以执行"

def test_reject_workflow_run() -> None:
    run = create_workflow_run("订单页面增加费用字段", 10)
    run_id = run.id
    rejected_run = reject_workflow_run(run_id=run_id, comment="方案风险较高，需要重做")
    assert rejected_run is not None
    assert rejected_run.id == run_id
    assert rejected_run.status == "rejected"
    assert rejected_run.review_comment == "方案风险较高，需要重做"

def test_approve_missing_workflow_run_returns_none() -> None:
    approved_run = approve_workflow_run(
        run_id="not-exist",
        comment="不存在",
    )
    assert approved_run is None