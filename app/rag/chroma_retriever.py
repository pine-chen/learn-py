from pathlib import Path
from uuid import uuid4

import chromadb

from app.rag.models import Document

class ChromaRetriever:
    def __init__(self, persist_dir:str = "data/chroma", collection_name:str = "frontend_agent_kb") ->  None:
        self.collection_name = collection_name

        Path(persist_dir).mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=persist_dir
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
        )

    def add_documents(self, documents: list[Document]) -> None:
        if not documents:
            return
        ids: list[str] = []
        content: list[str] = []
        metadata: list[dict[str, str]] = []

        for document in documents:
            ids.append(str(uuid4()))
            content.append(document.content)
            metadata.append({
                "source": document.source,
                "file_type": document.file_type,
                "module_type": document.module_type,
            })

        self.collection.add(
            ids=ids,
            documents=content,
            metadatas=metadata,
        )


    def clear(self) -> None:
        existing = self.collection.get()
        ids = existing.get("ids", [])
        if ids:
            self.collection.delete(ids=ids)


    def reset(self) -> None:
        try:
            self.client.delete_collection(
                name=self.collection_name,
            )
        except Exception:
            pass

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
        )

    def count(self) -> int:
        return self.collection.count()

    def search(self, query: str, limit: int = 10) -> list[Document]:
        results = self.collection.query(
            query_texts=[query],
            n_results=limit * 3
        )

        documents = results.get("documents", [])[0]
        metadatas = results.get("metadatas", [])[0]
        distances = results.get("distances", [])[0]

        allowed_module_types = {
            "views",
            "apis",
            "stores",
            "routers",
            "components",
        }

        items: list[Document] = []

        for content, metadata, distance in zip(documents, metadatas, distances):
            module_type = metadata.get("module_type", "unknown")
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

retriever = ChromaRetriever()
