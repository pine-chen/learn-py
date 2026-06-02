from app.services.requirement_parser import parse_requirement


def test_parse_requirement():
    text = """
新增订单审批费用字段

背景：
审批页面需要展示费用信息

需求：
增加费用字段
支持编辑

验收：
审批页显示费用
提交后保存成功
"""

    result = parse_requirement(text)

    assert result.title == "新增订单审批费用字段"

    assert result.background == "审批页面需要展示费用信息"

    assert len(result.requirements) == 2

    assert len(result.acceptance) == 2