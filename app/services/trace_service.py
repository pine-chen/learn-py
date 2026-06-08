from datetime import datetime, timezone
from uuid import uuid4

from app.schemas.trace import TraceEvent, TraceEventType

TRACE_EVENTS: dict[str, TraceEvent] = {}

def get_now() -> datetime:
    """获取当前UTC时间

    Returns:
        datetime: 当前的UTC时间对象，包含时区信息
    """
    return datetime.now(timezone.utc)

def add_trace_event(
        run_id: str,
        event_type: TraceEventType,
        title: str,
        message: str,
        task_id: str | None = None,
        payload: dict | None = None
) -> TraceEvent:
    """添加追踪事件到内存存储

    创建一个新的追踪事件并存储到全局事件字典中，用于记录工作流或任务的执行轨迹。

    Args:
        run_id: 运行ID，用于标识一次完整的工作流执行
        event_type: 事件类型，必须是TraceEventType中定义的合法值
                   如workflow_created、task_started、task_completed等
        title: 事件的标题，简要描述事件内容
        message: 事件的详细描述信息
        task_id: 任务ID（可选），如果事件与特定任务相关则提供
        payload: 附加数据（可选），以字典形式存储额外的上下文信息，默认为空字典

    Returns:
        TraceEvent: 创建的追踪事件对象，包含自动生成的唯一ID和创建时间戳

    Example:
        >>> event = add_trace_event(
        ...     run_id="run_123",
        ...     event_type="task_started",
        ...     title="任务开始",
        ...     message="数据处理任务已启动",
        ...     task_id="task_456"
        ... )
    """
    event = TraceEvent(
        id = str(uuid4()),
        run_id = run_id,
        task_id = task_id,
        event_type=event_type,
        title=title,
        message=message,
        payload=payload or  {},
        created_at=get_now()
    )

    TRACE_EVENTS[event.id] = event
    return event


def list_trace_events_by_run(run_id: str) -> list[TraceEvent]:
    """根据运行ID查询所有相关的追踪事件

    从内存存储中筛选出指定运行ID的所有事件，并按创建时间升序排列。

    Args:
        run_id: 运行ID，用于过滤属于同一次工作流执行的事件

    Returns:
        list[TraceEvent]: 按时间顺序排列的追踪事件列表，最早的事件在前

    Note:
        如果没有找到匹配的事件，返回空列表
    """
    events = [
        event
        for event in TRACE_EVENTS.values()
        if event.run_id == run_id
    ]
    return sorted(events, key=lambda event: event.created_at)

def list_trace_events_by_task(task_id: str) -> list[TraceEvent]:
    """根据任务ID查询所有相关的追踪事件

    从内存存储中筛选出指定任务ID的所有事件，并按创建时间升序排列。

    Args:
        task_id: 任务ID，用于过滤属于同一任务的事件

    Returns:
        list[TraceEvent]: 按时间顺序排列的追踪事件列表，最早的事件在前

    Note:
        如果没有找到匹配的事件，返回空列表
    """
    events = [
        event
        for event in TRACE_EVENTS.values()
        if event.task_id == task_id
    ]
    return sorted(events, key=lambda event: event.created_at)
