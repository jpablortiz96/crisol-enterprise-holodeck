# CRISOL Architecture

CRISOL is a production-safe enterprise simulation platform built around a
Next.js user experience, a FastAPI core, live Azure AI Search grounding, and
deterministic decision simulation.

## Design principles

1. **Workspace-first configuration** - Organization context, roles, skills,
   knowledge, profiles, and scenarios are explicit data boundaries.
2. **Evidence over assertion** - Results retain citations and decision
   evidence.
3. **Pressure-tested judgment** - Evaluation measures action under uncertainty,
   not content recall.
4. **Bounded cloud integration** - Live services have explicit readiness and
   fallback modes.
5. **No production control plane** - Simulation consequences never execute
   production changes.
6. **Sanitized data by default** - Versioned examples and workspace content use
   sanitized training data.

## User experience layer

| Surface | Responsibility |
| --- | --- |
| Command Center | Workspace readiness, inventory, next actions, and workflow entry points. |
| Workspace Setup | Organization, role, skill, knowledge, profile, and template configuration. |
| Scenario Studio | Scenario, persona, turn, decision, and expected-outcome authoring. |
| Evaluation Room | One-shot and synchronized scenario execution with consequences and evidence. |
| Results Center | Competence report, coach plan, manager fragility map, and replay. |
| Tools & Readiness | Health, grounding, telemetry, voice, evaluation, and MCP readiness. |

The frontend is a Next.js application deployed as the `crisol-web` Azure
Container App. It reads the backend address from
`NEXT_PUBLIC_CRISOL_API_URL`.

## Core platform layer

The `crisol-api` FastAPI application owns the platform contracts:

- **Workspace Store** validates and stores generated workspace configuration.
- **Scenario Library** merges workspace scenarios with optional example packs.
- **Scenario-driven NPC Ensemble** derives stakeholder behavior from the active
  scenario.
- **Multi-agent Orchestration** coordinates the Director, NPC Ensemble,
  Consequence Engine, Examiner, and Coach.
- **Consequence Engine** models severity, affected systems, contract exposure,
  and modeled revenue at risk.
- **Examiner / Competence Report** produces weighted dimensions, evidence,
  failure modes, skill gaps, and next actions.
- **Coach** turns observed gaps into targeted practice.
- **Manager Fragility Map** aggregates sanitized session evidence without PII.
- **Time-Travel Replay** deterministically projects alternate decision paths.
- **MCP Tool Surface** exposes six reusable CRISOL operations.
- **Telemetry / Evaluation / Security Checks** enforce allowlisted telemetry,
  release contracts, citations, sanitized data, and repository hygiene.

## Grounding architecture

`GET /grounding/status` reports the active boundary:

- `live-foundry-iq` requires a configured Microsoft Foundry project endpoint,
  model deployment, and a working Azure AI Search configuration.
- `live-azure-search` indicates working Azure AI Search retrieval without a
  configured Foundry project endpoint.
- `local-fallback` indicates missing or unavailable cloud grounding.

Azure AI Search provides live retrieval over the `crisol-knowledge` index. The
index contains only sanitized knowledge records with source metadata and data
classification. Retrieval preserves the application citation contract.

Local cited retrieval remains available for offline development and runtime
failure fallback. The mode is included in API metadata so the product does not
claim a cloud path that did not answer the request.

## Azure runtime

The verified production resource group contains:

| Resource | Role |
| --- | --- |
| Azure Container App `crisol-web` | Public Next.js product surface. |
| Azure Container App `crisol-api` | Public FastAPI product API. |
| Container Apps Environment `crisol-env` | Shared managed container runtime. |
| Azure Container Registry | Image build and storage. |
| Azure AI Search | Live grounded retrieval for `crisol-knowledge`. |
| Foundry/AIServices resource and project | Foundry project endpoint and model deployment boundary. |
| Log Analytics workspace | Container Apps platform and application logs. |
| Azure Speech | Optional scenario-persona voice synthesis when configured. |

The current public grounding endpoint reports `live-foundry-iq`. Azure Speech
remains independently optional; the simulation uses synchronized text fallback
when speech credentials are absent.

## Data boundaries

### Versioned data

- Sanitized example scenario packs.
- Sanitized example knowledge documents.
- Ontology fixtures for systems, contracts, skills, roles, and certifications.
- Validation rules and templates.

### Generated workspace data

- Workspace configuration.
- Workspace scenarios and knowledge.
- Workspace roles, skills, and profiles.

Generated workspace content is excluded from Git.

### Runtime data

- Completed sessions.
- Synthesized audio.
- Allowlisted telemetry.
- Workspace exports.

Runtime directories are excluded from Git and are not deployment secrets.

## Request flow

1. The browser loads `crisol-web`.
2. The frontend initializes product state from `crisol-api`.
3. Workspace and scenario services select sanitized configuration.
4. The orchestration loop runs scenario-driven agents and consequences.
5. Grounding queries Azure AI Search first when live retrieval is available.
6. Local cited retrieval handles offline or cloud-failure fallback.
7. The Examiner and Coach produce cited reports.
8. Session, replay, telemetry, and manager services persist generated runtime
   state outside source control.
9. The frontend renders decision timelines, evidence, and readiness insights.

## Simulation safety

CRISOL models operational and commercial consequences but does not execute
production actions. Revenue-at-risk values are modeled scenario signals, not
financial forecasts or observed customer losses.

The platform requires no real employee or customer PII. Human reviewers remain
responsible for employment, access, certification, and operational decisions.

## Detailed diagram

See [ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md).
