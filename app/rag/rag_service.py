from pathlib import Path

from app.rag.chunker import chunk_document
from app.rag.document_loader import load_file
from app.rag.chroma_retriever import retriever
from app.services.project_scanner import get_js_files, get_vue_files

def ingest_project(project_root: str) -> dict[str, int]:
    root = Path(project_root)

    if not root.exists():
        raise FileNotFoundError("项目路径不存在")
    if not root.is_dir():
        raise ValueError("项目路径不是目录")

    files = get_js_files(project_root) + get_vue_files(project_root)

    retriever.reset()
    total_documents = 0
    total_chunks = 0

    for file in files:
        document = load_file(file)
        chunks = chunk_document(document)
        retriever.add_documents(chunks)
        total_documents += 1
        total_chunks += len(chunks)

    return {
        "files": len(files),
        "documents": total_documents,
        "chunks": total_chunks
    }

def search_project_knowledge(query: str, limit: int = 10):
    return retriever.search(query = query, limit = limit)

def get_rag_status() -> dict[str, int]:
    return {
        "documents": retriever.count(),
    }
