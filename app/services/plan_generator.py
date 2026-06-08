from app.schemas.plan import PlanTargetFile, PlanStep
from app.services.code_locator import locate_code


def build_summary(total_files: int) -> str:
    if total_files == 0:
        return "没有定位到明确相关文件，建议调整需求描述或重新执行 RAG ingest。"

    return "根据代码定位结果，初步生成可能的修改方案。"

def build_target_files(files) ->  list[PlanTargetFile]:
    target_files: list[PlanTargetFile] = []

    for file in files:
        target_files.append(
            PlanTargetFile(
                source=file.source,
                file_type=file.file_type,
                module_type=file.module_type,
                reason=file.reason,
                hit_count=file.hit_count,
                best_distance=file.best_distance,
            )
        )

    return target_files

def build_steps(target_files: list[PlanTargetFile]) -> list[PlanStep]:
    steps: list[PlanStep] = []

    view_files = [
        file.source
        for file in target_files
        if file.module_type == "views"
    ]

    api_files = [
        file.source
        for file in target_files
        if file.module_type == "api"
    ]

    store_files = [
        file.source
        for file in target_files
        if file.module_type == "store"
    ]
    router_files = [
        file.source
        for file in target_files
        if file.module_type == "router"
    ]
    component_files = [
        file.source
        for file in target_files
        if file.module_type == "components"
    ]

    step_no = 1

    if view_files:
        steps.append(
            PlanStep(
                step_no=step_no,
                title="修改视图文件",
                description="根据需求描述，修改视图文件。",
                target_files=view_files
            )
        )
        step_no += 1

    if api_files:
        steps.append(
            PlanStep(
                step_no=step_no,
                title="修改 API 文件",
                description="根据需求描述，修改 API 文件。",
                target_files=api_files
            )
        )
        step_no += 1

    if store_files:
        steps.append(
            PlanStep(
                step_no=step_no,
                title="修改状态管理文件",
                description="根据需求描述，修改状态管理文件。",
                target_files=store_files
            )
        )
        step_no += 1

    if router_files:
        steps.append(
            PlanStep(
                step_no=step_no,
                title="修改路由文件",
                description="根据需求描述，修改路由文件。",
                target_files=router_files
            )
        )
        step_no += 1

    if component_files:
        steps.append(
            PlanStep(
                step_no=step_no,
                title="修改组件文件",
                description="根据需求描述，修改组件文件。",
                target_files=component_files
            )
        )
        step_no += 1

    return  steps


def build_risks(total_files: int) -> list[str]:
    risks = [
        "当前方案基于 RAG 检索结果生成，仍需要人工确认目标文件是否准确。",
        "如果需求涉及权限、接口字段、路由或状态管理，需要进一步检查关联文件。",
    ]
    if total_files == 0:
        risks.append("没有定位到明确相关文件，建议调整需求描述或重新执行 RAG ingest。")

    return risks

def generate_plan(query: str, limit: int = 10) -> dict:
    files = locate_code(query=query, limit = limit)
    target_files = build_target_files(files)
    steps = build_steps(target_files)
    risks = build_risks(total_files=len(target_files))

    return {
        "query": query,
        "summary": build_summary(total_files=len(target_files)),
        "target_files": target_files,
        "steps": steps,
        "risks": risks,
    }