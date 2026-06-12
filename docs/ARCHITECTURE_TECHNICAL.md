# CRISOL Technical Architecture

## System boundary

CRISOL consists of a Next.js frontend (`crisol-web`) and FastAPI backend
(`crisol-api`) deployed to Azure Container Apps. The backend owns workspace,
scenario, orchestration, grounding, scoring, replay, voice, MCP, telemetry, and
validation contracts.

## Component model

| Component | Responsibility | Runtime boundary |
| --- | --- | --- |
| App Shell | Navigation, initialization, backend-unavailable behavior, and product state | Next.js / Zustand |
| Workspace Store | Organization, role, skill, knowledge, profile, scenario, and package validation | FastAPI filesystem services |
| Scenario Library | Workspace scenarios plus optional versioned examples | FastAPI scenario services |
| Persona Layer | Scenario-specific personas and deterministic fallback personas | Backend agent services |
| Multi-agent Orchestration | Director, NPC Ensemble, Consequence Engine, Examiner, and Coach coordination | Deterministic Python loop |
| Grounding Layer | Azure AI Search first, cited local fallback on failure | REST client plus local retrieval |
| Azure AI Search | Live search over sanitized indexed knowledge | `crisol-knowledge` |
| Foundry Readiness | Project endpoint and model deployment configuration status | Microsoft Foundry project boundary |
| Azure Speech | Optional neural speech synthesis and MP3 caching | Backend-only credentials |
| Consequence Engine | Severity, affected systems, contract exposure, modeled revenue at risk | NetworkX ontology and rules |
| Examiner | Weighted dimensions, evidence, failure modes, and skill gaps | Scoring services |
| Coach | Practice plan and next-best actions | Backend agent service |
| Manager Fragility Map | Aggregate role, skill, and certification readiness signals | Sanitized saved sessions |
| Time-Travel Replay | Alternate deterministic projection from a saved node | Replay service |
| MCP Tool Surface | Six reusable scenario and insight operations | FastMCP and local registry |
| Telemetry / Security / Validation | Allowlisted telemetry, endpoint checks, scans, release scoring | Local runtime plus Log Analytics for deployed logs |

## API and event contracts

The web product initializes from REST endpoints for health, workspace,
scenarios, reports, tools, telemetry, voice, and grounding status.

Scenario execution supports:

- `POST /scenario/run-custom` for a complete one-shot result.
- `GET /scenario/stream-custom` for ordered SSE playback.
- `POST /replay/branch-from` for alternate-path projection.
- `GET /grounding/status` for the live grounding boundary.
- `GET /voice/status` for the active voice provider.

The SSE lifecycle is ordered:

1. `session_started`
2. `scenario_intro`
3. `turn_started`
4. `decision_selected`
5. `npc_reaction`
6. `consequence_delta`
7. `timeline_updated`
8. `score_final`
9. `coach_plan`
10. `manager_snapshot`
11. `session_completed`

## Grounding

The grounding adapter checks Azure Search configuration and queries the Search
REST API using the `api-key` header. Search results are normalized into the
existing citation contract:

```json
{
  "doc_id": "...",
  "title": "...",
  "file_name": "...",
  "chunk_id": "...",
  "quote": "..."
}
```

Grounding modes:

- `live-foundry-iq`: Azure AI Search is working and the Foundry project and
  model deployment are configured.
- `live-azure-search`: Azure AI Search is working without the Foundry project
  endpoint.
- `local-fallback`: cloud retrieval is missing or failed.

Azure AI Search is the implemented live retrieval path. The Foundry project
and `gpt-4o` deployment are readiness configuration boundaries; the current
orchestration loop is deterministic Python and does not claim hosted Foundry
agent execution.

## Voice

The voice layer:

1. Selects a configured voice by persona or style.
2. Sanitizes generated storage paths.
3. Synthesizes audio through Azure Speech when credentials are present.
4. Caches MP3 output under ignored runtime storage.
5. Returns text-only fallback when Speech is unavailable.

The current production `GET /voice/status` response reports text-only fallback.

## Data boundaries

### Versioned

- Sanitized example scenarios and knowledge.
- Role, skill, certification, system, contract, and work-signal fixtures.
- Templates, validators, and product code.

### Generated and ignored

- Workspace configuration and content.
- Sessions.
- Audio.
- Telemetry.
- Exports.
- Build output and dependencies.

No `.env` file or runtime credential is part of the deployment image context.

## Azure topology

The verified resource group contains:

- `crisol-web` and `crisol-api` Container Apps.
- Container Apps Environment `crisol-env`.
- Azure Container Registry.
- Log Analytics workspace.
- Azure AI Search service.
- Foundry/AIServices account and project.

Azure Speech is an external optional dependency configured through backend-only
environment variables.

## Safety and validation

- CORS accepts configured frontend origins and Azure Container Apps domains.
- Secret and sensitive-data scans run as part of release validation.
- Workspace imports validate the complete package before replacement.
- Azure Search indexing validates sanitized content before upload.
- Telemetry uses an explicit allowlist.
- Simulations do not execute production control-plane actions.
- Replay is a deterministic training projection, not a production rollback.
