from typing import Any, Dict

from app.rag.retriever import retrieve_documents


def query_knowledge_base(
    query: str,
    top_k: int = 5,
) -> Dict[str, Any]:
    """
    Query the Sentinel knowledge base using semantic retrieval.

    Args:
        query: Natural-language question or investigation query.
        top_k: Maximum number of relevant documents to retrieve.

    Returns:
        Dictionary containing the query and retrieved knowledge.
    """

    if not query or not query.strip():
        return {
            "success": False,
            "error": "Query cannot be empty.",
            "results": [],
        }

    top_k = max(1, min(top_k, 10))

    try:
        results = retrieve_documents(
            query=query.strip(),
            top_k=top_k,
        )

        return {
            "success": True,
            "query": query.strip(),
            "results": results,
            "result_count": len(results),
        }

    except Exception as exc:
        return {
            "success": False,
            "query": query.strip(),
            "error": str(exc),
            "results": [],
        }