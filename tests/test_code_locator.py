from app.rag.models import Document
from app.main import app
from app.schemas.code_location import CodeLocationItem
from app.services.code_locator import group_documents_by_source
from fastapi.testclient import TestClient


client = TestClient(app)


def test_group_documents_by_source_includes_file_type_and_sorts() -> None:
    documents = [
        Document(
            content="store match",
            source="/project/src/store/user.js",
            file_type=".js",
            module_type="stores",
            distance=0.1,
        ),
        Document(
            content="api match",
            source="/project/src/api/order.js",
            file_type=".js",
            module_type="apis",
            distance=0.2,
        ),
        Document(
            content="second api match",
            source="/project/src/api/order.js",
            file_type=".js",
            module_type="apis",
            distance=0.05,
        ),
        Document(
            content="ignored utility",
            source="/project/src/utils/format.js",
            file_type=".js",
            module_type="utils",
            distance=0.01,
        ),
    ]

    items = group_documents_by_source(documents)

    assert [item.module_type for item in items] == ["apis", "stores"]
    assert items[0].source == "/project/src/api/order.js"
    assert items[0].file_type == ".js"
    assert items[0].hit_count == 2
    assert items[0].best_distance == 0.05
    assert len(items[0].evidences) == 2


def test_code_locate_api_returns_location_items(monkeypatch) -> None:
    def fake_locate_code(query: str, limit: int = 10) -> list[CodeLocationItem]:
        assert query == "订单费用字段"
        assert limit == 5
        return [
            CodeLocationItem(
                source="/project/src/api/order.js",
                file_type=".js",
                module_type="apis",
                hit_count=1,
                best_distance=0.12,
                reason="该文件属于接口层，命中 1 个相关片段，可能涉及请求参数或接口字段调整",
                evidences=[],
            )
        ]

    monkeypatch.setattr("app.api.routes_code.locate_code", fake_locate_code)

    response = client.post(
        "/code/locate",
        json={
            "query": "订单费用字段",
            "limit": 5,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "query": "订单费用字段",
        "total_files": 1,
        "files": [
            {
                "source": "/project/src/api/order.js",
                "file_type": ".js",
                "module_type": "apis",
                "hit_count": 1,
                "best_distance": 0.12,
                "reason": "该文件属于接口层，命中 1 个相关片段，可能涉及请求参数或接口字段调整",
                "evidences": [],
            }
        ],
    }
