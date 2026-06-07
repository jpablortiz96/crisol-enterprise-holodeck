from datetime import datetime, timezone
from typing import Any

from app.agents.coach import generate_coach_plan
from app.agents.consequence import evaluate_decision
from app.agents.director import ScenarioDirector
from app.agents.examiner import score_session
from app.agents.npcs import generate_npc_reactions
from app.branching.timeline import build_timeline, create_decision_node, create_root_node
from app.ontology.graph import load_ontology
from app.ontology.graph import revenue_at_risk
from app.storage.session_store import save_session
from app.telemetry.events import emit_event


def run_simulation(
    role_id: str = "ROLE-SRE",
    scenario_seed: str | None = None,
    auto_mode: bool = True,
) -> dict[str, Any]:
    graph = load_ontology()
    director = ScenarioDirector()
    state = director.start_session(role_id, scenario_seed)
    state["session_id"] = f"{state['session_id']}-{_session_timestamp()}"
    state["revenue_at_risk"] = revenue_at_risk(graph, state["impacted_systems"])
    state["current_branch_id"] = "BR-ROOT"
    state["cascade_roots"] = list(state["impacted_systems"][:1])
    emit_event(
        "scenario_started",
        {
            "session_id": state["session_id"],
            "scenario_id": state["scenario"]["id"],
            "role_id": role_id,
            "status": "started",
        },
    )
    root_scenario = {
        **state["scenario"],
        "initial_severity": state["severity"],
        "initial_affected_systems": state["impacted_systems"],
        "initial_revenue_at_risk": state["revenue_at_risk"],
    }
    timeline_nodes = [create_root_node(state["session_id"], root_scenario)]
    parent_node_id = timeline_nodes[0]["node_id"]
    turns = []

    while director.should_continue(state):
        turn_context = director.build_turn_context(state)
        decision = _select_decision(turn_context, auto_mode)
        consequence = evaluate_decision(graph, state, decision)
        decision_node = create_decision_node(
            state["session_id"],
            parent_node_id,
            turn_context["turn_number"],
            decision,
            consequence,
        )
        timeline_nodes.append(decision_node)
        parent_node_id = decision_node["node_id"]
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
        emit_event(
            "consequence_evaluated",
            {
                "session_id": state["session_id"],
                "scenario_id": state["scenario"]["id"],
                "role_id": role_id,
                "turn_number": turn_context["turn_number"],
                "severity": consequence["new_severity"],
                "severity_delta": consequence["severity_delta"],
                "revenue_at_risk": consequence["revenue_at_risk"],
                "revenue_delta": consequence["revenue_delta"],
                "citation_count": len(turn_record["citations"]),
            },
        )
        emit_event(
            "turn_processed",
            {
                "session_id": state["session_id"],
                "scenario_id": state["scenario"]["id"],
                "role_id": role_id,
                "turn_number": turn_context["turn_number"],
                "status": "completed",
            },
        )
        state["history"].append(turn_record)
        state["turn_index"] += 1
        state["severity"] = consequence["new_severity"]
        state["impacted_systems"] = consequence["affected_systems"]
        state["revenue_at_risk"] = consequence["revenue_at_risk"]
        state["current_branch_id"] = consequence["branch_id"]

    session = {
        "session_id": state["session_id"],
        "scenario": state["scenario"],
        "turns": turns,
        "timeline": build_timeline(timeline_nodes),
    }
    final_score = score_session(session)
    emit_event(
        "score_generated",
        {
            "session_id": state["session_id"],
            "scenario_id": state["scenario"]["id"],
            "role_id": role_id,
            "score": final_score["score"],
            "readiness_band": final_score["readiness_band"],
            "citation_count": len(final_score["citations"]),
        },
    )
    coach_plan = generate_coach_plan(final_score, session)

    completed_session = {
        **session,
        "final_score": final_score,
        "coach_plan": coach_plan,
        "saved_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    save_session(completed_session)
    return completed_session


def _select_decision(turn_context: dict[str, Any], auto_mode: bool) -> dict[str, Any]:
    if auto_mode:
        return turn_context["auto_decision"]
    return turn_context["available_options"][0]


def _session_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
