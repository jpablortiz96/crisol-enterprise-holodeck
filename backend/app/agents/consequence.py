from typing import Any

import networkx as nx

from app.grounding.local_knowledge import answer_with_citations
from app.ontology.graph import affected_systems, revenue_at_risk


ACTION_EFFECTS = {
    "restart_checkout": {
        "delta": 2,
        "query": "checkout outage split brain retry database recovery",
        "world_delta": "Restarting checkout before database ownership is clear amplifies retry traffic and expands the cascade.",
    },
    "freeze_db_writes": {
        "delta": -1,
        "query": "database recovery identify primary writer",
        "world_delta": "Write paths are frozen while the team identifies the primary database writer and protects consistency.",
    },
    "escalate_incident_command": {
        "delta": -1,
        "query": "incident escalation stakeholder communication",
        "world_delta": "Incident command is active, owners are named, and stakeholder communication improves.",
    },
    "correlate_observability": {
        "delta": -1,
        "query": "checkout observability traces orders database",
        "world_delta": "Telemetry correlation narrows the fault domain and reduces uncertainty.",
    },
    "gradual_restore": {
        "delta": -2,
        "query": "database recovery traffic restoration",
        "world_delta": "Traffic is restored gradually after consistency checks, reducing customer and contract exposure.",
    },
    "ignore_database_symptoms": {
        "delta": 2,
        "query": "split brain database recovery incident escalation",
        "world_delta": "Ignoring database symptoms allows inconsistent order state to persist.",
    },
    "failover_without_validation": {
        "delta": 1,
        "query": "database recovery failover replication health",
        "world_delta": "Failover without validation increases the chance of data inconsistency.",
    },
}


def evaluate_decision(graph: nx.DiGraph, state: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
    action_type = decision.get("action_type", "")
    effect = ACTION_EFFECTS.get(
        action_type,
        {
            "delta": 0,
            "query": "incident escalation communication",
            "world_delta": "The action keeps the incident moving but does not materially change risk.",
        },
    )
    turn_number = state["turn_index"] + 1
    severity_delta = effect["delta"]
    new_severity = max(1, min(5, state["severity"] + severity_delta))
    current_systems = list(state["impacted_systems"])
    affected = _affected_for_action(graph, action_type, current_systems)
    revenue = revenue_at_risk(graph, affected)
    grounding = answer_with_citations(effect["query"], top_k=3)
    branch_id = f"BR-{turn_number:02d}-{action_type.upper().replace('_', '-')}"

    graph.add_node(
        branch_id,
        node_type="Branch",
        decision_id=decision["id"],
        label=decision["label"],
        new_severity=new_severity,
    )
    for system_id in affected:
        graph.add_edge(branch_id, system_id, relationship="affects")

    return {
        "branch_id": branch_id,
        "severity_delta": severity_delta,
        "new_severity": new_severity,
        "affected_systems": affected,
        "revenue_at_risk": revenue,
        "world_delta": effect["world_delta"],
        "citations": grounding["citations"],
    }


def _affected_for_action(graph: nx.DiGraph, action_type: str, current_systems: list[str]) -> list[str]:
    if action_type in {"restart_checkout", "ignore_database_symptoms", "failover_without_validation"}:
        return affected_systems(graph, ["SVC-checkout"])

    if action_type == "freeze_db_writes":
        stabilized = set(current_systems) | {"SVC-checkout", "SVC-orders", "SVC-db", "SVC-payments"}
        return sorted(stabilized)

    if action_type == "escalate_incident_command":
        stabilized = set(current_systems) & {"SVC-checkout", "SVC-orders", "SVC-db", "SVC-payments", "SVC-identity"}
        return sorted(stabilized or {"SVC-checkout", "SVC-orders", "SVC-db"})

    if action_type == "correlate_observability":
        return ["SVC-checkout", "SVC-orders", "SVC-db", "SVC-observability"]

    if action_type == "gradual_restore":
        return ["SVC-checkout", "SVC-orders"]

    return sorted(set(current_systems))
