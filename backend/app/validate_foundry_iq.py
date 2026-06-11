import json

from app.grounding.azure_search_client import (
    AzureSearchError,
    AzureSearchIndexNotFoundError,
    search_azure_knowledge,
)
from app.grounding.local_knowledge import (
    DEFAULT_KNOWLEDGE_DIR,
    answer_with_citations,
)
from app.grounding.status import get_grounding_status


INDEX_SETUP_COMMAND = (
    "Run python -m app.grounding.azure_search_indexer "
    "--create-index --upload-local-knowledge"
)


def main() -> None:
    warnings: list[str] = []
    status = get_grounding_status()
    print("grounding status:")
    print(json.dumps(status, indent=2))

    local_result = answer_with_citations(
        "checkout outage database recovery",
        top_k=3,
        data_dir=DEFAULT_KNOWLEDGE_DIR,
    )
    if not local_result.get("answer") or not local_result.get("citations"):
        raise SystemExit("FAIL local grounding fallback did not return cited content.")
    print(
        f"local fallback: PASS "
        f"({len(local_result['citations'])} citations)"
    )

    if status["azure_search_configured"]:
        try:
            results = search_azure_knowledge(
                "checkout outage database recovery",
                top=3,
            )
            print(f"Azure Search query: PASS ({len(results)} results)")
            if not results:
                warnings.append(
                    "Azure Search is reachable, but the query returned no results."
                )
        except AzureSearchIndexNotFoundError:
            warnings.append(INDEX_SETUP_COMMAND)
        except AzureSearchError as error:
            warnings.append(str(error))
    else:
        warnings.append(
            "Azure Search is not fully configured; cloud retrieval was not tested."
        )

    if not status["foundry_project_configured"]:
        warnings.append("Microsoft Foundry project endpoint is not configured.")
    if not status["model_deployment_configured"]:
        warnings.append("Microsoft Foundry model deployment is not configured.")

    for warning in dict.fromkeys(warnings):
        print(f"WARNING: {warning}")

    if warnings:
        print("PASS with WARNINGS")
    else:
        print("PASS")


if __name__ == "__main__":
    main()
