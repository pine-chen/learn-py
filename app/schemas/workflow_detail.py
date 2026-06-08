from datetime import datetime

from pydantic import BaseModel

from app.schemas.execution import ExecutionTask
from app.schemas.plan import PlanGenerateResponse
from app.schemas.trace import TraceEvent
from app.schemas.workflow import WorkflowRunStatus


class WorkflowRunSummary(BaseModel):
    """工作流运行实例摘要信息

    包含工作流的基本状态和元数据，用于在列表视图或详情视图中
    展示工作流的核心信息，不包含详细的执行计划。
    """
    id: str
    query: str
    status: WorkflowRunStatus
    review_comment: str | None = None
    created_at: datetime
    updated_at: datetime

class WorkflowProgress(BaseModel):
    """工作流执行进度统计信息

    聚合统计工作流中所有执行任务的状态分布，计算整体完成率。
    用于前端展示工作流的执行进度和任务状态概览。
    """
    total_tasks: int
    pending_tasks: int
    running_tasks: int
    completed_tasks: int
    failed_tasks: int
    completion_rate: float

class WorkflowRunDetail(BaseModel):
    """工作流运行实例完整详情

    聚合工作流的所有相关信息，包括基本摘要、执行计划、任务列表、
    进度统计和追踪事件，提供对工作流运行状态的全面视图。
    用于详情页展示工作流的完整信息。
    """
    run: WorkflowRunSummary
    plan: PlanGenerateResponse
    tasks: list[ExecutionTask]
    traces: list[TraceEvent]
    progress: WorkflowProgress
