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
    effect = ACTION_EFFECTS.get(action_type) or _scenario_effect(state, decision)
    turn_number = state["turn_index"] + 1
    severity_delta = effect["delta"]
    new_severity = max(1, min(5, state["severity"] + severity_delta))
    current_systems = list(state["impacted_systems"])
    affected = _affected_for_action(graph, state, decision, current_systems)
    previous_revenue = float(state.get("revenue_at_risk", revenue_at_risk(graph, current_systems)))
    exposure = _contract_exposure(graph, affected)
    revenue = round(sum(item["exposure"] for item in exposure), 2)
    revenue_delta = round(revenue - previous_revenue, 2)
    newly_affected = sorted(set(affected) - set(current_systems))
    recovered = sorted(set(current_systems) - set(affected))
    cascade_paths = _cascade_paths(graph, state, affected)
    grounding = answer_with_citations(effect["query"], top_k=3)
    branch_id = f"BR-{turn_number:02d}-{action_type.upper().replace('_', '-')}"
    parent_branch_id = state.get("current_branch_id", "BR-ROOT")

    graph.add_node(
        branch_id,
        node_type="Branch",
        parent_branch_id=parent_branch_id,
        decision_id=decision["id"],
        label=decision["label"],
        new_severity=new_severity,
        revenue_at_risk=revenue,
    )
    if parent_branch_id in graph:
        graph.add_edge(parent_branch_id, branch_id, relationship="branches_to")
    for system_id in affected:
        graph.add_edge(branch_id, system_id, relationship="affects")

    return {
        "branch_id": branch_id,
        "severity_delta": severity_delta,
        "new_severity": new_severity,
        "affected_systems": affected,
        "newly_affected_systems": newly_affected,
        "recovered_systems": recovered,
        "cascade_paths": cascade_paths,
        "contract_exposure": exposure,
        "revenue_at_risk": revenue,
        "revenue_delta": revenue_delta,
        "world_delta": effect["world_delta"],
        "citations": grounding["citations"],
    }


def _affected_for_action(
    graph: nx.DiGraph,
    state: dict[str, Any],
    decision: dict[str, Any],
    current_systems: list[str],
) -> list[str]:
    action_type = decision.get("action_type", "")
    scenario = state.get("scenario", {})
    if scenario.get("source") == "scenario-library" and scenario.get("id") != "SCN-SRE-001":
        return _affected_for_scenario_action(
            graph,
            current_systems,
            decision.get("risk_effect", "neutral"),
        )

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


def _affected_for_scenario_action(
    graph: nx.DiGraph,
    current_systems: list[str],
    risk_effect: str,
) -> list[str]:
    if risk_effect == "increase":
        expanded = set(current_systems)
        for system_id in current_systems:
            if system_id in graph:
                expanded.update(affected_systems(graph, [system_id]))
        return sorted(expanded)
    if risk_effect == "decrease" and len(current_systems) > 1:
        return sorted(current_systems[:-1])
    return sorted(set(current_systems))


def _scenario_effect(state: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
    risk_effect = decision.get("risk_effect", "neutral")
    delta = {"increase": 1, "decrease": -1, "neutral": 0}.get(risk_effect, 0)
    scenario = state.get("scenario", {})
    query = " ".join(
        [
            decision.get("label", ""),
            *scenario.get("knowledge_refs", []),
            *scenario.get("tags", []),
        ]
    )
    return {
        "delta": delta,
        "query": query or "incident escalation communication",
        "world_delta": decision.get(
            "expected_outcome",
            "The action advances the scenario without changing the modeled risk.",
        ),
    }


def _contract_exposure(graph: nx.DiGraph, affected_system_ids: list[str]) -> list[dict[str, Any]]:
    affected = set(affected_system_ids)
    exposure = []

    for contract_id, attributes in graph.nodes(data=True):
        if attributes.get("node_type") != "Contract":
            continue

        contract_systems = {
            target
            for _, target, edge_attributes in graph.out_edges(contract_id, data=True)
            if edge_attributes.get("relationship") == "depends_on"
        }
        impacted_systems = sorted(contract_systems & affected)
        if impacted_systems:
            revenue = float(attributes.get("revenue_per_hour", 0.0))
            exposure.append(
                {
                    "contract_id": contract_id,
                    "criticality": attributes.get("criticality", "unknown"),
                    "systems": impacted_systems,
                    "revenue_per_hour": revenue,
                    "exposure": revenue,
                }
            )

    return sorted(exposure, key=lambda item: item["contract_id"])


def _cascade_paths(graph: nx.DiGraph, state: dict[str, Any], affected_system_ids: list[str]) -> list[list[str]]:
    roots = state.get("cascade_roots") or ["SVC-checkout"]
    affected = set(affected_system_ids)
    paths: list[list[str]] = []

    for root in roots:
        if root not in graph:
            continue
        for target in sorted(affected):
            if target == root or target not in graph:
                continue
            if graph.nodes.get(target, {}).get("node_type") != "System":
                continue
            try:
                path = nx.shortest_path(graph, root, target)
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                continue
            if len(path) > 1 and all(graph.nodes.get(node, {}).get("node_type") == "System" for node in path):
                paths.append(path)

    deduped = []
    seen = set()
    for path in sorted(paths, key=lambda item: (len(item), item)):
        key = tuple(path)
        if key not in seen:
            seen.add(key)
            deduped.append(path)
    return deduped[:8]
