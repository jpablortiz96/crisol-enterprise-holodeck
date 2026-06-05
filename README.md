# CRISOL

The enterprise holodeck for role readiness, operational judgment, and revenue-aware practice.

## What CRISOL Does

CRISOL turns enterprise learning into realistic, measurable practice. It connects synthetic learner profiles, role requirements, system dependencies, contracts, certifications, and scenario seeds into an ontology graph. The first backend slice can answer questions such as:

- Which systems are affected when a critical service fails?
- How much synthetic hourly revenue is at risk?
- How ready is a learner for a target role?
- Which skills and certifications are missing?

The Phase 1 scaffold is intentionally local and synthetic. Phase 2 adds a local citation-first grounding layer over approved synthetic documents, plus a Foundry IQ adapter skeleton for later live configuration. Phase 3 adds the first deterministic multi-agent simulation loop for terminal demos. Phase 4 adds replay-ready branching timelines and local session storage. Phase 5 adds competence reporting and aggregate manager insights. Phase 6 adds the first browser-based War-Room frontend. Phase 7 adds live scenario playback over Server-Sent Events and cinematic War-Room updates. Phase 7.2 makes Azure Speech the primary NPC voice layer while retaining a safe text-only fallback.

## Why It Is Different

Most learning systems track course completion. CRISOL models business consequence. A learner can practice incident response, certification readiness, escalation judgment, and cross-role coordination against a graph that connects skills to systems, systems to contracts, and contracts to revenue exposure.

## Architecture Overview

The current backend includes:

- A FastAPI backend service.
- A NetworkX ontology graph loader.
- Synthetic learners, roles, skills, certifications, systems, contracts, scenarios, and work rhythm signals.
- Synthetic knowledge documents used as the approved local knowledge base.
- A simple revenue-at-risk calculation based on affected systems and dependent contracts.
- A local citation fallback for grounded answers.
- A Foundry IQ adapter boundary that falls back locally until Azure resources are configured.
- A local multi-agent simulation loop for seeded incident practice.
- A branching timeline with parented decision nodes, cascade paths, revenue deltas, and contract exposure.
- Local ignored session storage under `backend/.crisol_sessions/`.
- A weighted competence report with cited evidence, skill gaps, certification alignment, and next best actions.
- A no-PII manager fragility map over saved synthetic sessions.
- A Next.js War-Room dashboard for running simulations, viewing the timeline, reading reports, and showing manager aggregate risk.
- A streaming scenario endpoint for live playback in the War-Room.
- Azure Speech synthesis for NPC reactions when configured.
- Per-session MP3 caching under ignored local storage at `backend/.crisol_audio/`.
- A safe text-only fallback when Speech credentials, SDK support, or synthesis are unavailable.

The backend exposes:

- `GET /health`
- `GET /ontology/summary`
- `GET /ontology/revenue-at-risk?systems=SVC-checkout`
- `GET /grounding/test?q=checkout%20outage%20database%20recovery`
- `GET /scenario/run?role_id=ROLE-SRE`
- `GET /scenario/stream?role_id=ROLE-SRE`
- `GET /voice/status`
- `GET /voice/test?text=hello&persona=VP%20Operations`
- `GET /scenario/run/timeline?role_id=ROLE-SRE`
- `GET /scenario/sessions`
- `GET /scenario/{session_id}`
- `GET /scenario/{session_id}/timeline`
- `GET /reports/competence/{session_id}`
- `GET /reports/latest`
- `GET /manager/fragility-map`
- `GET /manager/readiness-summary`

## Microsoft IQ Integration Plan

CRISOL uses an honest phased integration model:

- Foundry IQ: Phase 2 adds the adapter skeleton and local citation fallback. Live indexing requires Azure project and search configuration.
- Fabric IQ Ontology: Phase 1 uses a local NetworkX graph and a small adapter boundary so the ontology can later map to Fabric-backed entities.
- Work IQ: Phase 1 uses synthetic work rhythm signals through local JSON data. Live signals are not implemented yet.

