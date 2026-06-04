# CRISOL

The enterprise holodeck for role readiness, operational judgment, and revenue-aware practice.

## What CRISOL Does

CRISOL turns enterprise learning into realistic, measurable practice. It connects synthetic learner profiles, role requirements, system dependencies, contracts, certifications, and scenario seeds into an ontology graph. The first backend slice can answer questions such as:

- Which systems are affected when a critical service fails?
- How much synthetic hourly revenue is at risk?
- How ready is a learner for a target role?
- Which skills and certifications are missing?

The Phase 1 scaffold is intentionally local and synthetic. Phase 2 adds a local citation-first grounding layer over approved synthetic documents, plus a Foundry IQ adapter skeleton for later live configuration. Phase 3 adds the first deterministic multi-agent simulation loop for terminal demos. Phase 4 adds replay-ready branching timelines and local session storage. Phase 5 adds competence reporting and aggregate manager insights.

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

The backend exposes:

- `GET /health`
- `GET /ontology/summary`
- `GET /ontology/revenue-at-risk?systems=SVC-checkout`
- `GET /grounding/test?q=checkout%20outage%20database%20recovery`
- `GET /scenario/run?role_id=ROLE-SRE`
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

```powershell
cd backend
python -m app.validate_phase5
python -m app.validate_phase4
python -m app.run_scenario --role ROLE-SRE
python -m app.grounding.build_knowledge_base
python -m app.grounding.test_grounding
python -m app.ontology.load
uvicorn app.main:app --reload
```

After starting the server, open:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/ontology/summary
http://127.0.0.1:8000/ontology/revenue-at-risk?systems=SVC-checkout
http://127.0.0.1:8000/grounding/test?q=checkout%20outage%20database%20recovery
http://127.0.0.1:8000/scenario/run?role_id=ROLE-SRE
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
- [ ] Live Foundry IQ indexing and retrieval.
- [ ] Next.js frontend.
