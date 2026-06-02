from app.rag.models import Document


def chunk_document(doc: Document, chunk_size: int = 500) -> list[Document]:
    """将文档按指定大小分割成多个片段。

    Args:
        doc: 需要分割的原始文档对象，包含完整的内容和元数据信息。
        chunk_size: 每个片段的最大字符数，默认为500个字符。

    Returns:
        分割后的文档对象列表，每个文档对象包含原文件的部分内容和相同的元数据（source和file_type）。
    """
    content = doc.content
    chunks = []
    start = 0

    # 按chunk_size大小依次截取文档内容，创建新的Document对象
    while start < len(content):
        end = start + chunk_size
        chunk_content = content[start:end]
        chunks.append(Document(
            content = chunk_content,
            source = doc.source,
            file_type = doc.file_type
        ))
        start = end
    return  chunks