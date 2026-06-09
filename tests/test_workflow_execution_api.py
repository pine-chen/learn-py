from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_create_workflow_run_api() -> None:
    response = client.post("/workflow/runs", json={
        "query": "订单页面增加费用字段",
        "limit": 10
    })

    assert response.status_code == 200
    data = response.json()

    assert data["id"]
    assert data["query"] == "订单页面增加费用字段"
    assert data["status"] == "plan_generated"
    assert data["plan"] is not None

def test_get_workflow_run_api() -> None:
    create_response = client.post("/workflow/runs", json={
        "query": "订单页面增加费用字段",
        "limit": 10
    })
    run_id = create_response.json()["id"]

    response = client.get(f"/workflow/run/{run_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == run_id
    assert data["query"] == "订单页面增加费用字段"
    assert data["status"] == "plan_generated"
    assert data["plan"] is not None

def test_approve_workflow_run_api() -> None:
    create_response = client.post("/workflow/runs", json={
        "query": "订单页面增加费用字段",
        "limit": 10
    })
    run_id = create_response.json()["id"]
    approve_response = client.post(f"/workflow/run/{run_id}/approve", json={
        "comment": "方案确认，可以执行"
    })

    assert approve_response.status_code == 200
    data = approve_response.json()

    assert data["id"] == run_id
    assert data["status"] == "approved"
    assert data["review_comment"] == "方案确认，可以执行"

def test_reject_workflow_run_api() -> None:
    create_response = client.post("/workflow/runs", json={
        "query": "订单详情增加复杂交互",
        "limit": 10
    })
    run_id = create_response.json()["id"]
    reject_response = client.post(f"/workflow/run/{run_id}/reject", json={
        "comment": "方案风险较高，需要重做"
    })

    assert reject_response.status_code == 200
    data = reject_response.json()
    assert data["id"] == run_id
    assert data["status"] == "rejected"
    assert data["review_comment"] == "方案风险较高，需要重做"

def test_create_execution_tasks_requires_approved_run_api() -> None:
    create_response = client.post("/workflow/runs", json={
        "query": "订单页面增加费用字段",
        "limit": 10
    })
    run_id = create_response.json()["id"]
    task_response = client.post(f"/workflow/runs/{run_id}/execution-tasks")

    assert task_response.status_code == 400

def test_create_execution_tasks_after_approve_api() -> None:
    create_response = client.post("/workflow/runs", json={
        "query": "订单页面增加费用字段",
        "limit": 10
    })
    run_id = create_response.json()["id"]
    client.post(f"/workflow/run/{run_id}/approve", json={
        "comment": "方案确认，可以执行"
    })

    task_response = client.post(f"/workflow/runs/{run_id}/execution-tasks")

    assert task_response.status_code == 200
    data = task_response.json()
    assert data["run_id"] == run_id
    assert data["total_tasks"] > 0
    assert len(data["tasks"]) == data["total_tasks"]
    assert data["tasks"][0]["status"] == "pending"

def test_list_execution_tasks_api() -> None:
    create_response = client.post("/workflow/runs", json={
        "query": "订单页面增加费用字段",
        "limit": 10
    })
    run_id = create_response.json()["id"]
    client.post(f"/workflow/run/{run_id}/approve", json={
        "comment": "方案确认，可以执行"
    })
    client.post(f"/workflow/runs/{run_id}/execution-tasks")
    task_list_response = client.get(f"/workflow/runs/{run_id}/execution-tasks")
    assert task_list_response.status_code == 200
    data = task_list_response.json()

    # 确认接口返回的是列表
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["run_id"] == run_id

