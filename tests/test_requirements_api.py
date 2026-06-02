from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_parse_requirement_api():
    responses = client.post(
        "/requirements/parse",
        json={
            "content": """
            新增订单审批费用字段
            
            背景：
            审批页面需要展示费用信息
            
            需求：
            增加费用字段
            
            验收：
            显示费用
            """

        })

    assert responses.status_code == 200
    assert responses.json()["title"] == "新增订单审批费用字段"