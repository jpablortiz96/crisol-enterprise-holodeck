# Submission Notes

## Project

CRISOL is an enterprise practice environment for role readiness and business-consequence simulation.

## Phase 1 Deliverable

The current submission includes:

- FastAPI backend scaffold.
- Local NetworkX ontology graph.
- Synthetic roles, skills, certifications, learners, contracts, systems, scenarios, and work signals.
- Revenue-at-risk calculation.
- Starter knowledge documents for later grounded retrieval.
- Documentation for architecture, agents, IQ integration, and demo flow.

## Differentiator

CRISOL connects learning readiness to operational and commercial consequences. It models how missing skills, missing certifications, system dependencies, and contract exposure can combine during an incident.

The current backend turns each run into scored readiness: weighted competence dimensions, cited evidence trail, failure modes, skill gaps, synthetic certification alignment, and next best actions.

Manager insights aggregate saved synthetic runs into a fragility map without exposing PII or individual learner identity.

## Data Boundary

All data is synthetic demonstration data. No real employee, customer, telemetry, or secret data is included.

Reports use cited synthetic evidence from approved local documents and simulation outcomes. Certification alignment is synthetic readiness guidance only.

## Future Work

- Foundry IQ grounded knowledge with citations.
- Fabric-backed ontology mapping.
- Live or approved synthetic Work IQ adapters.
- Scenario scoring and coaching workflows.
- Richer manager dashboards over aggregate readiness risk.
- Frontend experience for demos.
