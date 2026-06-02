from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_rag_search_empty() -> None:
    response = client.post(
        "/rag/search",
        json={
            "query": "不存在的关键词",
            "limit": 10,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == "不存在的关键词"
    assert data["total"] == 0
    assert data["results"] == []