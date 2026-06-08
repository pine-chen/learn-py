"""工作流服务模块

提供工作流运行实例的创建、查询、审批和拒绝等核心功能。
使用内存字典存储工作流运行数据。
"""
from datetime import datetime, timezone
from uuid import uuid4

from app.schemas.plan import PlanGenerateResponse
from app.schemas.workflow import WorkflowRun
from app.services.plan_generator import generate_plan
from app.services.trace_service import add_trace_event

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

    根据用户查询生成执行计划，并创建新的工作流运行实例。该函数会调用计划生成器
    基于用户需求创建详细的修改方案，然后将工作流初始化为待审批状态。

    Args:
        query: 用户查询字符串，用于描述需求或问题，计划生成器将基于此生成执行方案
        limit: 计划生成的限制数量，控制生成步骤的上限，范围通常在1-50之间，默认为10

    Returns:
        WorkflowRun: 新创建的工作流运行实例对象，包含以下关键信息：
            - id: 自动生成的UUID作为唯一标识
            - query: 原始用户查询
            - status: 初始状态为"plan_generated"（待审批）
            - plan: 生成的完整执行计划，包括目标文件和执行步骤
            - created_at/updated_at: 创建和更新时间戳

    Note:
        - 新创建的工作流状态为"plan_generated"，需要等待人工审批后才能执行
        - 工作流实例会自动存储到全局内存字典RUNS中，以ID为键
        - 使用UUID4算法生成全局唯一的标识符
        - 会自动创建两条追踪事件：workflow_created和plan_generated
        - plan_generated事件包含目标文件数量和步骤数量的统计信息

    Example:
        >>> run = create_workflow_run(
        ...     query="修复登录页面的样式问题",
        ...     limit=5
        ... )
        >>> print(run.status)
        'plan_generated'
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

    add_trace_event(
        run_id=run.id,
        event_type="workflow_created",
        title="工作流创建",
        message="工作流已创建，请等待审批",
        payload={
            "query": query,
            "limit": limit,
        }
    )

    add_trace_event(
        run_id=run.id,
        event_type="plan_generated",
        title="生成修改方案",
        message="已根据代码定位结果生成初步修改方案。",
        payload={
            "total_files": len(plan.target_files),
            "total_steps": len(plan.steps),
        },
    )

    return  run

def list_workflow_runs() -> list[WorkflowRun]:
    """获取所有工作流运行实例列表

    从内存存储中检索所有已创建的工作流运行实例，不进行任何过滤或排序。

    Returns:
        list[WorkflowRun]: 包含所有已创建工作流运行实例的列表，返回顺序不保证

    Note:
        返回的是RUNS字典中所有值的副本（通过.values()转换为列表）
    """
    return list(RUNS.values())

def get_workflow_run(run_id: str) -> WorkflowRun | None:
    """根据ID获取指定的工作流运行实例

    通过工作流运行实例的唯一标识符查找并返回对应的完整信息。

    Args:
        run_id: 工作流运行实例的唯一标识符（UUID字符串格式）

    Returns:
        WorkflowRun | None: 如果找到则返回对应的工作流运行实例对象，
                           包含完整的状态、计划和审核信息；
                           如果未找到匹配的实例则返回None

    Note:
        使用字典的get方法，不存在时不会抛出异常而是返回None
    """
    return RUNS.get(run_id)

def approve_workflow_run(run_id: str, comment: str | None = None) -> WorkflowRun |  None:
    """审批通过指定的工作流运行实例

    将工作流状态从"plan_generated"更新为"approved"，表示方案已通过人工审核，
    可以进入执行阶段。同时记录审核备注和更新时间戳，并生成审批通过的追踪事件。

    Args:
        run_id: 工作流运行实例的唯一标识符（UUID字符串格式）
        comment: 可选的审核备注信息，用于说明审批意见或建议，默认为None

    Returns:
        WorkflowRun | None: 如果审批成功则返回更新后的工作流实例对象（状态已更新），
                           如果未找到对应ID的实例则返回None

    Note:
        - 更新操作会修改状态为"approved"、设置审核备注并更新updated_at时间戳
        - 使用model_copy方法创建对象的深拷贝以保证数据一致性
        - 会自动创建一条workflow_approved类型的追踪事件
        - 如果comment为None，追踪事件的message会使用默认文本

    Example:
        >>> updated_run = approve_workflow_run(
        ...     run_id="run_123abc",
        ...     comment="方案合理，可以执行"
        ... )
        >>> if updated_run:
        ...     print(updated_run.status)
        'approved'
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

    add_trace_event(
        run_id=run_id,
        event_type="workflow_approved",
        title="人工审核通过",
        message=comment or "方案已通过人工审核。",
    )

    return updated_run

def reject_workflow_run(run_id: str, comment: str | None = None) -> WorkflowRun |  None:
    """拒绝指定的工作流运行实例

    将工作流状态从"plan_generated"更新为"rejected"，表示方案未通过人工审核，
    需要重新制定或放弃执行。同时记录审核备注和更新时间戳，并生成拒绝的追踪事件。

    Args:
        run_id: 工作流运行实例的唯一标识符（UUID字符串格式）
        comment: 可选的审核备注信息，用于说明拒绝原因或改进建议，默认为None

    Returns:
        WorkflowRun | None: 如果拒绝成功则返回更新后的工作流实例对象（状态已更新），
                           如果未找到对应ID的实例则返回None

    Note:
        - 更新操作会修改状态为"rejected"、设置审核备注并更新updated_at时间戳
        - 使用model_copy方法创建对象的深拷贝以保证数据一致性
        - 会自动创建一条workflow_rejected类型的追踪事件
        - 如果comment为None，追踪事件的message会使用默认文本

    Example:
        >>> updated_run = reject_workflow_run(
        ...     run_id="run_123abc",
        ...     comment="方案过于复杂，需要简化"
        ... )
        >>> if updated_run:
        ...     print(updated_run.status)
        'rejected'
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

    add_trace_event(
        run_id=run_id,
        event_type="workflow_rejected",
        title="人工审核拒绝",
        message=comment or "方案未通过人工审核。",
    )

    return updated_run
