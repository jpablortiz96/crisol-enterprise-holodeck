from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from app.agents.coach import generate_coach_plan
from app.agents.consequence import evaluate_decision
from app.agents.director import AUTO_DECISION_PLAN, DISTRACTOR_OPTIONS, ScenarioDirector
from app.agents.examiner import score_session
from app.agents.npcs import generate_npc_reactions
from app.branching.timeline import build_timeline, create_decision_node
from app.ontology.graph import load_ontology
from app.scoring.competence_report import generate_competence_report
from app.storage.session_store import load_session, save_session


def branch_from_session(
    session_id: str,
    decision_node_id: str,
    alternative_action: str,
) -> dict[str, Any]:
    original_session = load_session(session_id)
    target_node = _find_decision_node(original_session, decision_node_id)
    target_turn = int(target_node["turn_number"])
    new_session_id = f"{session_id}-BRANCH-{_session_timestamp()}"

    preserved_turns = [
        deepcopy(turn)
        for turn in original_session.get("turns", [])
        if int(turn["turn_number"]) < target_turn
    ]
    preserved_nodes = [
        {**deepcopy(node), "session_id": new_session_id}
        for node in original_session["timeline"]["nodes"]
        if int(node["turn_number"]) < target_turn
    ]
    if not preserved_nodes:
        raise ValueError("Replay branch requires the source timeline root node.")

    graph = load_ontology()
    director = ScenarioDirector()
    state = director.start_session(
        original_session["scenario"]["role_id"],
        original_session["scenario"]["id"],
    )
    root_node = preserved_nodes[0]
    state.update(
        {
            "session_id": new_session_id,
            "severity": root_node["severity"],
            "impacted_systems": list(root_node["affected_systems"]),
            "revenue_at_risk": float(root_node["revenue_at_risk"]),
            "current_branch_id": root_node["branch_id"],
            "cascade_roots": ["SVC-checkout"],
            "history": [],
            "turn_index": 0,
        }
    )
    for turn in preserved_turns:
        _advance_state(state, turn)

    turns = preserved_turns
    timeline_nodes = preserved_nodes
    parent_node_id = timeline_nodes[-1]["node_id"]
    alternative_decision = _resolve_alternative_decision(alternative_action)
    original_decisions = {
        int(turn["turn_number"]): deepcopy(turn["decision"])
        for turn in original_session.get("turns", [])
    }

    while director.should_continue(state):
        turn_context = director.build_turn_context(state)
        turn_number = int(turn_context["turn_number"])
        decision = (
            alternative_decision
            if turn_number == target_turn
            else original_decisions.get(turn_number, deepcopy(turn_context["auto_decision"]))
        )
        consequence = evaluate_decision(graph, state, decision)
        decision_node = create_decision_node(
            new_session_id,
            parent_node_id,
            turn_number,
            decision,
            consequence,
        )
        timeline_nodes.append(decision_node)
        parent_node_id = decision_node["node_id"]
        npc_reactions = generate_npc_reactions(turn_context, decision, consequence)
        turn_record = {
            "turn_number": turn_number,
            "situation": turn_context["situation"],
            "decision": decision,
            "npc_reactions": npc_reactions,
            "consequence": consequence,
            "citations": _unique_citations(
                [*turn_context["citations"], *consequence["citations"]]
            ),
        }
        turns.append(turn_record)
        _advance_state(state, turn_record)

    projected_session = {
        "session_id": new_session_id,
        "scenario": deepcopy(original_session["scenario"]),
        "turns": turns,
        "timeline": build_timeline(timeline_nodes),
        "replay_projection": {
            "source_session_id": session_id,
            "branched_from_node_id": decision_node_id,
            "projection_type": "deterministic replay projection",
            "boundary": "This is not an exact production rollback.",
        },
    }
    final_score = score_session(projected_session)
    projected_session["final_score"] = final_score
    projected_session["coach_plan"] = generate_coach_plan(final_score, projected_session)
    projected_session["saved_at"] = _utc_now()
    save_session(projected_session)

    comparison = compare_branches(original_session, projected_session)
    citations = _unique_citations(
        [
            *original_session.get("scenario", {}).get("citations", []),
            *[
                citation
                for turn in projected_session["turns"][target_turn - 1 :]
                for citation in turn.get("citations", [])
            ],
        ]
    )
    return {
        "source_session_id": session_id,
        "new_session_id": new_session_id,
        "branched_from_node_id": decision_node_id,
        "alternative_decision": alternative_decision,
        "original_path_summary": _path_summary(original_session),
        "alternative_path_summary": _path_summary(projected_session),
        "timeline": projected_session["timeline"],
        "comparison": comparison,
        "citations": citations,
    }


