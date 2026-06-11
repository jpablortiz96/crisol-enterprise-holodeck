import os
from typing import Any

from app.grounding.azure_search_client import (
    AzureSearchError,
    search_azure_knowledge,
)


def _configured(name: str) -> bool:
    return bool(os.getenv(name, "").strip())


def get_grounding_status() -> dict[str, Any]:
    foundry_project_configured = _configured("AZURE_AI_PROJECT_ENDPOINT")
    model_deployment_configured = _configured("AZURE_AI_MODEL_DEPLOYMENT")
    search_index = os.getenv("AZURE_SEARCH_INDEX", "").strip()
    azure_search_configured = bool(
        _configured("AZURE_SEARCH_ENDPOINT")
        and search_index
        and _configured("AZURE_SEARCH_KEY")
    )
    azure_search_working = False
    search_warning = ""
    if azure_search_configured:
        try:
            search_azure_knowledge("*", top=1)
            azure_search_working = True
        except AzureSearchError:
            search_warning = (
                "Azure Search is configured but unavailable; "
                "local knowledge fallback is active."
            )

    if (
        foundry_project_configured
        and model_deployment_configured
        and azure_search_working
    ):
        mode = "live-foundry-iq"
    elif azure_search_working:
        mode = "live-azure-search"
    else:
        mode = "local-fallback"

    warnings: list[str] = []
    if not azure_search_configured:
        warnings.append(
            "Azure Search is not fully configured; local knowledge fallback is active."
        )
    elif search_warning:
        warnings.append(search_warning)
    if not foundry_project_configured:
        warnings.append("Microsoft Foundry project endpoint is not configured.")
    if not model_deployment_configured:
        warnings.append("Microsoft Foundry model deployment is not configured.")

    return {
        "mode": mode,
        "foundry_project_configured": foundry_project_configured,
        "model_deployment_configured": model_deployment_configured,
        "azure_search_configured": azure_search_configured,
        "search_index": search_index,
        "warnings": warnings,
    }
