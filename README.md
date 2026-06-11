# CRISOL - Enterprise Holodeck

CRISOL is a revenue-aware readiness platform for practicing high-stakes enterprise decisions before they affect production.

## What It Does

CRISOL turns role requirements, system dependencies, business exposure, certifications, and sanitized scenario packs into measurable operational practice. Participants make decisions inside a branching simulation, receive synchronized stakeholder pressure, and finish with cited competence evidence and manager-level readiness signals.

## Why It Matters

Course completion does not prove judgment under pressure. CRISOL evaluates how a participant detects risk, controls business impact, communicates, escalates, and recovers when several systems and stakeholders are moving at once.

The platform is designed for:

- Operational readiness and incident-response practice.
- Role-transition and certification preparation.
- Cross-functional decision training.
- Evidence-based coaching and manager planning.
- Safe exploration of alternative decisions without production changes.

## Product Capabilities

- Empty-by-default configurable enterprise workspace.
- Validated workspace export and import packages.
- Guided first-customer walkthrough with actionable setup state.
- Scenario-driven NPC personas with deterministic generic fallbacks.
- Scenario, knowledge, role, skill, and evaluated-profile studios.
- Workspace Scenario Library with optional validated example packs.
- One-shot and synchronized live simulations.
- Branching consequence timeline with severity and revenue deltas.
- Azure Speech NPC room with text fallback.
- Cited Competence Score and targeted coaching plan.
- Aggregate Manager Fragility Map without personal data.
- Deterministic Time-Travel Replay projections.
- Six-tool MCP surface for reusable scenario operations.
- Grounded retrieval boundaries with local fallback.
- Structured local telemetry and release evaluation.
- Recording Mode optimized for 16:9 product capture.

## Architecture

CRISOL uses a Next.js War Room and a FastAPI service. The backend combines a NetworkX ontology, a deterministic scenario director, consequence and scoring services, local ignored session storage, replay projection, speech synthesis, MCP tools, evaluation checks, and allowlisted telemetry.

```text
Next.js War Room
  -> FastAPI product API
     -> Workspace configuration and Scenario Library
     -> Ontology and business-impact graph
     -> Grounding and citation adapters
     -> Competence and manager insights
     -> Replay, MCP, voice, evaluation, telemetry
     -> Ignored local runtime storage
```

Architecture details are documented in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Microsoft Stack And IQ Integration

- **Azure Speech** provides NPC voice synthesis when configured.
- **Microsoft Learn MCP** provides live certification grounding with bounded local fallback.
- **Foundry IQ** has an adapter boundary for approved knowledge retrieval; live indexing requires Azure configuration.
- **Fabric IQ** maps to the local ontology boundary and depends on target capacity for a live adapter.
- **Work IQ** uses sanitized local work-signal fixtures until connected to approved enterprise tenant signals.
- **Azure Container Apps or App Service** are the recommended backend deployment targets.

Every scored claim and grounded answer retains citations or returns a bounded fallback result.

## Workspace Setup

CRISOL starts empty. Initialize or inspect the local workspace from `backend`:

```powershell
python -m app.workspace.setup --empty
python -m app.workspace.setup --status
python -m app.workspace.setup --with-examples
python -m app.workspace.setup --creator-operations-template
python -m app.workspace.setup --eduky-template
```

The browser setup flow exposes Start Empty, generic workspace packs, Creator Operations Readiness, the optional example pack, and a separate optional customer-specific pack. Organization name, industry, and workspace name can be configured independently of any template. Generated workspace files stay under ignored local storage and are not committed.

- [Empty workspace mode](docs/EMPTY_WORKSPACE.md)
- [Workspace setup](docs/WORKSPACE_SETUP.md)
- [First customer workspace](docs/FIRST_CUSTOMER_WORKSPACE.md)
- [Product walkthrough](docs/PRODUCT_WALKTHROUGH.md)
- [Workspace packages](docs/WORKSPACE_PACKAGES.md)
- [Eduky first-customer walkthrough](docs/FIRST_CUSTOMER_EDUKY.md)

## Workspace Packages

Export, inspect, and import the active sanitized workspace from `backend`:

```powershell
python -m app.workspace.package --export
python -m app.workspace.package --summary .crisol_exports/wpk-example.json
python -m app.workspace.package --import .crisol_exports/wpk-example.json
```

