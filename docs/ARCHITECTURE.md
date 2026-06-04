# Architecture

CRISOL models role readiness through a five-agent architecture connected to an ontology graph.

## Five-Agent Architecture

1. Director

   Selects the scenario, learner role, business stakes, time pressure, and target competencies.

2. NPC Ensemble

   Represents synthetic stakeholders such as operations leads, security reviewers, data owners, and managers.

3. Consequence Engine

   Evaluates affected systems, contract exposure, escalation paths, and revenue-at-risk.

4. Examiner

   Scores decisions against expected competencies, role requirements, certifications, and scenario outcomes.

5. Coach

   Converts performance gaps into practice recommendations, study priorities, and follow-up scenarios.

## Data Flow

1. Synthetic JSON data is loaded from `backend/app/data`.
2. `app.ontology.graph.load_ontology` builds a directed NetworkX graph.
3. The graph links learners, roles, skills, certifications, systems, contracts, scenarios, and work signals.
4. FastAPI endpoints expose health, graph summary, and revenue-at-risk views.
5. Future phases will add grounded knowledge retrieval, live ontology sources, and a frontend.

## Phase 1 Boundaries

Phase 1 does not connect to live Azure services, production telemetry, or real employee data. All data is synthetic and local.
