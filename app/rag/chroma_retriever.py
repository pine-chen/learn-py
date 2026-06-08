from pathlib import Path
from uuid import uuid4

import chromadb

from app.rag.models import Document


class ChromaRetriever:
    """
    基于Chroma的向量检索器，用于存储和检索前端项目知识库文档
    支持持久化存储、文档增删、相似度搜索等功能
    """
    
    def __init__(self, persist_dir:str = "data/chroma", collection_name:str = "frontend_agent_kb") ->  None:
        """
        初始化Chroma检索器实例
        
        Args:
            persist_dir: Chroma数据库的持久化存储目录路径，默认为"data/chroma"
            collection_name: 集合名称，用于标识不同的知识库，默认为"frontend_agent_kb"
        """
        self.collection_name = collection_name

        # 确保持久化目录存在，如果不存在则递归创建
        Path(persist_dir).mkdir(parents=True, exist_ok=True)

        # 创建持久化客户端并初始化集合
        self.client = chromadb.PersistentClient(
            path=persist_dir
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
        )

    def add_documents(self, documents: list[Document]) -> None:
        """
        批量添加文档到向量数据库中
        
        Args:
            documents: 要添加的文档列表，每个文档包含内容、来源、文件类型和模块类型等信息
        """
        if not documents:
            return
        
        ids: list[str] = []
        content: list[str] = []
        metadata: list[dict[str, str]] = []

        # 构建批量插入所需的数据结构：ID、内容和元数据
        for document in documents:
            ids.append(str(uuid4()))
            content.append(document.content)
            metadata.append({
                "source": document.source,
                "file_type": document.file_type,
                "module_type": document.module_type,
            })

        # 批量插入文档到Chroma集合中
        self.collection.add(
            ids=ids,
            documents=content,
            metadatas=metadata,
        )

    def clear(self) -> None:
        """
        清空当前集合中的所有文档，但保留集合结构
        """
        existing = self.collection.get()
        ids = existing.get("ids", [])
        
        # 如果存在文档，则根据ID批量删除
        if ids:
            self.collection.delete(ids=ids)

    def reset(self) -> None:
        """
        完全重置集合：删除旧集合并创建新的空集合
        用于彻底清空知识库并重新初始化的场景
        """
        try:
            # 尝试删除现有集合，如果集合不存在则忽略异常
            self.client.delete_collection(
                name=self.collection_name,
            )
        except Exception:
            pass

        # 重新创建空集合
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
        )

    def count(self) -> int:
        """
        获取当前集合中的文档总数
        
        Returns:
            int: 集合中文档的数量
        """
        return self.collection.count()

    def search(self, query: str, limit: int = 10) -> list[Document]:
        """
        执行相似度搜索，查找与查询文本最相关的文档
        
        Args:
            query: 查询文本，用于在向量空间中检索相似文档
            limit: 返回结果的数量上限，默认为10
            
        Returns:
            list[Document]: 排序后的相关文档列表，已过滤掉不允许的模块类型
        """
        # 扩大检索范围以获取更多候选结果，后续进行过滤
        results = self.collection.query(
            query_texts=[query],
            n_results=limit * 3
        )

        # 提取第一组查询结果（单查询模式）
        documents = results.get("documents", [])[0]
        metadatas = results.get("metadatas", [])[0]
        distances = results.get("distances", [])[0]

        # 定义允许返回的模块类型白名单
        allowed_module_types = {
            "views",
            "apis",
            "stores",
            "routers",
            "components",
        }

        items: list[Document] = []

        # 遍历搜索结果，过滤并转换为Document对象
        for content, metadata, distance in zip(documents, metadatas, distances):
            module_type = metadata.get("module_type", "unknown")
            
            # 跳过不在白名单中的模块类型
            if module_type not in allowed_module_types:
                continue

            items.append(
                Document(
                    content=content,
                    source=metadata.get("source", ""),
                    file_type=metadata.get("file_type", ""),
                    module_type=metadata.get("module_type", "unknown"),
                    distance=float(distance),
                )
            )
        return  items


# 创建全局默认的检索器实例，供其他模块直接使用
retriever = ChromaRetriever()
