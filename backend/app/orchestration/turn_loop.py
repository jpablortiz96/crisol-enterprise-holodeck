from typing import Any

from app.agents.coach import generate_coach_plan
from app.agents.consequence import evaluate_decision
from app.agents.director import ScenarioDirector
from app.agents.examiner import score_session
from app.agents.npcs import generate_npc_reactions
from app.ontology.graph import load_ontology


def run_simulation(
    role_id: str = "ROLE-SRE",
    scenario_seed: str | None = None,
    auto_mode: bool = True,
) -> dict[str, Any]:
    graph = load_ontology()
    director = ScenarioDirector()
    state = director.start_session(role_id, scenario_seed)
    turns = []

    while director.should_continue(state):
        turn_context = director.build_turn_context(state)
        decision = _select_decision(turn_context, auto_mode)
        consequence = evaluate_decision(graph, state, decision)
        npc_reactions = generate_npc_reactions(turn_context, decision, consequence)
        turn_record = {
            "turn_number": turn_context["turn_number"],
            "situation": turn_context["situation"],
            "decision": decision,
            "npc_reactions": npc_reactions,
            "consequence": consequence,
            "citations": [*turn_context["citations"], *consequence["citations"]],
        }
        turns.append(turn_record)
        state["history"].append(turn_record)
        state["turn_index"] += 1
        state["severity"] = consequence["new_severity"]
        state["impacted_systems"] = consequence["affected_systems"]

    session = {
        "session_id": state["session_id"],
        "scenario": state["scenario"],
        "turns": turns,
    }
    final_score = score_session(session)
    coach_plan = generate_coach_plan(final_score, session)

    return {
        **session,
        "final_score": final_score,
        "coach_plan": coach_plan,
    }


def _select_decision(turn_context: dict[str, Any], auto_mode: bool) -> dict[str, Any]:
    if auto_mode:
        return turn_context["auto_decision"]
    return turn_context["available_options"][0]
