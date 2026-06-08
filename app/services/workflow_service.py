"""工作流服务模块

提供工作流运行实例的创建、查询、审批和拒绝等核心功能。
使用内存字典存储工作流运行数据。
"""
from datetime import datetime, timezone
from uuid import uuid4

from app.schemas.plan import PlanGenerateResponse
from app.schemas.workflow import WorkflowRun
from app.services.plan_generator import generate_plan

# 内存存储的工作流运行实例字典，键为工作流ID，值为WorkflowRun对象
RUNS:dict[str, WorkflowRun] =  {}

def get_now() -> datetime:
    """获取当前UTC时间

    Returns:
        datetime: 当前的UTC时间对象，包含时区信息
    """
    return datetime.now(timezone.utc)

def create_workflow_run(query: str, limit: int = 10) -> WorkflowRun:
    """创建工作流运行实例

    根据用户查询生成执行计划，并创建新的工作流运行实例。

    Args:
        query: 用户查询字符串，用于生成执行计划
        limit: 计划生成的限制数量，默认为10

    Returns:
        WorkflowRun: 新创建的工作流运行实例，包含生成的计划和初始状态

    Note:
        - 新创建的工作流状态为"plan_generated"
        - 工作流实例会自动存储到内存字典RUNS中
        - 使用UUID作为工作流的唯一标识符
    """
    plan_data = generate_plan(query, limit)

    plan = PlanGenerateResponse(**plan_data)

    now = get_now()

    run = WorkflowRun(
        id=str(uuid4()),
        query=query,
        status="plan_generated",
        plan=plan,
        review_comment=None,
        created_at=now,
        updated_at=now,
    )

    RUNS[run.id] = run

    return  run

def list_workflow_runs() -> list[WorkflowRun]:
    """获取所有工作流运行实例列表

    Returns:
        list[WorkflowRun]: 包含所有已创建工作流运行实例的列表
    """
    return list(RUNS.values())

def get_workflow_run(run_id: str) -> WorkflowRun | None:
    """根据ID获取指定的工作流运行实例

    Args:
        run_id: 工作流运行实例的唯一标识符

    Returns:
        WorkflowRun | None: 如果找到则返回对应的工作流运行实例，否则返回None
    """
    return RUNS.get(run_id)

def approve_workflow_run(run_id: str, comment: str | None = None) -> WorkflowRun |  None:
    """审批通过指定的工作流运行实例

    将工作流状态更新为"approved"，并可选添加审核备注。

    Args:
        run_id: 工作流运行实例的唯一标识符
        comment: 可选的审核备注信息，默认为None

    Returns:
        WorkflowRun | None: 如果审批成功则返回更新后的工作流实例，如果未找到则返回None

    Note:
        更新操作会修改状态为"approved"、设置审核备注并更新时间戳
    """
    run = RUNS.get(run_id)

    if run is None:
        return None

    updated_run = run.model_copy(update={
        "status": "approved",
        "review_comment": comment,
        "updated_at": get_now(),
    })

    RUNS[run_id] = updated_run

    return updated_run

def reject_workflow_run(run_id: str, comment: str | None = None) -> WorkflowRun |  None:
    """拒绝指定的工作流运行实例

    将工作流状态更新为"rejected"，并可选添加审核备注。

    Args:
        run_id: 工作流运行实例的唯一标识符
        comment: 可选的审核备注信息，默认为None

    Returns:
        WorkflowRun | None: 如果拒绝成功则返回更新后的工作流实例，如果未找到则返回None

    Note:
        更新操作会修改状态为"rejected"、设置审核备注并更新时间戳
    """
    run = RUNS.get(run_id)

    if run is None:
        return None

    updated_run = run.model_copy(update={
        "status": "rejected",
        "review_comment": comment,
        "updated_at": get_now(),
    })

    RUNS[run_id] = updated_run

    return updated_run
