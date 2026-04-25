import sys

from app.rag.rag_pipeline import vectordb


def query_text(question: str = "refund policy", k: int = 3) -> list[str]:
    results = vectordb.similarity_search(question, k=k)
    return [result.page_content for result in results]


if __name__ == "__main__":
    for page_content in query_text():
        sys.stdout.write(f"{page_content}\n")
