from copy import deepcopy
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Callable

from app.agents.coach import generate_coach_plan
from app.agents.consequence import evaluate_decision
from app.agents.director import AUTO_DECISION_PLAN, DISTRACTOR_OPTIONS, ScenarioDirector
from app.agents.examiner import score_session
from app.agents.npcs import generate_npc_reactions
from app.branching.timeline import build_timeline, create_decision_node, create_root_node
from app.insights.manager import build_fragility_map
from app.ontology.graph import load_ontology, revenue_at_risk
from app.replay.time_travel import branch_from_session
from app.scoring.competence_report import generate_competence_report
from app.storage.session_store import load_session, save_session
from app.telemetry.events import emit_event


_ACTIVE_SESSIONS: dict[str, dict[str, Any]] = {}
_SESSION_LOCK = RLock()


def start_simulacrum(
    role: str = "ROLE-SRE",
    difficulty: str = "standard",
    scenario_seed: str | None = None,
) -> dict[str, Any]:
    _emit_tool_called("start_simulacrum")
    graph = load_ontology()
    director = ScenarioDirector()
    state = director.start_session(role, scenario_seed)
    state["session_id"] = f"{state['session_id']}-{_session_timestamp()}"
    state["difficulty"] = difficulty
    state["revenue_at_risk"] = revenue_at_risk(graph, state["impacted_systems"])
    state["current_branch_id"] = "BR-ROOT"
    state["cascade_roots"] = list(state["impacted_systems"][:1])
    root_scenario = {
        **state["scenario"],
        "initial_severity": state["severity"],
        "initial_affected_systems": state["impacted_systems"],
        "initial_revenue_at_risk": state["revenue_at_risk"],
    }
    entry = {
        "graph": graph,
        "director": director,
        "state": state,
        "turns": [],
        "timeline_nodes": [create_root_node(state["session_id"], root_scenario)],
        "completed_session": None,
    }
    with _SESSION_LOCK:
        _ACTIVE_SESSIONS[state["session_id"]] = entry

    situation = director.build_turn_context(state)
    return {
        "session_id": state["session_id"],
        "scenario": state["scenario"],
        "difficulty": difficulty,
        "current_situation": situation["situation"],
        "available_options": situation["available_options"],
        "citations": situation["citations"],
    }


def get_situation(session_id: str) -> dict[str, Any]:
    _emit_tool_called("get_situation", session_id)
    with _SESSION_LOCK:
        entry = _ACTIVE_SESSIONS.get(session_id)
        if entry is not None:
            state = entry["state"]
            if entry["director"].should_continue(state):
                context = entry["director"].build_turn_context(state)
                return {
                    "session_id": session_id,
                    "current_turn": context["turn_number"],
                    "situation": context["situation"],
                    "stakes": {
                        "severity": context["severity"],
                        "affected_systems": context["affected_systems"],
                    },
                    "revenue_at_risk": state["revenue_at_risk"],
                    "available_options": context["available_options"],
                    "citations": context["citations"],
                }
            completed = entry["completed_session"] or _snapshot_session(entry)
            return _completed_situation(completed)

    return _completed_situation(load_session(session_id))


def make_decision(session_id: str, action: str) -> dict[str, Any]:
    _emit_tool_called("make_decision", session_id)
    with _SESSION_LOCK:
        entry = _ACTIVE_SESSIONS.get(session_id)
        if entry is None:
            raise ValueError(f"Active simulacrum not found: {session_id}")
        state = entry["state"]
        director: ScenarioDirector = entry["director"]
        if not director.should_continue(state):
            raise ValueError(f"Simulacrum is already complete: {session_id}")

        turn_context = director.build_turn_context(state)
        decision = _resolve_decision(action, turn_context["available_options"])
        consequence = evaluate_decision(entry["graph"], state, decision)
        parent_node_id = entry["timeline_nodes"][-1]["node_id"]
        decision_node = create_decision_node(
            session_id,
            parent_node_id,
            turn_context["turn_number"],
            decision,
            consequence,
        )
        entry["timeline_nodes"].append(decision_node)
        npc_reactions = generate_npc_reactions(turn_context, decision, consequence)
        turn_record = {
            "turn_number": turn_context["turn_number"],
            "situation": turn_context["situation"],
            "decision": decision,
            "npc_reactions": npc_reactions,
            "consequence": consequence,
            "citations": _unique_citations(
                [*turn_context["citations"], *consequence["citations"]]
            ),
        }
        entry["turns"].append(turn_record)
        state["history"].append(turn_record)
        state["turn_index"] += 1
        state["severity"] = consequence["new_severity"]
        state["impacted_systems"] = consequence["affected_systems"]
        state["revenue_at_risk"] = consequence["revenue_at_risk"]
        state["current_branch_id"] = consequence["branch_id"]

        timeline = build_timeline(entry["timeline_nodes"])
        if not director.should_continue(state):
            entry["completed_session"] = _complete_session(entry)

        return {
            "session_id": session_id,
            "decision": decision,
            "world_delta": consequence["world_delta"],
            "consequence": consequence,
            "npc_reactions": npc_reactions,
            "timeline": timeline,
            "citations": turn_record["citations"],
        }


def branch_from(
    session_id: str,
    decision_node_id: str,
    alternative_action: str,
) -> dict[str, Any]:
    _emit_tool_called("branch_from", session_id)
    return branch_from_session(session_id, decision_node_id, alternative_action)


def get_competence_report(session_id: str) -> dict[str, Any]:
    _emit_tool_called("get_competence_report", session_id)
    with _SESSION_LOCK:
        entry = _ACTIVE_SESSIONS.get(session_id)
        if entry is not None:
            session = entry["completed_session"] or _snapshot_session(entry)
        else:
            session = load_session(session_id)
    return {"report": generate_competence_report(session)}


