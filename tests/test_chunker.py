from app.rag.chunker import chunk_document
from app.rag.document_loader import load_file


def test_chunk_document():
    doc = load_file("app/main.py")

    chunks = chunk_document(doc, chunk_size=100)

    print(chunks)

    assert len(chunks) > 0
    assert chunks[0].source == "app/main.py"
    assert chunks[0].file_type == ".py"
    assert len(chunks[0].content) < 1000
    assert len(chunks[0].content) > 0