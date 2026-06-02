from app.rag.document_loader import load_file

def test_load_file():
    doc = load_file("app/main.py")

    print(doc, 'test')

    assert doc.source == "app/main.py"
    assert len(doc.content) > 0