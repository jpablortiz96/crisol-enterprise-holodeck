from datetime import datetime, timezone
from typing import Any


def create_root_node(session_id: str, scenario: dict[str, Any]) -> dict[str, Any]:
    return {
        "node_id": "NODE-ROOT",
        "session_id": session_id,
        "parent_node_id": None,
        "turn_number": 0,
        "decision_id": None,
        "decision_label": None,
        "severity": int(scenario.get("initial_severity", 4)),
        "affected_systems": list(scenario.get("initial_affected_systems", scenario.get("impacted_systems", []))),
        "revenue_at_risk": float(scenario.get("initial_revenue_at_risk", 0.0)),
        "revenue_delta": 0.0,
        "world_delta": "Scenario initialized.",
        "branch_id": "BR-ROOT",
        "created_at": _utc_now(),
    }


def create_decision_node(
    session_id: str,
    parent_node_id: str,
    turn_number: int,
    decision: dict[str, Any],
    consequence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "node_id": f"NODE-{turn_number:03d}",
        "session_id": session_id,
        "parent_node_id": parent_node_id,
        "turn_number": turn_number,
        "decision_id": decision["id"],
        "decision_label": decision["label"],
        "severity": consequence["new_severity"],
        "affected_systems": consequence["affected_systems"],
        "revenue_at_risk": consequence["revenue_at_risk"],
        "revenue_delta": consequence["revenue_delta"],
        "world_delta": consequence["world_delta"],
        "branch_id": consequence["branch_id"],
        "created_at": _utc_now(),
    }


def build_timeline(nodes: list[dict[str, Any]]) -> dict[str, Any]:
    if not nodes:
        raise ValueError("Timeline requires at least one root node.")

    root_node = nodes[0]
    edges = [
        {
            "from": node["parent_node_id"],
            "to": node["node_id"],
            "label": node["decision_label"] or "Start",
        }
        for node in nodes
        if node.get("parent_node_id")
    ]
    timeline = {
        "session_id": root_node["session_id"],
        "root_node_id": root_node["node_id"],
        "nodes": nodes,
        "edges": edges,
    }
    timeline["summary"] = summarize_timeline(timeline)
    return timeline


def summarize_timeline(timeline: dict[str, Any]) -> dict[str, Any]:
    nodes = timeline["nodes"]
    return {
        "total_nodes": len(nodes),
        "max_severity": max(node["severity"] for node in nodes),
        "max_revenue_at_risk": max(node["revenue_at_risk"] for node in nodes),
        "final_severity": nodes[-1]["severity"],
        "final_revenue_at_risk": nodes[-1]["revenue_at_risk"],
    }


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