def get_manager_fragility_map() -> dict[str, Any]:
    _emit_tool_called("get_manager_fragility_map")
    return {"fragility_map": build_fragility_map()}


TOOL_DEFINITIONS = [
    {
        "name": "start_simulacrum",
        "description": "Start a sanitized CRISOL role-readiness incident simulacrum.",
        "input_schema": {
            "role": "string",
            "difficulty": "string",
            "scenario_seed": "string|null",
        },
    },
    {
        "name": "get_situation",
        "description": "Get the current situation, stakes, options, and citations for a simulacrum.",
        "input_schema": {"session_id": "string"},
    },
    {
        "name": "make_decision",
        "description": "Apply one learner decision and return deterministic consequences and NPC reactions.",
        "input_schema": {"session_id": "string", "action": "string"},
    },
    {
        "name": "branch_from",
        "description": "Create a deterministic replay projection from a saved decision node.",
        "input_schema": {
            "session_id": "string",
            "decision_node_id": "string",
            "alternative_action": "string",
        },
    },
    {
        "name": "get_competence_report",
        "description": "Generate a cited competence report for a sanitized training session.",
        "input_schema": {"session_id": "string"},
    },
    {
        "name": "get_manager_fragility_map",
        "description": "Return the aggregate no-PII manager fragility map.",
        "input_schema": {},
    },
]


TOOL_FUNCTIONS: dict[str, Callable[..., dict[str, Any]]] = {
    "start_simulacrum": start_simulacrum,
    "get_situation": get_situation,
    "make_decision": make_decision,
    "branch_from": branch_from,
    "get_competence_report": get_competence_report,
    "get_manager_fragility_map": get_manager_fragility_map,
}


def list_registered_tools() -> list[dict[str, Any]]:
    return deepcopy(TOOL_DEFINITIONS)


def call_registered_tool(name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    function = TOOL_FUNCTIONS.get(name)
    if function is None:
        raise ValueError(f"Unknown CRISOL tool: {name}")
    return function(**(arguments or {}))


def run_local_demo() -> dict[str, Any]:
    started = start_simulacrum()
    session_id = started["session_id"]
    situation = get_situation(session_id)
    decision = make_decision(session_id, "Freeze writes and identify primary database writer")
    report = get_competence_report(session_id)["report"]
    return {
        "tools": [tool["name"] for tool in list_registered_tools()],
        "started": {
            "session_id": session_id,
            "scenario_id": started["scenario"]["id"],
            "current_situation": started["current_situation"],
        },
        "situation": {
            "current_turn": situation["current_turn"],
            "revenue_at_risk": situation["revenue_at_risk"],
            "citation_count": len(situation["citations"]),
        },
        "decision": {
            "decision": decision["decision"]["label"],
            "new_severity": decision["consequence"]["new_severity"],
            "world_delta": decision["world_delta"],
        },
        "competence_report": {
            "session_id": report["session_id"],
            "overall_score": report["overall_score"],
            "readiness_band": report["readiness_band"],
            "evidence_count": len(report["evidence_trail"]),
        },
    }


def _complete_session(entry: dict[str, Any]) -> dict[str, Any]:
    session = _snapshot_session(entry)
    final_score = score_session(session)
    completed = {
        **session,
        "final_score": final_score,
        "coach_plan": generate_coach_plan(final_score, session),
        "saved_at": _utc_now(),
    }
    save_session(completed)
    return completed


def _snapshot_session(entry: dict[str, Any]) -> dict[str, Any]:
    state = entry["state"]
    return {
        "session_id": state["session_id"],
        "scenario": deepcopy(state["scenario"]),
        "turns": deepcopy(entry["turns"]),
        "timeline": build_timeline(deepcopy(entry["timeline_nodes"])),
    }


def _completed_situation(session: dict[str, Any]) -> dict[str, Any]:
    last_turn = session.get("turns", [])[-1] if session.get("turns") else None
    summary = session["timeline"]["summary"]
    return {
        "session_id": session["session_id"],
        "current_turn": len(session.get("turns", [])),
        "situation": (
            last_turn["consequence"]["world_delta"]
            if last_turn
            else "The saved simulacrum has no completed decisions."
        ),
        "stakes": {
            "severity": summary["final_severity"],
            "affected_systems": (
                last_turn["consequence"]["affected_systems"] if last_turn else []
            ),
        },
        "revenue_at_risk": summary["final_revenue_at_risk"],
        "available_options": [],
        "citations": last_turn.get("citations", []) if last_turn else [],
    }


def _resolve_decision(action: str, available_options: list[dict[str, Any]]) -> dict[str, Any]:
    normalized = " ".join(action.lower().split())
    decisions = [*available_options, *AUTO_DECISION_PLAN, *DISTRACTOR_OPTIONS]
    unique_decisions = {decision["id"]: decision for decision in decisions}.values()
    for decision in unique_decisions:
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
    all_decisions = [*AUTO_DECISION_PLAN, *DISTRACTOR_OPTIONS]
    for keywords, action_type in keyword_actions:
        if any(keyword in normalized for keyword in keywords):
            return deepcopy(
                next(item for item in all_decisions if item["action_type"] == action_type)
            )
    return {
        "id": "DEC-CUSTOM",
        "label": action.strip() or "Custom incident action",
        "description": "Synthetic custom action supplied through the CRISOL tool interface.",
        "competencies": ["SK-incident-triage"],
        "action_type": "custom_incident_action",
    }


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


def _emit_tool_called(tool_name: str, session_id: str | None = None) -> None:
    emit_event(
        "mcp_tool_called",
        {
            "tool_name": tool_name,
            "session_id": session_id,
            "status": "called",
        },
    )
