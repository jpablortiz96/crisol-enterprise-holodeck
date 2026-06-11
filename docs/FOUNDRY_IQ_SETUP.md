# Foundry IQ and Azure Search Setup

CRISOL uses Azure AI Search for live knowledge retrieval and retains a
sanitized local fallback. Foundry readiness is reported separately so the
application does not claim a live Foundry integration when only Search is
configured.

## Environment variables

| Variable | Purpose |
| --- | --- |
| `AZURE_AI_PROJECT_ENDPOINT` | Microsoft Foundry project endpoint. Required for `live-foundry-iq` status. |
| `AZURE_AI_MODEL_DEPLOYMENT` | Model deployment name associated with the Foundry project. |
| `AZURE_SEARCH_ENDPOINT` | Azure AI Search service endpoint, such as `https://<service>.search.windows.net`. |
| `AZURE_SEARCH_INDEX` | Search index name. Use `crisol-knowledge`. |
| `AZURE_SEARCH_KEY` | Search API key. Store it as a Container Apps secret and never commit it. |
| `AZURE_OPENAI_ENDPOINT` | Optional Azure OpenAI endpoint reserved for model calls. |
| `AZURE_OPENAI_API_KEY` | Optional Azure OpenAI key. Store it as a secret. |

## Create Azure AI Search

Run these commands in PowerShell. Replace placeholders with your subscription
and a globally unique Search service name.

```powershell
$SUBSCRIPTION_ID = "<subscription-id>"
$RESOURCE_GROUP = "rg-crisol-prod"
$LOCATION = "eastus"
$SEARCH_SERVICE = "<globally-unique-search-service-name>"
$SEARCH_INDEX = "crisol-knowledge"

az login
az account set --subscription $SUBSCRIPTION_ID
az provider register --namespace Microsoft.Search
az search service create `
  --name $SEARCH_SERVICE `
  --resource-group $RESOURCE_GROUP `
  --location $LOCATION `
  --sku basic

$SEARCH_ENDPOINT = "https://$SEARCH_SERVICE.search.windows.net"
$SEARCH_ADMIN_KEY = az search admin-key show `
  --resource-group $RESOURCE_GROUP `
  --service-name $SEARCH_SERVICE `
  --query primaryKey `
  --output tsv
```

Do not print `$SEARCH_ADMIN_KEY` or persist it in a repository file.

## Create and populate the index

Set process-scoped variables and run the indexer from `backend`.

```powershell
Set-Location backend
$env:AZURE_SEARCH_ENDPOINT = $SEARCH_ENDPOINT
$env:AZURE_SEARCH_INDEX = $SEARCH_INDEX
$env:AZURE_SEARCH_KEY = $SEARCH_ADMIN_KEY

python -m app.grounding.azure_search_indexer --create-index
python -m app.grounding.azure_search_indexer --upload-local-knowledge
python -m app.grounding.azure_search_indexer --status
python -m app.validate_foundry_iq

$SEARCH_QUERY_KEY = az search query-key create `
  --name "crisol-api-query" `
  --resource-group $RESOURCE_GROUP `
  --service-name $SEARCH_SERVICE `
  --query key `
  --output tsv
```

The upload command reads Markdown only from the packaged, example, and
workspace knowledge directories. It rejects content that fails the existing
sanitized-data validation and never reads `.env`.

## Configure Azure Container Apps

```powershell
$BACKEND_APP = "crisol-api"

az containerapp secret set `
  --name $BACKEND_APP `
  --resource-group $RESOURCE_GROUP `
  --secrets "azure-search-key=$SEARCH_QUERY_KEY"

az containerapp update `
  --name $BACKEND_APP `
  --resource-group $RESOURCE_GROUP `
  --set-env-vars `
    "AZURE_SEARCH_ENDPOINT=$SEARCH_ENDPOINT" `
    "AZURE_SEARCH_INDEX=$SEARCH_INDEX" `
    "AZURE_SEARCH_KEY=secretref:azure-search-key" `
    "AZURE_AI_MODEL_DEPLOYMENT=gpt-4o"
```

When a Foundry project is available, add its non-secret endpoint:

```powershell
$FOUNDRY_PROJECT_ENDPOINT = "<foundry-project-endpoint>"

az containerapp update `
  --name $BACKEND_APP `
  --resource-group $RESOURCE_GROUP `
  --set-env-vars `
    "AZURE_AI_PROJECT_ENDPOINT=$FOUNDRY_PROJECT_ENDPOINT"
```

If Azure OpenAI credentials are required later, add the key as a Container
Apps secret and reference it with `secretref:`. Do not pass it as a plain
environment-variable value.

## Verify status

```powershell
$BACKEND_URL = az containerapp show `
  --name $BACKEND_APP `
  --resource-group $RESOURCE_GROUP `
  --query properties.configuration.ingress.fqdn `
  --output tsv

Invoke-RestMethod "https://$BACKEND_URL/grounding/status"
Invoke-RestMethod "https://$BACKEND_URL/grounding/test?q=checkout%20outage"
az containerapp logs show `
  --name $BACKEND_APP `
  --resource-group $RESOURCE_GROUP `
  --follow
```

## Grounding modes and claims

- `live-foundry-iq`: the Foundry project endpoint, model deployment, and Azure
  AI Search configuration are present. README language may claim Foundry IQ
  configuration readiness.
- `live-azure-search`: Azure AI Search is configured. README language may
  claim live Azure AI Search grounding, but must not claim live Foundry IQ.
- `local-fallback`: cloud grounding is incomplete or a Search request failed.
  README language must describe sanitized local grounding only.

The status endpoint performs a lightweight Search query before returning a
live mode. Also run `python -m app.validate_foundry_iq` and verify a cited
Search result before making a live-service claim.

Azure AI Search REST reference:
https://learn.microsoft.com/rest/api/searchservice/

Azure Container Apps secret reference:
https://learn.microsoft.com/azure/container-apps/manage-secrets
