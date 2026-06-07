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

Phase 8 turns these capabilities into a reusable agentic platform:

- A six-tool MCP server can start simulacrums, inspect situations, apply decisions, branch saved sessions, generate competence reports, and retrieve aggregate manager risk.
- Microsoft Learn MCP provides live certification-grounded context when available, with a clearly labeled synthetic local fallback when unavailable.
- Time-travel replay compares an original path with an alternative decision path across competence score, severity, and revenue-at-risk.
- Replay is described and implemented as a deterministic replay projection, not an exact production rollback.

## Data Boundary

All data is synthetic demonstration data. No real employee, customer, telemetry, or secret data is included.

Reports use cited synthetic evidence from approved local documents and simulation outcomes. Certification alignment is synthetic readiness guidance only.

Microsoft Learn MCP results are used only when the live adapter succeeds. Fallback results remain synthetic local guidance and are not presented as official certification documentation.

## Future Work

- Foundry IQ grounded knowledge with citations.
- Fabric-backed ontology mapping.
- Live or approved synthetic Work IQ adapters.
- Production-grade replay checkpoints and persisted branch graphs.
- External MCP client packaging and deployment profiles.
