# Agents

CRISOL is organized around five functional agents. Phase 3 implements deterministic local contracts for the terminal simulation loop.

## Director

The Director chooses the simulation context. It selects a learner role, scenario seed, systems under stress, stakes, active personas, available options, and turn continuation.

Current implementation: `app.agents.director.ScenarioDirector`

Key methods:

- `select_scenario(role_id, scenario_seed)`
- `start_session(role_id, scenario_seed)`
- `build_turn_context(state)`
- `should_continue(state)`

## NPC Ensemble

The NPC Ensemble represents synthetic participants defined by each scenario. When a scenario omits personas, the ensemble derives a deterministic generic roster from its role, industry, tags, and difficulty.

Current implementation: `app.agents.npcs.generate_npc_reactions`

Each reaction carries the scenario persona's role, communication style, pressure profile, voice style, and avatar style through orchestration and live streaming.

## Consequence Engine

The Consequence Engine reads the ontology graph to identify affected systems, branch nodes, severity movement, contract exposure, revenue-at-risk, and cascade paths.

Current implementation: `app.agents.consequence.evaluate_decision`

Phase 4 consequence fields:

- `branch_id`
- `severity_delta`
- `new_severity`
- `affected_systems`
- `newly_affected_systems`
- `recovered_systems`
- `cascade_paths`
- `contract_exposure`
- `revenue_at_risk`
- `revenue_delta`
- `world_delta`
- `citations`

Bad decisions expand active systems and exposure. Recovery decisions shrink active systems and reduce final severity.

## Examiner

The Examiner compares learner decisions with expected competencies. It now uses the reusable scoring rubric to produce a cited competence report.

Current implementation: `app.agents.examiner.score_session`

Phase 5 report fields:

- overall score and readiness band
- weighted dimensions
- cited evidence trail
- failure modes
- skill gaps
- synthetic certification alignment
- next best actions

## Coach

The Coach turns the Examiner output into a structured learning plan. It picks the highest-leverage gap from the competence report and returns concise practice steps, success criteria, a manager note, and citations.

Current implementation: `app.agents.coach.generate_coach_plan`

## Local Orchestration

`app.orchestration.turn_loop.run_simulation` runs the Director, Consequence Engine, NPC Ensemble, Examiner, and Coach in sequence. The loop is deterministic, uses synthetic data only, and includes citations from the local grounding layer where possible.

The current implementation does not call live hosted agents. The contracts are shaped so future phases can swap local functions for Microsoft Agent Framework or Foundry-hosted agents.

Phase 4 also builds a branching timeline during orchestration and saves the completed session for local replay.

Phase 5 adds manager-level aggregate insights over saved sessions without exposing individual learner identity.
