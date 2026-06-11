import re
from pathlib import Path
from typing import Any


DEFAULT_KNOWLEDGE_DIR = Path(__file__).resolve().parents[1] / "data" / "knowledge"


def _tokenize(value: str) -> list[str]:
    return re.findall(r"[a-z0-9][a-z0-9/-]*", value.lower())


def _extract_title(text: str, file_path: Path) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return file_path.stem.replace("_", " ").title()


def _extract_doc_id(title: str, file_path: Path) -> str:
    matches = re.findall(r"\b[A-Z][A-Z0-9]+(?:-[A-Z0-9]+)+\b", title)
    if matches:
        return matches[-1]
    return file_path.stem.upper().replace("_", "-")


def _split_chunks(text: str) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            if current:
                chunks.append("\n".join(current).strip())
                current = []
            continue
        if stripped.startswith("#") and current:
            chunks.append("\n".join(current).strip())
            current = [stripped]
        else:
            current.append(stripped)

    if current:
        chunks.append("\n".join(current).strip())

    return [chunk for chunk in chunks if chunk]


def load_knowledge_docs(data_dir: Path | None = None) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []

    for knowledge_dir in _knowledge_directories(data_dir):
        for file_path in sorted(knowledge_dir.glob("*.md")):
            text = file_path.read_text(encoding="utf-8")
            title = _extract_title(text, file_path)
            doc_id = _extract_doc_id(title, file_path)
            chunks = [
                {
                    "doc_id": doc_id,
                    "title": title,
                    "file_name": file_path.name,
                    "chunk_id": f"{file_path.stem}#chunk-{index}",
                    "text": chunk,
                }
                for index, chunk in enumerate(_split_chunks(text), start=1)
            ]
            documents.append(
                {
                    "doc_id": doc_id,
                    "title": title,
                    "file_name": file_path.name,
                    "text": text,
                    "chunks": chunks,
                }
            )

    return documents


def _knowledge_directories(data_dir: Path | None) -> list[Path]:
    if data_dir is not None:
        return [data_dir]
    from app.workspace.config import (
        EXAMPLE_KNOWLEDGE_DIR,
        WORKSPACE_KNOWLEDGE_DIR,
        get_workspace_config,
    )

    directories = [WORKSPACE_KNOWLEDGE_DIR]
    if get_workspace_config()["load_examples"]:
        directories.append(EXAMPLE_KNOWLEDGE_DIR)
    return directories


def _score_chunk(query: str, chunk_text: str) -> int:
    query_terms = _tokenize(query)
    if not query_terms:
        return 0

    query_lower = query.lower().strip()
    chunk_lower = chunk_text.lower()
    score = sum(chunk_lower.count(term) for term in query_terms)

    if query_lower and query_lower in chunk_lower:
        score += max(8, len(query_terms) * 3)

    return score


def search_knowledge(query: str, top_k: int = 5, data_dir: Path | None = None) -> list[dict[str, Any]]:
    if top_k < 1:
        return []

    results: list[dict[str, Any]] = []
    for document in load_knowledge_docs(data_dir):
        for chunk in document["chunks"]:
            score = _score_chunk(query, chunk["text"])
            if score > 0:
                results.append({**chunk, "score": score})

    return sorted(results, key=lambda item: (-item["score"], item["file_name"], item["chunk_id"]))[:top_k]


def _short_quote(text: str, max_length: int = 220) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= max_length:
        return normalized
    return normalized[: max_length - 3].rstrip() + "..."


def _answer_from_chunks(query: str, chunks: list[dict[str, Any]]) -> str:
    if not chunks:
        return (
            "The approved synthetic knowledge base does not contain enough information "
            f"to answer: {query}"
        )

    snippets = []
    for chunk in chunks[:3]:
        text = re.sub(r"^#+\s*", "", chunk["text"]).strip()
        first_sentence = re.split(r"(?<=[.!?])\s+", " ".join(text.split()))[0]
        snippets.append(first_sentence)

    return " ".join(snippets)


def answer_with_citations(
    query: str,
    top_k: int = 5,
    data_dir: Path | None = None,
) -> dict[str, Any]:
    chunks = search_knowledge(query, top_k=top_k, data_dir=data_dir)
    if not chunks and data_dir is None:
        chunks = search_knowledge(
            query,
            top_k=top_k,
            data_dir=DEFAULT_KNOWLEDGE_DIR,
        )
    citations = [
        {
            "doc_id": chunk["doc_id"],
            "title": chunk["title"],
            "file_name": chunk["file_name"],
            "chunk_id": chunk["chunk_id"],
            "quote": _short_quote(chunk["text"]),
        }
        for chunk in chunks
    ]

    if not citations:
        return {
            "answer": _answer_from_chunks(query, []),
            "citations": [],
            "mode": "local",
        }

    return {
        "answer": _answer_from_chunks(query, chunks),
        "citations": citations,
        "mode": "local",
    }
