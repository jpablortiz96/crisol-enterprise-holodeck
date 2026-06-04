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

The NPC Ensemble represents synthetic participants in the scenario. Phase 3 includes VP Operations, Product Manager, Database Lead, and Support Lead personas.

Current implementation: `app.agents.npcs.generate_npc_reactions`

## Consequence Engine

The Consequence Engine reads the ontology graph to identify affected systems, branch nodes, severity movement, contract exposure, and revenue-at-risk.

Current implementation: `app.agents.consequence.evaluate_decision`

## Examiner

The Examiner compares learner decisions with expected competencies. It scores triage, technical correctness, communication, escalation judgment, and data-layer recovery.

Current implementation: `app.agents.examiner.score_session`

## Coach

The Coach turns the Examiner output into a learning plan. It identifies the highest-leverage skill gap and returns a concise practice plan.

Current implementation: `app.agents.coach.generate_coach_plan`

## Local Orchestration

`app.orchestration.turn_loop.run_simulation` runs the Director, Consequence Engine, NPC Ensemble, Examiner, and Coach in sequence. The loop is deterministic, uses synthetic data only, and includes citations from the local grounding layer where possible.

The current implementation does not call live hosted agents. The contracts are shaped so future phases can swap local functions for Microsoft Agent Framework or Foundry-hosted agents.
