from fastapi import APIRouter, HTTPException
from app.rag.rag_service import ingest_project, search_project_knowledge, get_rag_status
from app.schemas.rag import (RagIngestRequest, RagIngestResponse, RagSearchResponse, RagSearchRequest)

router = APIRouter(
    prefix="/rag",
    tags=["rag"],
)

@router.post("/ingest", response_model=RagIngestResponse)
def ingest_rag(request: RagIngestRequest):
    try:
        return ingest_project(request.project_root)

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="项目路径不存在",
        )

    except NotADirectoryError:
        raise HTTPException(
            status_code=400,
            detail="项目路径不是目录",
        )

@router.post("/search", response_model=RagSearchResponse)
def search_rag(request: RagSearchRequest):
    result = search_project_knowledge(query=request.query, limit=request.limit)

    return {
        "query": request.query,
        "total": len(result),
        "results": result
    }

@router.get("/status")
def rag_status():
    return get_rag_status()