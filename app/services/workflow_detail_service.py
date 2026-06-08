from app.schemas.workflow_detail import WorkflowProgress, WorkflowRunDetail, WorkflowRunSummary
from app.services.execution_service import list_execution_tasks
from app.services.trace_service import list_trace_events_by_run
from app.services.workflow_service import get_workflow_run


def build_progress(tasks) -> WorkflowProgress:
    """根据执行任务列表构建工作流进度统计信息

    遍历所有执行任务，统计不同状态的任务数量，并计算整体完成率。
    完成率基于已完成和失败的任务数占总任务数的比例计算。

    Args:
        tasks: 执行任务列表，包含不同状态的任务对象

    Returns:
        WorkflowProgress: 工作流进度统计对象，包含以下信息：
            - total_tasks: 总任务数量
            - pending_tasks: 等待执行的任务数量
            - running_tasks: 正在执行的任务数量
            - completed_tasks: 已成功完成的任务数量
            - failed_tasks: 执行失败的任务数量
            - completion_rate: 完成率（0.0-1.0），计算公式为(completed_tasks + failed_tasks) / total_tasks

    Note:
        - 如果任务列表为空，完成率设为0以避免除零错误
        - 完成率的计算包含了已完成和失败的任务，因为这两种状态都代表任务已结束
        - 未识别的状态会被计入总数但不会分配到具体分类中

    Example:
        >>> progress = build_progress(tasks)
        >>> print(f"完成率: {progress.completion_rate * 100:.2f}%")
        >>> print(f"待处理: {progress.pending_tasks}, 运行中: {progress.running_tasks}")
    """
    total_tasks = len(tasks)

    pending_tasks = 0
    running_tasks = 0
    completed_tasks = 0
    failed_tasks = 0

    for task in tasks:
        if task.status == "pending":
            pending_tasks += 1
        elif task.status == "running":
            running_tasks += 1
        elif task.status == "completed":
            completed_tasks += 1
        elif task.status == "failed":
            failed_tasks += 1

    if total_tasks == 0:
        completion_rate = 0
    else:
        completion_rate = (completed_tasks + failed_tasks) / total_tasks

    return WorkflowProgress(
        total_tasks=total_tasks,
        pending_tasks=pending_tasks,
        running_tasks=running_tasks,
        completed_tasks=completed_tasks,
        failed_tasks=failed_tasks,
        completion_rate=completion_rate
    )

def get_workflow_run_detail(run_id: str) -> WorkflowRunDetail | None:
    """获取工作流运行实例的完整详情信息

    聚合工作流的基本信息、执行计划、关联任务、进度统计和追踪事件，
    构建一个完整的工作流详情视图。该函数整合了多个数据源，提供
    对工作流运行状态的全面展示。

    Args:
        run_id: 工作流运行实例的唯一标识符（UUID字符串格式）

    Returns:
        WorkflowRunDetail | None: 如果找到则返回完整的工作流详情对象，包含：
            - run: 工作流摘要信息（ID、查询、状态、审核意见、时间戳等）
            - plan: 完整的执行计划（目标文件、步骤、风险等）
            - tasks: 所有关联的执行任务列表
            - progress: 任务进度统计信息
            - traces: 按时间排序的所有追踪事件列表
            如果工作流不存在则返回None

    Note:
        - 如果工作流不存在，直接返回None
        - 如果工作流没有关联的执行任务，tasks字段为空列表
        - 追踪事件按创建时间升序排列
        - 进度统计基于实际存在的执行任务计算

    Example:
        >>> detail = get_workflow_run_detail("run_123abc")
        >>> if detail:
        ...     print(f"工作流状态: {detail.run.status}")
        ...     print(f"任务进度: {detail.progress.completion_rate * 100:.2f}%")
        ...     print(f"追踪事件数: {len(detail.traces)}")
    """
    run = get_workflow_run(run_id)

    if run is None:
        return None

    tasks = list_execution_tasks(run_id)

    if tasks is None:
        tasks = []

    traces = list_trace_events_by_run(run_id)

    return WorkflowRunDetail(
        run = WorkflowRunSummary(
            id = run.id,
            query = run.query,
            status = run.status,
            review_comment = run.review_comment,
            created_at = run.created_at,
            updated_at = run.updated_at
        ),
        plan=run.plan,
        tasks=tasks,
        progress=build_progress(tasks),
        traces=traces,
    )
