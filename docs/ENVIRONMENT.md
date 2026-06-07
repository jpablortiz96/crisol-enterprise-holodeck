# Environment Configuration

Environment variables are supplied at runtime. Secrets must not be committed, placed in frontend code, or written to telemetry.

| Variable | Required | Purpose |
| --- | --- | --- |
| `AZURE_AI_PROJECT_ENDPOINT` | Optional | Azure AI project endpoint for configured hosted capabilities. |
| `AZURE_AI_MODEL_DEPLOYMENT` | Optional | Model deployment name used by configured Azure integrations. |
| `AZURE_SEARCH_ENDPOINT` | Optional | Azure AI Search endpoint for future live knowledge retrieval. |
| `CRISOL_KNOWLEDGE_BASE` | Optional | Logical knowledge-base identifier for configured retrieval. |
| `AZURE_SPEECH_KEY` | Optional secret | Enables Azure Speech synthesis. Text fallback remains available without it. |
| `AZURE_SPEECH_REGION` | Optional | Azure Speech region paired with the Speech key. |
| `LEARN_MCP_URL` | Optional | Microsoft Learn MCP endpoint. Defaults to `https://learn.microsoft.com/api/mcp`. |
| `LEARN_MCP_TIMEOUT_SECONDS` | Optional | Bounded timeout for Learn MCP calls. |
| `NEXT_PUBLIC_CRISOL_API_URL` | Frontend deployment | Public backend base URL embedded into the frontend build. |

The local `.env` file is ignored and must remain outside source control. Use platform secret stores for deployed environments. `NEXT_PUBLIC_*` variables are visible to browsers and must never contain secrets.
