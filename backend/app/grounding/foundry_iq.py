from pathlib import Path
from typing import Any

from app.grounding.azure_search_client import (
    AzureSearchError,
    is_azure_search_available,
    search_azure_knowledge,
)
from app.grounding.local_knowledge import answer_with_citations
from app.grounding.status import get_grounding_status


def is_foundry_configured() -> bool:
    return get_grounding_status()["mode"] == "live-foundry-iq"


def grounded_answer(query: str, top_k: int = 5) -> dict[str, Any]:
    if is_azure_search_available():
        try:
            results = search_azure_knowledge(query, top=top_k)
            chunks = [_azure_result_to_chunk(item) for item in results]
            return {
                "answer": _answer_from_chunks(query, chunks),
                "citations": [_citation_from_chunk(chunk) for chunk in chunks],
                "mode": "live-azure-search",
                "grounding_mode": "live-azure-search",
            }
        except AzureSearchError:
            pass

    local_answer = answer_with_citations(query, top_k=top_k)
    return {
        **local_answer,
        "mode": "local-fallback",
        "grounding_mode": "local-fallback",
    }


def _azure_result_to_chunk(result: dict[str, Any]) -> dict[str, str]:
    source = str(result.get("source", "azure-search"))
    identifier = str(result.get("id", "")).strip() or "azure-search-result"
    return {
        "doc_id": identifier,
        "title": str(result.get("title", "Azure Search result")),
        "file_name": Path(source).name or source,
        "chunk_id": identifier,
        "text": str(result.get("content", "")),
    }


def _citation_from_chunk(chunk: dict[str, str]) -> dict[str, str]:
    return {
        "doc_id": chunk["doc_id"],
        "title": chunk["title"],
        "file_name": chunk["file_name"],
        "chunk_id": chunk["chunk_id"],
        "quote": _short_quote(chunk["text"]),
    }


def _short_quote(text: str, max_length: int = 220) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= max_length:
        return normalized
    return normalized[: max_length - 3].rstrip() + "..."


def _answer_from_chunks(query: str, chunks: list[dict[str, str]]) -> str:
    if not chunks:
        return (
            "The configured Azure Search index does not contain enough information "
            f"to answer: {query}"
        )
    return " ".join(
        " ".join(chunk["text"].split())[:500]
        for chunk in chunks[:3]
        if chunk["text"].strip()
    )
