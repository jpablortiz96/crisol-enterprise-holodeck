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
10. `app.scoring.competence_report` converts sessions into cited readiness reports.
11. `app.insights.manager` aggregates saved sessions into a no-PII fragility map.
12. `app.grounding.learn_mcp` connects to Microsoft Learn MCP when available and returns a bounded synthetic fallback otherwise.
13. `app.replay.time_travel` creates deterministic replay projections from saved decision nodes.
14. `app.mcp_server` exposes six CRISOL capabilities through a local registry and `FastMCP`.
15. FastAPI endpoints expose health, graph summary, revenue-at-risk, grounding tests, scenario run, live scenario stream, saved sessions, replay, MCP tools, reports, and manager summaries.
16. The Next.js War-Room consumes the one-shot scenario endpoint, live SSE stream, replay endpoint, and MCP demo endpoint.
17. `app.scenarios` validates, imports, selects, and normalizes manual scenario packs.
18. `app.telemetry` records allowlisted local lifecycle events and optionally initializes OpenTelemetry.
19. `app.eval` verifies groundedness, citation integrity, scenario safety, tools, replay, voice fallback, and product language.
20. Future phases will add live indexing, hosted agents, and live ontology sources.

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

## MCP And Replay Layer

Phase 8 adds two reusable platform interfaces:

```text
MCP client or War-Room
        |
        +--> CRISOL MCP registry / FastMCP
        |        |
        |        +--> Director + Consequence Engine
        |        +--> Competence Report
        |        +--> Manager Fragility Map
        |        +--> Replay Projection
        |
        +--> FastAPI replay and MCP endpoints
                 |
                 +--> Saved synthetic sessions
                 +--> Microsoft Learn MCP adapter
                 +--> Synthetic local knowledge fallback
```

The MCP registry and HTTP endpoints call the same underlying services. The replay layer copies the pre-branch timeline, replaces the selected decision, simulates the remaining path deterministically, and saves a new session. It is a deterministic replay projection, not an exact production rollback.

The Learn adapter uses streamable HTTP with a bounded timeout. Live results are marked `learn-mcp`. Unavailable live grounding is marked `local-fallback`, and all fallback content is explicitly synthetic rather than official certification documentation.

## Scenario And Assurance Layer

Phase 9 adds a manual product scenario boundary:

```text
Scenario pack JSON
      |
      +--> structure validator
      +--> sensitive-content validator
      +--> runtime seed adapter
                 |
                 +--> Director
                 +--> Consequence Engine
                 +--> Streaming and replay

Runtime lifecycle
      |
      +--> allowlisted local telemetry
      +--> optional OpenTelemetry adapter
      +--> evaluation harness
```

The Scenario Library uses the same scoring, citation, MCP, replay, voice, and timeline contracts as internal seeds. Scenario imports do not execute production actions.

## Manager Insights

Phase 5 adds an aggregate readiness view over saved synthetic sessions:

- average readiness score
- readiness band distribution
- highest-risk dimension and skill
- role-level risk
- skill fragility
- synthetic certification readiness alignment

The manager output does not include employee names, emails, learner identity, or PII.

## SSE Event Stream

Phase 7 adds `GET /scenario/stream?role_id=ROLE-SRE` for live War-Room playback:

1. The backend runs the deterministic simulation and saves the session normally.
2. `app.streaming.sse.build_stream_events` converts the session into ordered event envelopes.
3. FastAPI returns a `text/event-stream` response through `StreamingResponse`.
4. The frontend opens an `EventSource` connection from `Play Live Simulation`.
5. The event rail appends every envelope with its session ID and sequence.
6. Turn events build the scenario feed progressively.
7. `consequence_delta` updates severity and revenue metrics.
8. `timeline_updated` refreshes the ReactFlow decision graph.
9. `score_final`, `coach_plan`, and `manager_snapshot` hydrate the final assessment panels.
10. `session_completed` closes the stream and leaves the completed session visible.

The event order is:

- `session_started`
- `scenario_intro`
- `turn_started`
- `decision_selected`
- `npc_reaction`
- `consequence_delta`
- `timeline_updated`
- `score_final`
- `coach_plan`
- `manager_snapshot`
- `session_completed`

## Azure Speech Voice Layer

Phase 7.2 makes Azure Speech the primary voice layer for streamed NPC reactions:

1. `app.voice.speech` selects a configurable neural voice for each persona.
2. The backend truncates synthesis input to a safe length and sanitizes all generated path segments.
3. Azure Speech writes MP3 output under `backend/.crisol_audio/<session_id>/`.
4. The cache key includes session, event, persona, and line content so repeated playback reuses the same file.
5. FastAPI serves generated files through the `/audio` static mount.
6. Each `npc_reaction` event includes a `voice` result with provider, voice name, format, and audio URL.
7. The frontend queues audio URLs through `HTMLAudioElement` to prevent overlapping NPC speech.
8. The Voice toggle can stop and clear playback without interrupting the event stream.

The Speech key remains backend-only. If configuration is missing, the provider is `text-only`. If Azure synthesis fails, the provider is `azure-speech-fallback`. Both paths preserve the text reaction and allow the simulation to complete.

## Phase Boundaries

Phase 1 does not connect to live Azure services, production telemetry, or real employee data. All data is synthetic and local.

Phase 2 adds local cited retrieval and an adapter skeleton. Live Foundry IQ indexing and retrieval remain configuration-driven future work.

Phase 3 adds local deterministic agent orchestration. It does not require live Azure credentials or hosted agent calls.

Phase 4 adds local replay storage under `backend/.crisol_sessions/`. The folder is ignored and should not be committed.

Phase 5 adds product-grade reporting over synthetic saved sessions. Certification alignment is a synthetic readiness signal only, not official certification status.

Phase 6 adds the local War-Room frontend.

Phase 7 adds SSE playback and optional speech fallback.

Phase 7.2 adds Azure Speech synthesis and local MP3 caching. Azure credentials remain optional because text fallback is always available.

Phase 8 adds local MCP tools, optional live Microsoft Learn MCP grounding, and deterministic replay projections. It does not claim production checkpoint restoration or official certification status.

Phase 9 adds sanitized scenario authoring, local assurance telemetry, evaluation checks, and deployment artifacts. Product UI explicitly states that the platform is a training environment with no production changes.
