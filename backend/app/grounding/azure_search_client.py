import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


AZURE_SEARCH_API_VERSION = "2024-07-01"
DEFAULT_TIMEOUT_SECONDS = 10.0


class AzureSearchError(RuntimeError):
    pass


class AzureSearchIndexNotFoundError(AzureSearchError):
    pass


def is_azure_search_available() -> bool:
    return bool(
        os.getenv("AZURE_SEARCH_ENDPOINT", "").strip()
        and os.getenv("AZURE_SEARCH_INDEX", "").strip()
        and os.getenv("AZURE_SEARCH_KEY", "").strip()
    )


def search_azure_knowledge(query: str, top: int = 5) -> list[dict[str, Any]]:
    normalized_query = query.strip()
    if not normalized_query or top < 1:
        return []
    if not is_azure_search_available():
        raise AzureSearchError("Azure Search is not fully configured.")

    index_name = quote(os.environ["AZURE_SEARCH_INDEX"].strip(), safe="")
    payload = request_azure_search(
        "POST",
        f"/indexes/{index_name}/docs/search",
        {
            "search": normalized_query,
            "top": min(top, 50),
            "select": (
                "id,title,content,source,tags,data_classification,updated_at"
            ),
        },
    )
    return [
        {
            "id": str(item.get("id", "")),
            "title": str(item.get("title", "Azure Search result")),
            "content": str(item.get("content", "")),
            "source": str(item.get("source", "")),
            "tags": [
                str(tag) for tag in item.get("tags", []) if str(tag).strip()
            ],
            "data_classification": str(
                item.get("data_classification", "")
            ),
            "updated_at": item.get("updated_at"),
            "score": item.get("@search.score", 0),
        }
        for item in payload.get("value", [])
        if isinstance(item, dict)
    ]


def request_azure_search(
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT", "").strip().rstrip("/")
    api_key = os.getenv("AZURE_SEARCH_KEY", "").strip()
    if not endpoint or not api_key:
        raise AzureSearchError("Azure Search endpoint and key are required.")

    separator = "&" if "?" in path else "?"
    url = (
        f"{endpoint}{path}{separator}"
        f"{urlencode({'api-version': AZURE_SEARCH_API_VERSION})}"
    )
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(
        url,
        data=body,
        method=method,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "api-key": api_key,
        },
    )

    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            response_body = response.read()
    except HTTPError as error:
        if error.code == 404:
            raise AzureSearchIndexNotFoundError(
                "The configured Azure Search index was not found."
            ) from error
        raise AzureSearchError(
            f"Azure Search request failed with HTTP {error.code}."
        ) from error
    except (URLError, TimeoutError) as error:
        raise AzureSearchError("Azure Search request could not connect.") from error

    if not response_body:
        return {}
    try:
        parsed = json.loads(response_body)
    except json.JSONDecodeError as error:
        raise AzureSearchError("Azure Search returned invalid JSON.") from error
    if not isinstance(parsed, dict):
        raise AzureSearchError("Azure Search returned an unexpected response.")
    return parsed
