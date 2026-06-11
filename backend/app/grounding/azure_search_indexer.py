import argparse
import base64
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

from app.grounding.azure_search_client import (
    AZURE_SEARCH_API_VERSION,
    AzureSearchError,
    AzureSearchIndexNotFoundError,
    is_azure_search_available,
    request_azure_search,
)
from app.grounding.local_knowledge import (
    DEFAULT_KNOWLEDGE_DIR,
    load_knowledge_docs,
)
from app.scenarios.validators import validate_no_sensitive_content
from app.workspace.config import (
    EXAMPLE_KNOWLEDGE_DIR,
    WORKSPACE_KNOWLEDGE_DIR,
)


DATA_CLASSIFICATION = "sanitized-training"
KNOWLEDGE_DIRECTORIES = (
    ("packaged", DEFAULT_KNOWLEDGE_DIR),
    ("examples", EXAMPLE_KNOWLEDGE_DIR),
    ("workspace", WORKSPACE_KNOWLEDGE_DIR),
)


def create_index() -> None:
    index_name = _index_name()
    request_azure_search(
        "PUT",
        f"/indexes/{quote(index_name, safe='')}",
        {
            "name": index_name,
            "fields": [
                {"name": "id", "type": "Edm.String", "key": True},
                {
                    "name": "title",
                    "type": "Edm.String",
                    "searchable": True,
                },
                {
                    "name": "content",
                    "type": "Edm.String",
                    "searchable": True,
                },
                {
                    "name": "source",
                    "type": "Edm.String",
                    "filterable": True,
                },
                {
                    "name": "tags",
                    "type": "Collection(Edm.String)",
                    "filterable": True,
                },
                {
                    "name": "data_classification",
                    "type": "Edm.String",
                    "filterable": True,
                },
                {
                    "name": "updated_at",
                    "type": "Edm.DateTimeOffset",
                    "filterable": True,
                    "sortable": True,
                },
            ],
        },
    )
    print(f"PASS created or updated Azure Search index: {index_name}")


def upload_local_knowledge() -> None:
    documents = build_index_documents()
    if not documents:
        raise AzureSearchError("No sanitized local knowledge documents were found.")

    indexed = 0
    for offset in range(0, len(documents), 500):
        batch = documents[offset : offset + 500]
        result = request_azure_search(
            "POST",
            f"/indexes/{quote(_index_name(), safe='')}/docs/index",
            {
                "value": [
                    {"@search.action": "mergeOrUpload", **document}
                    for document in batch
                ]
            },
        )
        failures = [
            item
            for item in result.get("value", [])
            if isinstance(item, dict) and not item.get("status")
        ]
        if failures:
            raise AzureSearchError(
                f"Azure Search rejected {len(failures)} knowledge records."
            )
        indexed += len(batch)

    print(
        f"PASS uploaded {indexed} sanitized knowledge chunks "
        f"to index: {_index_name()}"
    )


def show_status() -> None:
    if not is_azure_search_available():
        print("WARN Azure Search is not fully configured.")
        return
    index_name = _index_name()
    try:
        index = request_azure_search(
            "GET",
            f"/indexes/{quote(index_name, safe='')}",
        )
    except AzureSearchIndexNotFoundError:
        print(f"WARN Azure Search index is missing: {index_name}")
        return
    print(
        json.dumps(
            {
                "configured": True,
                "index": index.get("name", index_name),
                "field_count": len(index.get("fields", [])),
                "api_version": AZURE_SEARCH_API_VERSION,
            },
            indent=2,
        )
    )


def build_index_documents() -> list[dict[str, Any]]:
    indexed_documents: list[dict[str, Any]] = []
    content_hashes: set[str] = set()

    for source_group, directory in KNOWLEDGE_DIRECTORIES:
        if not directory.exists():
            continue
        for document in load_knowledge_docs(directory):
            content_hash = hashlib.sha256(
                document["text"].encode("utf-8")
            ).hexdigest()
            if content_hash in content_hashes:
                continue
            content_hashes.add(content_hash)

            file_path = directory / document["file_name"]
            updated_at = datetime.fromtimestamp(
                file_path.stat().st_mtime,
                tz=timezone.utc,
            ).isoformat()
            source = f"{source_group}/{document['file_name']}"
            for chunk in document["chunks"]:
                record = {
                    "id": _document_key(source, chunk["chunk_id"]),
                    "title": chunk["title"],
                    "content": chunk["text"],
                    "source": source,
                    "tags": _tags(source_group, file_path),
                    "data_classification": DATA_CLASSIFICATION,
                    "updated_at": updated_at,
                }
                errors = validate_no_sensitive_content(record)
                if errors:
                    raise ValueError(
                        f"Knowledge file failed sanitized-data validation: "
                        f"{file_path.name}"
                    )
                indexed_documents.append(record)

    return indexed_documents


def _document_key(source: str, chunk_id: str) -> str:
    value = f"{source}#{chunk_id}".encode("utf-8")
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _tags(source_group: str, file_path: Path) -> list[str]:
    terms = [
        term
        for term in file_path.stem.replace("-", "_").split("_")
        if term
    ]
    return list(dict.fromkeys([source_group, *terms]))


def _index_name() -> str:
    index_name = os.getenv("AZURE_SEARCH_INDEX", "").strip()
    if not index_name:
        raise AzureSearchError("AZURE_SEARCH_INDEX is required.")
    return index_name


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Manage the CRISOL sanitized Azure Search knowledge index."
    )
    parser.add_argument("--create-index", action="store_true")
    parser.add_argument("--upload-local-knowledge", action="store_true")
    parser.add_argument("--status", action="store_true")
    arguments = parser.parse_args()

    if not any(
        (
            arguments.create_index,
            arguments.upload_local_knowledge,
            arguments.status,
        )
    ):
        parser.error("Select at least one index operation.")

    try:
        if arguments.create_index:
            create_index()
        if arguments.upload_local_knowledge:
            upload_local_knowledge()
        if arguments.status:
            show_status()
    except (AzureSearchError, ValueError) as error:
        raise SystemExit(f"FAIL {error}") from error


if __name__ == "__main__":
    main()