def compare_branches(
    original_session: dict[str, Any],
    branched_session: dict[str, Any],
) -> dict[str, Any]:
    original_timeline = original_session["timeline"]["summary"]
    alternative_timeline = branched_session["timeline"]["summary"]
    original_score = _score_value(original_session)
    alternative_score = _score_value(branched_session)
    score_delta = round(alternative_score - original_score, 1)
    severity_delta = (
        alternative_timeline["final_severity"] - original_timeline["final_severity"]
    )
    revenue_delta = round(
        alternative_timeline["max_revenue_at_risk"]
        - original_timeline["max_revenue_at_risk"],
        2,
    )
    return {
        "original_final_score": original_score,
        "alternative_projected_score": alternative_score,
        "score_delta": score_delta,
        "original_max_revenue_at_risk": original_timeline["max_revenue_at_risk"],
        "alternative_revenue_at_risk": alternative_timeline["max_revenue_at_risk"],
        "alternative_max_revenue_at_risk": alternative_timeline["max_revenue_at_risk"],
        "revenue_at_risk_delta": revenue_delta,
        "original_final_severity": original_timeline["final_severity"],
        "alternative_final_severity": alternative_timeline["final_severity"],
        "severity_delta": severity_delta,
        "reasoning_summary": (
            "This deterministic replay projection replaces one decision and re-simulates "
            f"the remaining synthetic path. Score delta: {score_delta:+.1f}; final severity "
            f"delta: {severity_delta:+d}; max revenue-at-risk delta: {revenue_delta:+.2f}. "
            "It is not an exact production rollback."
        ),
    }


def _find_decision_node(session: dict[str, Any], node_id: str) -> dict[str, Any]:
    node = next(
        (item for item in session.get("timeline", {}).get("nodes", []) if item["node_id"] == node_id),
        None,
    )
    if node is None:
        raise ValueError(f"Timeline node not found: {node_id}")
    if int(node.get("turn_number", 0)) < 1 or not node.get("decision_id"):
        raise ValueError("Replay must branch from a decision node, not the timeline root.")
    return node


def _resolve_alternative_decision(action: str) -> dict[str, Any]:
    normalized = " ".join(action.lower().split())
    decisions = [*AUTO_DECISION_PLAN, *DISTRACTOR_OPTIONS]
    for decision in decisions:
        if normalized in {
            decision["id"].lower(),
            decision["label"].lower(),
            decision["action_type"].lower(),
        }:
            return deepcopy(decision)

    keyword_actions = (
        (("fail over", "failover"), "failover_without_validation"),
        (("freeze", "writer"), "freeze_db_writes"),
        (("restart",), "restart_checkout"),
        (("escalate", "incident command"), "escalate_incident_command"),
        (("correlate", "trace", "observability"), "correlate_observability"),
        (("restore", "reopen"), "gradual_restore"),
        (("ignore",), "ignore_database_symptoms"),
    )
    for keywords, action_type in keyword_actions:
        if any(keyword in normalized for keyword in keywords):
            return deepcopy(next(item for item in decisions if item["action_type"] == action_type))

    return {
        "id": "DEC-ALTERNATIVE-CUSTOM",
        "label": action.strip() or "Custom replay action",
        "description": "Synthetic custom action supplied for deterministic replay projection.",
        "competencies": ["SK-incident-triage"],
        "action_type": "custom_replay_action",
    }


def _advance_state(state: dict[str, Any], turn: dict[str, Any]) -> None:
    consequence = turn["consequence"]
    state["history"].append(turn)
    state["turn_index"] += 1
    state["severity"] = consequence["new_severity"]
    state["impacted_systems"] = list(consequence["affected_systems"])
    state["revenue_at_risk"] = consequence["revenue_at_risk"]
    state["current_branch_id"] = consequence["branch_id"]


def _path_summary(session: dict[str, Any]) -> dict[str, Any]:
    timeline = session["timeline"]["summary"]
    return {
        "session_id": session["session_id"],
        "decisions": [
            {
                "turn_number": turn["turn_number"],
                "decision_id": turn["decision"]["id"],
                "decision_label": turn["decision"]["label"],
            }
            for turn in session.get("turns", [])
        ],
        "final_score": _score_value(session),
        "max_severity": timeline["max_severity"],
        "final_severity": timeline["final_severity"],
        "max_revenue_at_risk": timeline["max_revenue_at_risk"],
        "final_revenue_at_risk": timeline["final_revenue_at_risk"],
    }


def _score_value(session: dict[str, Any]) -> float:
    score = session.get("final_score") or generate_competence_report(session)
    return round(float(score.get("overall_score", score.get("score", 0.0))), 1)


def _unique_citations(citations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique = []
    seen = set()
    for citation in citations:
        key = (citation.get("doc_id"), citation.get("chunk_id"))
        if key in seen:
            continue
        seen.add(key)
        unique.append(citation)
    return unique[:12]


def _session_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
