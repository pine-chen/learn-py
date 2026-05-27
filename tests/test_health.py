from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_get_app_info() -> None:
    response = client.get("/api/info")
    assert response.status_code == 200
    assert response.json()["app_name"] == "Frontend Agent Workflow Platform"
    assert response.json()["env"] == "dev"
    assert response.json()["api_prefix"] == ""
