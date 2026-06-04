# CRISOL

The enterprise holodeck for role readiness, operational judgment, and revenue-aware practice.

## What CRISOL Does

CRISOL turns enterprise learning into realistic, measurable practice. It connects synthetic learner profiles, role requirements, system dependencies, contracts, certifications, and scenario seeds into an ontology graph. The first backend slice can answer questions such as:

- Which systems are affected when a critical service fails?
- How much synthetic hourly revenue is at risk?
- How ready is a learner for a target role?
- Which skills and certifications are missing?

The Phase 1 scaffold is intentionally local and synthetic. It creates the backend foundation before any live integrations or frontend work.

## Why It Is Different

Most learning systems track course completion. CRISOL models business consequence. A learner can practice incident response, certification readiness, escalation judgment, and cross-role coordination against a graph that connects skills to systems, systems to contracts, and contracts to revenue exposure.

## Architecture Overview

Phase 1 includes:

- A FastAPI backend service.
- A NetworkX ontology graph loader.
- Synthetic learners, roles, skills, certifications, systems, contracts, scenarios, and work rhythm signals.
- Starter knowledge documents for later grounded retrieval.
- A simple revenue-at-risk calculation based on affected systems and dependent contracts.

The backend exposes:

- `GET /health`
- `GET /ontology/summary`
- `GET /ontology/revenue-at-risk?systems=SVC-checkout`

## Microsoft IQ Integration Plan

CRISOL uses an honest phased integration model:

- Foundry IQ: Phase 2 will connect grounded knowledge with citations. Phase 1 only prepares synthetic knowledge files.
- Fabric IQ Ontology: Phase 1 uses a local NetworkX graph and a small adapter boundary so the ontology can later map to Fabric-backed entities.
- Work IQ: Phase 1 uses synthetic work rhythm signals through local JSON data. Live signals are not implemented yet.

## Synthetic Data Disclaimer

All Phase 1 data is synthetic demonstration data. Learner IDs, contract IDs, systems, scenarios, and documents are fabricated. Do not add real names, real emails, customer data, production telemetry, secrets, or personally identifiable information.

## Local Run Commands

```powershell
cd backend
python -m app.ontology.load
uvicorn app.main:app --reload
```

After starting the server, open:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/ontology/summary
http://127.0.0.1:8000/ontology/revenue-at-risk?systems=SVC-checkout
```

## Phase Status

- [x] Pre-flight setup files exist.
- [x] Local `.env` is ignored.
- [x] Phase 1 backend scaffold.
- [x] Synthetic ontology data.
- [x] Ontology graph loader.
- [x] Revenue-at-risk endpoint.
- [x] Health endpoint.
- [ ] Phase 2 Foundry IQ integration.
- [ ] Next.js frontend.
