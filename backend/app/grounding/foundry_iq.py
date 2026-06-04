import os
from typing import Any

from app.grounding.local_knowledge import answer_with_citations


REQUIRED_ENV_VARS = [
    "AZURE_AI_PROJECT_ENDPOINT",
    "AZURE_AI_MODEL_DEPLOYMENT",
    "AZURE_SEARCH_ENDPOINT",
    "CRISOL_KNOWLEDGE_BASE",
]


def is_foundry_configured() -> bool:
    return all(os.getenv(name) for name in REQUIRED_ENV_VARS)


def grounded_answer(query: str, top_k: int = 5) -> dict[str, Any]:
    local_answer = answer_with_citations(query, top_k=top_k)

    if not is_foundry_configured():
        return local_answer

    # TODO: Add the live Foundry IQ retrieval call when the Azure project,
    # search index, credential flow, and citation contract are finalized.
    return {
        **local_answer,
        "mode": "local-fallback",
    }
