"""执行任务服务模块

提供执行任务的创建、查询等功能。
根据已审批的工作流运行实例生成具体的执行任务。
使用内存字典存储执行任务数据。
"""
from datetime import datetime, timezone
from uuid import uuid4

from app.schemas.execution import ExecutionTask
from app.services.workflow_service import get_workflow_run
from app.services.trace_service import add_trace_event

# 内存存储的执行任务字典，键为任务ID，值为ExecutionTask对象
TASKS: dict[str, ExecutionTask] = {}

def get_now() -> datetime:
    """获取当前UTC时间

    Returns:
        datetime: 当前的UTC时间对象，包含时区信息
    """
    return datetime.now(timezone.utc)

def create_execution_tasks(run_id: str) -> list[ExecutionTask] | None:
    """根据工作流运行实例创建执行任务列表
    
    为已审批通过的工作流运行实例中的每个计划步骤创建对应的执行任务。
    该函数会检查工作流的存在性和状态，确保只有已审批的工作流才能生成执行任务。
    如果该工作流的任务已存在则返回现有任务，避免重复创建。

    Args:
        run_id: 工作流运行实例的唯一标识符（UUID字符串格式）

    Returns:
        list[ExecutionTask] | None:
            - 如果工作流不存在，返回None
            - 如果工作流未审批通过（状态不是"approved"），返回空列表
            - 否则返回创建或已存在的执行任务列表，按步骤顺序排列

    Note:
        - 只有状态为"approved"的工作流才能创建执行任务
        - 新创建的任务状态为"pending"（待执行）
        - 任务会从工作流计划中提取步骤信息（步骤号、标题、描述、目标文件等）
        - 会自动创建一条execution_tasks_created类型的追踪事件，包含任务数量和ID列表
        - 使用幂等设计，多次调用不会重复创建任务

    Example:
        >>> tasks = create_execution_tasks("run_123abc")
        >>> if tasks:
        ...     print(f"创建了 {len(tasks)} 个任务")
        ...     for task in tasks:
        ...         print(f"  - 步骤{task.step_no}: {task.title}")
    """
    run = get_workflow_run(run_id)

    if run is None:
        return None

    # 检查工作流是否已审批通过
    if run.status != "approved":
        return []

    # 检查是否已存在该工作流的执行任务，避免重复创建
    existing_tasks = [
        task
        for task in TASKS.values()
        if task.run_id == run_id
    ]

    if existing_tasks:
        return existing_tasks

    now = get_now()

    tasks: list[ExecutionTask] = []

    # 为工作流计划中的每个步骤创建对应的执行任务
    for step in run.plan.steps:
        task = ExecutionTask(
            id=str(uuid4()),
            run_id=run_id,
            step_no=step.step_no,
            title=step.title,
            description=step.description,
            target_files=step.target_files,
            status="pending",
            note= None,
            created_at=now,
            updated_at=now,
        )

        TASKS[task.id] = task
        tasks.append(task)

    add_trace_event(
        run_id=run_id,
        event_type="execution_tasks_created",
        title="生成执行任务",
        message=f"已根据审核通过的方案生成 {len(tasks)} 个执行任务。",
        payload={
            "total_tasks": len(tasks),
            "task_ids": [task.id for task in tasks],
        },
    )

    return tasks


def list_execution_tasks(run_id: str) -> list[ExecutionTask] | None:
    """获取指定工作流运行实例的所有执行任务

    根据工作流运行实例的ID查询其关联的所有执行任务，包括不同状态的任务。

    Args:
        run_id: 工作流运行实例的唯一标识符（UUID字符串格式）

    Returns:
        list[ExecutionTask] | None:
            - 如果工作流不存在，返回None
            - 否则返回该工作流关联的所有执行任务列表，可能为空列表

    Note:
        返回的任务不进行排序，保持创建时的顺序
    """
    run = get_workflow_run(run_id)

    if run is None:
        return None
    return [
        task
        for task in TASKS.values()
        if task.run_id == run_id
    ]

def get_execution_task(task_id: str) -> ExecutionTask | None:
    """根据ID获取指定的执行任务

    通过执行任务的唯一标识符查找并返回对应的完整任务信息。

    Args:
        task_id: 执行任务的唯一标识符（UUID字符串格式）

    Returns:
        ExecutionTask | None: 如果找到则返回对应的执行任务对象，
                             包含完整的任务信息和状态；
                             如果未找到匹配的任务则返回None

    Note:
        使用字典的get方法，不存在时不会抛出异常而是返回None
    """
    return TASKS.get(task_id)

def update_execution_task_status(task_id: str, status: str, note: str | None = None) -> ExecutionTask | None:
    """更新执行任务的状态

    修改指定执行任务的状态信息，并可选添加备注说明。
    根据状态变化自动创建相应的追踪事件（task_started、task_completed或task_failed）。

    Args:
        task_id: 执行任务的唯一标识符（UUID字符串格式）
        status: 要更新的目标状态，必须是ExecutionTaskStatus中定义的合法值：
                - "running": 任务开始执行
                - "completed": 任务成功完成
                - "failed": 任务执行失败
                - "pending": 任务等待执行
        note: 可选的任务执行备注或说明信息，用于记录执行细节或失败原因，默认为None

    Returns:
        ExecutionTask | None:
            - 如果更新成功，返回更新后的执行任务实例（包含新的状态和时间戳）
            - 如果任务不存在，返回None

    Note:
        - 更新操作会同时刷新任务的updated_at时间戳
        - 当状态为"running"、"completed"或"failed"时，会自动创建对应的追踪事件
        - 追踪事件包含任务的详细信息（任务ID、步骤号、标题、目标文件、状态变更等）
        - 使用model_copy方法创建对象的深拷贝以保证数据一致性

    Example:
        >>> updated_task = update_execution_task_status(
        ...     task_id="task_456def",
        ...     status="running",
        ...     note="开始执行代码修改"
        ... )
        >>> if updated_task:
        ...     print(f"任务状态: {updated_task.status}")
        '任务状态: running'
    """
    task = TASKS.get(task_id)
    if task is None:
        return None

    # 创建更新后的任务副本并保存到存储中
    updated_task = task.model_copy(update={
        "status": status,
        "note": note,
        "updated_at": get_now(),
    })
    TASKS[task_id] = updated_task

    # 定义状态到追踪事件类型的映射关系
    event_type_map = {
        "running": "task_started",
        "completed": "task_completed",
        "failed": "task_failed",
    }

    # 定义状态到追踪事件标题的映射关系
    title_map = {
    "running": "开始执行任务",
    "completed": "完成执行任务",
    "failed": "执行任务失败",
    }

    if status in event_type_map:
        add_trace_event(
            run_id=task.run_id,
            task_id=task.id,
            event_type=event_type_map[status],
            title=title_map[status],
            message=note or f"任务状态更新为 {status}。",
            payload={
                "task_id": task.id,
                "step_no": task.step_no,
                "title": task.title,
                "target_files": task.target_files,
                "from_status": task.status,
                "to_status": status,
            },
    )
    return updated_task
