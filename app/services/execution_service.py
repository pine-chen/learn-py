"""执行任务服务模块

提供执行任务的创建、查询等功能。
根据已审批的工作流运行实例生成具体的执行任务。
使用内存字典存储执行任务数据。
"""
from datetime import datetime, timezone
from uuid import uuid4

from app.schemas.execution import ExecutionTask
from app.services.workflow_service import get_workflow_run

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
    
    为已审批的工作流运行实例中的每个计划步骤创建对应的执行任务。
    如果任务已存在则返回现有任务，避免重复创建。
    
    Args:
        run_id: 工作流运行实例的唯一标识符
        
    Returns:
        list[ExecutionTask] | None: 
            - 如果工作流不存在，返回None
            - 如果工作流未审批通过，返回空列表
            - 否则返回创建或已存在的执行任务列表
            
    Note:
        - 只有状态为"approved"的工作流才能创建执行任务
        - 新创建的任务状态为"pending"
        - 任务会从工作流计划中提取步骤信息（步骤号、标题、描述、目标文件等）
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

    return tasks


def list_execution_tasks(run_id: str) -> list[ExecutionTask] | None:
    """获取指定工作流运行实例的所有执行任务
    
    Args:
        run_id: 工作流运行实例的唯一标识符
        
    Returns:
        list[ExecutionTask] | None: 
            - 如果工作流不存在，返回None
            - 否则返回该工作流关联的所有执行任务列表
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
    
    Args:
        task_id: 执行任务的唯一标识符
        
    Returns:
        ExecutionTask | None: 如果找到则返回对应的执行任务，否则返回None
    """
    return TASKS.get(task_id)

def update_execution_task_status(task_id: str, status: str, note: str | None = None) -> ExecutionTask | None:
    """更新执行任务的状态

    修改指定执行任务的状态信息，并可选添加备注说明。

    Args:
        task_id: 执行任务的唯一标识符
        status: 要更新的目标状态（如 "running"、"completed"、"failed" 等）
        note: 可选的任务执行备注或说明信息，默认为None

    Returns:
        ExecutionTask | None:
            - 如果更新成功，返回更新后的执行任务实例
            - 如果任务不存在，返回None

    Note:
        更新操作会同时刷新任务的更新时间戳
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
    return updated_task
