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
4. Synthetic markdown knowledge files are loaded from `backend/app/data/knowledge`.
5. `app.grounding.local_knowledge` returns cited local answers from approved synthetic documents.
6. `app.grounding.foundry_iq` provides the adapter boundary for future live Foundry IQ retrieval.
7. `app.orchestration.turn_loop` runs the local five-agent simulation loop.
8. `app.branching.timeline` builds parented branch nodes and edges for replay.
9. `app.storage.session_store` saves completed sessions under ignored local JSON storage.
10. FastAPI endpoints expose health, graph summary, revenue-at-risk, grounding test, scenario run, saved sessions, and timeline views.
11. Future phases will add live indexing, hosted agents, live ontology sources, and a frontend.

## Local Orchestration Loop

Phase 3 runs a deterministic terminal simulation:

1. The Director selects the SRE scenario and builds each turn context.
2. The auto learner makes a seeded decision, including an early bad restart decision.
3. The Consequence Engine computes severity, affected systems, branch nodes, and revenue-at-risk.
4. The NPC Ensemble reacts to the decision and current severity.
5. After at least five turns, the Examiner scores competence dimensions.
6. The Coach returns a micro-learning plan with citations.

## Branching Timeline

Phase 4 makes the consequence chain replay-ready:

- Every run starts with `NODE-ROOT`.
- Every learner decision creates a `NODE-###` branch node with `parent_node_id`.
- Edges carry decision labels for future graph rendering.
- Consequences include newly affected systems, recovered systems, cascade paths, contract exposure, and revenue deltas.
- The timeline summary tracks max severity, max revenue-at-risk, final severity, and final revenue-at-risk.

The JSON shape is ready for a future ReactFlow frontend, but no frontend is created in this phase.

## Phase Boundaries

Phase 1 does not connect to live Azure services, production telemetry, or real employee data. All data is synthetic and local.

Phase 2 adds local cited retrieval and an adapter skeleton. Live Foundry IQ indexing and retrieval remain configuration-driven future work.

Phase 3 adds local deterministic agent orchestration. It does not require live Azure credentials or hosted agent calls.

Phase 4 adds local replay storage under `backend/.crisol_sessions/`. The folder is ignored and should not be committed.
