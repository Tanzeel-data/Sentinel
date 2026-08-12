from typing import Any, Dict, List

from app.rag.knowledge_base import SentinelKnowledgeBase


def retrieve_documents(
    query: str,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """
    Retrieve the most relevant documents from the
    Sentinel ChromaDB knowledge base.
    """

    if not query or not query.strip():
        return []

    top_k = max(1, min(top_k, 10))

    knowledge_base = SentinelKnowledgeBase()

    return knowledge_base.search(
        query=query.strip(),
        top_k=top_k,
    )