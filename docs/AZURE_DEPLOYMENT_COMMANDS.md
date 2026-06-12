# Azure Container Apps Deployment Commands

This runbook deploys the CRISOL backend and frontend to Azure Container Apps.
Use placeholders and process-scoped variables. Do not write credentials to
repository files.

## Variables

```powershell
$SUBSCRIPTION_ID = "<subscription-id>"
$RESOURCE_GROUP = "rg-crisol-prod"
$LOCATION = "eastus"
$ENVIRONMENT = "crisol-env"
$REGISTRY = "<globally-unique-acr-name>"
$BACKEND_APP = "crisol-api"
$FRONTEND_APP = "crisol-web"
$BACKEND_IMAGE = "$REGISTRY.azurecr.io/crisol-api:latest"
$FRONTEND_IMAGE = "$REGISTRY.azurecr.io/crisol-web:latest"
```

## Login and providers

```powershell
az login
az account set --subscription $SUBSCRIPTION_ID
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights
az provider register --namespace Microsoft.ContainerRegistry
az provider register --namespace Microsoft.Search
```

## Resource group, registry, and environment

```powershell
az group create --name $RESOURCE_GROUP --location $LOCATION
az acr create `
  --name $REGISTRY `
  --resource-group $RESOURCE_GROUP `
  --location $LOCATION `
  --sku Basic

az containerapp env create `
  --name $ENVIRONMENT `
  --resource-group $RESOURCE_GROUP `
  --location $LOCATION
```

## Build images

```powershell
az acr build `
  --registry $REGISTRY `
  --image "crisol-api:latest" `
  backend
```

The frontend public API address is embedded during the Next.js build. Deploy
the backend first, capture its URL, then build the frontend image with that
address:

```powershell
az containerapp create `
  --name $BACKEND_APP `
  --resource-group $RESOURCE_GROUP `
  --environment $ENVIRONMENT `
  --image $BACKEND_IMAGE `
  --target-port 8000 `
  --ingress external `
  --registry-server "$REGISTRY.azurecr.io"

$BACKEND_FQDN = az containerapp show `
  --name $BACKEND_APP `
  --resource-group $RESOURCE_GROUP `
  --query properties.configuration.ingress.fqdn `
  --output tsv
$BACKEND_URL = "https://$BACKEND_FQDN"

az acr build `
  --registry $REGISTRY `
  --image "crisol-web:latest" `
  --build-arg "NEXT_PUBLIC_CRISOL_API_URL=$BACKEND_URL" `
  frontend

az containerapp create `
  --name $FRONTEND_APP `
  --resource-group $RESOURCE_GROUP `
  --environment $ENVIRONMENT `
  --image $FRONTEND_IMAGE `
  --target-port 3000 `
  --ingress external `
  --registry-server "$REGISTRY.azurecr.io" `
  --env-vars "NEXT_PUBLIC_CRISOL_API_URL=$BACKEND_URL"
```

## Configure CORS

```powershell
$FRONTEND_FQDN = az containerapp show `
  --name $FRONTEND_APP `
  --resource-group $RESOURCE_GROUP `
  --query properties.configuration.ingress.fqdn `
  --output tsv
$FRONTEND_URL = "https://$FRONTEND_FQDN"

az containerapp update `
  --name $BACKEND_APP `
  --resource-group $RESOURCE_GROUP `
  --set-env-vars "FRONTEND_URL=$FRONTEND_URL"
```

Configure Search and Foundry variables using the secret workflow in
[FOUNDRY_IQ_SETUP.md](FOUNDRY_IQ_SETUP.md).

## Verify

```powershell
Invoke-RestMethod "$BACKEND_URL/health"
Invoke-RestMethod "$BACKEND_URL/grounding/status"
Invoke-WebRequest $FRONTEND_URL

az containerapp logs show `
  --name $BACKEND_APP `
  --resource-group $RESOURCE_GROUP `
  --follow
```

## Clean up

This deletes the entire resource group:

```powershell
az group delete --name $RESOURCE_GROUP --yes --no-wait
```