Exports are stored under ignored local storage at `backend/.crisol_exports/`. Import validates the complete package before replacing the generated workspace and keeps examples disabled.

## Scenario Library

Workspace scenarios are saved under ignored local storage at `backend/app/data/workspace/scenario_packs/`. Versioned examples are stored separately under `backend/app/data/examples/scenario_packs/` and appear only when example mode is enabled. Each pack declares fictional identifiers, role, industry, systems, decisions, success criteria, failure modes, and knowledge references. Personas are scenario-specific; when omitted, CRISOL derives a deterministic generic roster from the scenario context.

```powershell
cd backend
python -m app.scenarios.importer
```

The frontend selector drives both standard and live simulation runs. Authoring rules are in [docs/PRODUCT_SCENARIOS.md](docs/PRODUCT_SCENARIOS.md).

## Azure Speech NPC Room

When `AZURE_SPEECH_KEY` and `AZURE_SPEECH_REGION` are available to the backend process, NPC reactions are synthesized and cached under ignored local runtime storage. Without valid configuration, the same scenario remains fully usable through synchronized text fallback.

Voice credentials stay server-side and are never returned to the browser.

## MCP Tool Surface

CRISOL exposes six local tools:

- `start_simulacrum`
- `get_situation`
- `make_decision`
- `branch_from`
- `get_competence_report`
- `get_manager_fragility_map`

```powershell
cd backend
python -m app.mcp_server.server --list-tools
python -m app.mcp_server.server --serve --transport stdio
```

The web product exposes the same contracts through its Tool Preview panel.

## Time-Travel Replay

Time-Travel Replay starts from a saved decision node, substitutes an alternative action, and re-simulates the remaining path. It compares competence score, severity, revenue at risk, reasoning, and citations.

Replay is a deterministic projection for training analysis. It is not an exact production rollback.

## Competence Score And Manager Fragility Map

The Competence Score includes weighted dimensions, cited evidence, failure modes, skill gaps, certification alignment, and next actions. The Manager Fragility Map aggregates sanitized session evidence by role, dimension, skill, and certification without storing personal profiles.

These outputs support coaching and readiness planning. Human reviewers remain responsible for employment, access, certification, and operational decisions.

## Security And Data Policy

- Repository scenarios and examples use sanitized or synthetic training data.
- Real customer, employee, contact, payment, credential, and confidential incident data are prohibited.
- `.env`, virtual environments, generated sessions, audio, telemetry, build output, and dependencies are ignored.
- Telemetry accepts only an explicit field allowlist.
- The repository scanner checks credentials, sensitive-data patterns, and product language.
- CRISOL does not execute production control-plane actions.

See [docs/SECURITY.md](docs/SECURITY.md) and [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md).

## Run Locally

Backend:

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

The first launch presents an empty-workspace setup panel. Configure content manually, apply Creator Operations Readiness or another generic template, apply the separate optional customer pack, or enable the example pack.

Recording Mode is available in the command header. It preserves Scenario Library, live simulation, Azure Speech status, citations, revenue impact, timeline, Competence Score, Manager Fragility Map, Time-Travel Replay, and MCP tools while reducing technical recording noise.

## Validation Commands

```powershell
cd backend
python -m app.security.scan
python -m app.validate_workspace_package
python -m app.validate_dynamic_personas
python -m app.validate_empty_workspace
python -m app.validate_release
python -m app.validate_phase9
python -m app.validate_phase8
python -m app.validate_phase7
python -m app.validate_phase5
python -m app.validate_phase4
python -m app.maintenance.reset_local_state --seed-demo
```

```powershell
cd frontend
npm install
npm run build
```

## Deployment Notes

The backend includes a non-root Python container with a health check. Deployment guidance covers local production mode, Azure Container Apps, Azure App Service, secret stores, health probes, and MCP network controls.

- [Deployment guide](docs/DEPLOYMENT.md)
- [Docker smoke test](docs/DOCKER_SMOKE_TEST.md)
- [Release candidate report](docs/RELEASE_CANDIDATE_REPORT.md)

## Screenshot Placeholders

Capture these release images after running a clean seeded baseline:

1. War Room in Recording Mode with Scenario Library and Azure Speech status.
2. Live branching timeline with revenue delta and cited events.
3. Competence Score beside the Manager Fragility Map.
4. Time-Travel Replay branch comparison.
5. MCP Tool Preview with the six-tool registry.