Every grounded answer must include citations. If the approved synthetic knowledge base does not contain enough information, the backend returns a safe no-answer response instead of fabricating support.

## Synthetic Data Disclaimer

All Phase 1 data is synthetic demonstration data. Learner IDs, contract IDs, systems, scenarios, and documents are fabricated. Do not add real names, real emails, customer data, production telemetry, secrets, or personally identifiable information.

## Local Run Commands

Backend checks:

```powershell
cd backend
python -m app.validate_phase5
python -m app.validate_phase7
python -m app.validate_phase4
python -m app.run_scenario --role ROLE-SRE
python -m app.grounding.build_knowledge_base
python -m app.grounding.test_grounding
python -m app.ontology.load
uvicorn app.main:app --reload
```

Browser demo:

Terminal 1:

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

Terminal 2:

```powershell
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

The War-Room includes two demo buttons:

- `Run SRE Simulation`
- `Play Live Simulation`

`Play Live Simulation` connects to `GET /scenario/stream?role_id=ROLE-SRE` and updates the event rail, scenario feed, timeline, consequence metrics, competence score, coach plan, and manager snapshot as events arrive. With Voice enabled, Azure Speech audio is queued so NPC lines do not overlap. Without valid Speech configuration, NPC reactions continue through the text-only fallback.

## Azure Speech

Azure Speech is the primary NPC voice layer. Configure these variables in the local ignored `.env` file or the process environment:

```text
AZURE_SPEECH_KEY=
AZURE_SPEECH_REGION=
```

Persona voices can be overridden with:

```text
AZURE_SPEECH_VOICE_VP=
AZURE_SPEECH_VOICE_PM=
AZURE_SPEECH_VOICE_DB=
AZURE_SPEECH_VOICE_SUPPORT=
```

Generated MP3 files are cached per session under `backend/.crisol_audio/`. The directory is ignored and must not be committed. The Speech key is read only by the backend and is never returned to the frontend.

After starting the server, open:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/ontology/summary
http://127.0.0.1:8000/ontology/revenue-at-risk?systems=SVC-checkout
http://127.0.0.1:8000/grounding/test?q=checkout%20outage%20database%20recovery
http://127.0.0.1:8000/scenario/run?role_id=ROLE-SRE
http://127.0.0.1:8000/scenario/stream?role_id=ROLE-SRE
http://127.0.0.1:8000/voice/status
http://127.0.0.1:8000/voice/test?text=Checkout%20is%20down%20and%20revenue%20is%20at%20risk&persona=VP%20Operations
http://127.0.0.1:8000/scenario/run/timeline?role_id=ROLE-SRE
http://127.0.0.1:8000/scenario/sessions
http://127.0.0.1:8000/reports/latest
http://127.0.0.1:8000/manager/fragility-map
http://127.0.0.1:8000/manager/readiness-summary
```

## Phase Status

- [x] Pre-flight setup files exist.
- [x] Local `.env` is ignored.
- [x] Phase 1 backend scaffold.
- [x] Synthetic ontology data.
- [x] Ontology graph loader.
- [x] Revenue-at-risk endpoint.
- [x] Health endpoint.
- [x] Phase 2 local citation fallback.
- [x] Phase 2 Foundry IQ adapter skeleton.
- [x] Phase 3 deterministic terminal simulation loop.
- [x] Phase 3 scenario run API endpoint.
- [x] Phase 4 branching timeline.
- [x] Phase 4 local session replay storage.
- [x] Phase 4 validation script.
- [x] Phase 5 scored competence report.
- [x] Phase 5 manager fragility map.
- [x] Phase 5 validation script.
- [x] Phase 6 War-Room frontend.
- [x] Phase 7 SSE live playback.
- [x] Phase 7 optional speech fallback.
- [x] Phase 7.2 Azure Speech synthesis and queued NPC playback.
- [ ] Live Foundry IQ indexing and retrieval.
