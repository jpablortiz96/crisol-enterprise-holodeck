# Deployment

## Local Production Run

Install dependencies in an isolated Python environment, configure required environment variables outside source control, and start Uvicorn without reload mode:

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Run the frontend separately:

```powershell
cd frontend
npm ci
npm run build
npm run start
```

Set `NEXT_PUBLIC_CRISOL_API_URL` during the frontend build so browser requests target the deployed backend.

## Container

Build from the backend directory:

```powershell
docker build -t crisol-backend:local .
docker run --rm -p 8000:8000 --env-file <secure-runtime-env-file> crisol-backend:local
```

The image excludes `.env`, local sessions, generated audio, telemetry, virtual environments, logs, and build output. Mount durable storage only when saved sessions or local telemetry must survive container replacement.

## Azure Container Apps

1. Push the backend image to Azure Container Registry.
2. Deploy an Azure Container App with ingress on port `8000`.
3. Store secrets in Container Apps secrets or Azure Key Vault references.
4. Use a managed identity for Azure project and search access where supported.
5. Configure minimum replicas, health probes against `/health`, and log collection.
6. Build the frontend with the public backend URL and deploy it independently.

## Azure App Service

Use a Linux Web App configured for a custom container or Python 3.11. Set the startup command to:

```text
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Keep application settings in App Service configuration and use Key Vault references for secrets. Enable health checks on `/health`.

## Hosted Agent Direction

The CRISOL MCP server can be registered as a tool surface for a hosted agent. A production deployment should expose the MCP transport behind authenticated network controls, keep scenario execution permissions separate from administrative operations, and use managed identity for Azure dependencies. CRISOL does not execute production changes.
