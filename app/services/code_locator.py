from collections import defaultdict

from app.rag.models import Document
from app.rag.rag_service import search_project_knowledge
from app.schemas.code_location import CodeLocationItem, CodeEvidence

# 定义允许处理的模块类型集合，用于过滤前端项目中的关键代码层
ALLOWED_MODULE_TYPES = {
    "views",
    "apis",
    "stores",
    "routers",
    "components",
}

# 定义模块类型的优先级排序，数值越小优先级越高，unknown和utils优先级最低
MODULE_PRIORITY = {
    "views": 1,
    "apis": 2,
    "stores": 3,
    "routers": 4,
    "components": 5,
    "utils": 9,
    "unknown": 99,
}


def build_reason(source: str, module_type: str, hit_count: int) -> str:
    """
    根据模块类型和命中次数生成推荐理由说明

    Args:
        source: 文件来源路径
        module_type: 模块类型（如views、apis、stores等）
        hit_count: 命中的相关片段数量

    Returns:
        str: 描述该文件为何需要被关注的理由文本，根据不同模块类型提供差异化说明
    """
    if module_type == "views":
        return f"该文件属于页面层，命中 {hit_count} 个相关片段，可能涉及需求对应页面修改"
    if module_type == "apis":
        return f"该文件属于接口层，命中 {hit_count} 个相关片段，可能涉及请求参数或接口字段调整"

    if module_type == "stores":
        return f"该文件属于状态管理层，命中 {hit_count} 个相关片段，可能涉及状态字段或数据流调整"

    if module_type == "routers":
        return f"该文件属于路由层，命中 {hit_count} 个相关片段，可能涉及页面入口或权限路由"

    if module_type == "components":
        return f"该文件属于组件层，命中 {hit_count} 个相关片段，可能涉及复用组件修改"

    return f"该文件命中 {hit_count} 个相关片段，需要进一步人工确认"


def group_documents_by_source(documents: list[Document]) -> list[CodeLocationItem]:
    """
    将文档按来源文件分组，并为每个文件生成代码定位项
    该函数会过滤掉不允许的模块类型，计算最佳匹配距离，并提取证据片段

    Args:
        documents: 从RAG检索返回的文档列表，包含代码片段及其元数据

    Returns:
        list[CodeLocationItem]: 已排序的代码定位项列表，按模块优先级、匹配距离和命中次数排序
    """
    grouped: dict[str, list[Document]] = defaultdict(list)

    # 遍历所有文档，按source路径分组，同时过滤掉不在允许列表中的模块类型
    for document in documents:
        if document.module_type not in ALLOWED_MODULE_TYPES:
            continue

        grouped[document.source].append(document)

    items: list[CodeLocationItem] = []

    # 对每个分组的文档进行处理，提取关键信息并构建代码定位项
    for source, docs in grouped.items():
        first = docs[0]

        # 收集该分组中所有有效的距离值（非None值）
        distances = [
            doc.distance
            for doc in docs
            if doc.distance is not None
        ]

        # 取最小距离作为最佳匹配度指标
        best_distances = min(distances) if distances else None

        # 为每个分组提取前3个最相关的文档作为证据片段，限制证据数量以避免冗余
        evidences = [
            CodeEvidence(
                content=doc.content[:500],
                distance=doc.distance,
            )
            for doc in docs[:3]
        ]

        # 构建该文件的代码定位项，包含模块信息、命中统计和推荐理由
        items.append(
            CodeLocationItem(
                source=source,
                file_type=first.file_type,
                module_type=first.module_type,
                hit_count=len(docs),
                best_distance=best_distances,
                reason=build_reason(
                    source=source,
                    module_type=first.module_type,
                    hit_count=len(docs),
                ),
                evidences=evidences,
            )
        )

    # 按多维度规则排序：模块优先级 > 最佳匹配距离 > 命中次数（降序）
    return sorted(
        items,
        key=lambda item: (
            MODULE_PRIORITY.get(item.module_type, 99),
            item.best_distance if item.best_distance is not None else 999,
            -item.hit_count,
        ),
    )


def locate_code(
        query: str,
        limit: int = 10,
) -> list[CodeLocationItem]:
    """
    根据自然语言查询定位相关的代码文件
    通过RAG服务检索项目知识，并对结果进行聚类和优先级排序

    Args:
        query: 用户的自然语言查询，用于匹配相关代码
        limit: 返回的代码定位项数量上限，默认为10

    Returns:
        list[CodeLocationItem]: 排序后的代码定位项列表，每项包含文件路径、模块类型、
                               匹配证据和推荐理由等信息
    """
    # 扩大检索范围以获取足够的候选片段，提高召回率
    documents = search_project_knowledge(
        query=query,
        limit=limit * 5,
    )

    # 对检索结果按文件分组并排序
    located_files = group_documents_by_source(documents)

    return located_files[:limit]
