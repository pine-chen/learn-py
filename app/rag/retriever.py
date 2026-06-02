from app.rag.models import Document

class SimpleRetriever:
    def __init__(self) ->  None:
        self.documents:list[Document] = []

    def add_documents(self, documents: list[Document]) -> None:
        self.documents.extend(documents)


    def clear(self) -> None:
        self.documents = []


    def count(self) -> int:
        return len(self.documents)

    def search(self, query: str, limit: int = 10) -> list[Document]:
        results:list[Document] = []
        for doc in self.documents:
            if query in doc.content:
                results.append(doc)
        return results

retriever = SimpleRetriever()