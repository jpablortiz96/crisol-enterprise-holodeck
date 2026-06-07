import asyncio
import json
import os
from datetime import timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

import httpx

from app.grounding.local_knowledge import search_knowledge


DEFAULT_LEARN_MCP_URL = "https://learn.microsoft.com/api/mcp"
FALLBACK_MESSAGE = (
    "Microsoft Learn MCP is documented as the preferred live grounding source; "
    "local fallback is active."
)
CERTIFICATIONS_FILE = Path(__file__).resolve().parents[1] / "data" / "certifications.json"


def is_learn_mcp_configured() -> bool:
    return bool(_learn_mcp_url())


@lru_cache(maxsize=64)
def search_learn_docs(query: str, top_k: int = 3) -> dict[str, Any]:
    normalized_query = query.strip()
    if not normalized_query:
        return _local_fallback(query, top_k)

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        pass
    else:
        return _local_fallback(normalized_query, top_k)

    try:
        return asyncio.run(_search_live(normalized_query, top_k))
    except Exception:
        return _local_fallback(normalized_query, top_k)


@lru_cache(maxsize=16)
def certification_context(certification_id: str) -> dict[str, Any]:
    normalized_id = certification_id.strip().upper()
    certification = next(
        (item for item in _load_certifications() if item["id"].upper() == normalized_id),
        None,
    )
    query_parts = [normalized_id, "certification readiness"]
    if certification:
        query_parts.extend([certification["name"], *certification.get("covers_skills", [])])
    result = search_learn_docs(" ".join(query_parts), top_k=3)
    return {
        "certification_id": normalized_id,
        "certification": certification,
        **result,
    }


async def _search_live(query: str, top_k: int) -> dict[str, Any]:
    from mcp import ClientSession
    from mcp.client.streamable_http import streamable_http_client

    timeout_seconds = _timeout_seconds()
    timeout = httpx.Timeout(timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        async with streamable_http_client(
            _learn_mcp_url(),
            http_client=client,
            terminate_on_close=True,
        ) as (read_stream, write_stream, _):
            async with ClientSession(
                read_stream,
                write_stream,
                read_timeout_seconds=timedelta(seconds=timeout_seconds),
            ) as session:
                await session.initialize()
                tools = await session.list_tools()
                search_tool = _select_search_tool(tools.tools)
                if search_tool is None:
                    raise ValueError("Microsoft Learn MCP search tool is unavailable.")
                result = await session.call_tool(
                    search_tool.name,
                    arguments=_search_arguments(search_tool.inputSchema, query, top_k),
                    read_timeout_seconds=timedelta(seconds=timeout_seconds),
                )

    results = _normalize_live_result(result, top_k)
    if not results:
        raise ValueError("Microsoft Learn MCP returned no usable search results.")
    return {
        "mode": "learn-mcp",
        "query": query,
        "results": results,
        "message": "Live Microsoft Learn MCP grounding is active.",
    }


def _select_search_tool(tools: list[Any]) -> Any | None:
    preferred_names = (
        "microsoft_docs_search",
        "search_microsoft_learn",
        "search",
    )
    by_name = {tool.name: tool for tool in tools}
    for name in preferred_names:
        if name in by_name:
            return by_name[name]
    return next((tool for tool in tools if "search" in tool.name.lower()), None)


def _search_arguments(input_schema: dict[str, Any], query: str, top_k: int) -> dict[str, Any]:
    properties = input_schema.get("properties", {})
    arguments: dict[str, Any] = {}
    for key in ("query", "q", "search", "search_query"):
        if key in properties:
            arguments[key] = query
            break
    if not arguments:
        arguments["query"] = query
    for key in ("top_k", "limit", "count"):
        if key in properties:
            arguments[key] = top_k
            break
    return arguments


def _normalize_live_result(result: Any, top_k: int) -> list[dict[str, Any]]:
    payload = result.model_dump(mode="json") if hasattr(result, "model_dump") else {}
    structured = payload.get("structuredContent") or payload.get("structured_content")
    candidates = _candidate_results(structured)
    if candidates:
        return candidates[:top_k]

    normalized = []
    for item in payload.get("content", []):
        text = item.get("text") if isinstance(item, dict) else None
        if not text:
            continue
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = None
        parsed_candidates = _candidate_results(parsed)
        if parsed_candidates:
            normalized.extend(parsed_candidates)
        else:
            normalized.append(
                {
                    "title": "Microsoft Learn MCP result",
                    "url": None,
                    "content": " ".join(text.split())[:600],
                }
            )
    return normalized[:top_k]


def _candidate_results(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [_normalize_result_item(item) for item in payload if isinstance(item, (dict, str))]
    if not isinstance(payload, dict):
        return []
    for key in ("results", "documents", "items", "value"):
        value = payload.get(key)
        if isinstance(value, list):
            return [_normalize_result_item(item) for item in value if isinstance(item, (dict, str))]
    return []


def _normalize_result_item(item: dict[str, Any] | str) -> dict[str, Any]:
    if isinstance(item, str):
        return {"title": "Microsoft Learn MCP result", "url": None, "content": item[:600]}
    return {
        "title": item.get("title") or item.get("name") or "Microsoft Learn MCP result",
        "url": item.get("url") or item.get("href"),
        "content": (
            item.get("content")
            or item.get("excerpt")
            or item.get("summary")
            or item.get("text")
            or ""
        )[:600],
    }


def _local_fallback(query: str, top_k: int) -> dict[str, Any]:
    results = [
        {
            "title": item["title"],
            "source": "synthetic-local-knowledge",
            "file_name": item["file_name"],
            "chunk_id": item["chunk_id"],
            "content": " ".join(item["text"].split())[:600],
            "official": False,
        }
        for item in search_knowledge(query, top_k=top_k)
    ]
    return {
        "mode": "local-fallback",
        "query": query,
        "results": results,
        "message": FALLBACK_MESSAGE,
        "boundary": "Synthetic local guidance; not official certification documentation.",
    }


def _load_certifications() -> list[dict[str, Any]]:
    return json.loads(CERTIFICATIONS_FILE.read_text(encoding="utf-8"))


def _learn_mcp_url() -> str:
    return os.getenv("LEARN_MCP_URL", DEFAULT_LEARN_MCP_URL).strip()


def _timeout_seconds() -> float:
    try:
        return max(0.5, min(float(os.getenv("LEARN_MCP_TIMEOUT_SECONDS", "1.5")), 8.0))
    except ValueError:
        return 1.5
