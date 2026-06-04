import json
from collections import Counter
from pathlib import Path
from typing import Any

import networkx as nx


DEFAULT_DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def _load_json(data_dir: Path, filename: str) -> list[dict[str, Any]]:
    with (data_dir / filename).open("r", encoding="utf-8") as source:
        return json.load(source)


def _add_node(graph: nx.DiGraph, node_id: str, node_type: str, **attributes: Any) -> None:
    graph.add_node(node_id, node_type=node_type, **attributes)


def _add_edge(graph: nx.DiGraph, source: str, target: str, relationship: str) -> None:
    if source in graph and target in graph:
        graph.add_edge(source, target, relationship=relationship)


def load_ontology(data_dir: Path | None = None) -> nx.DiGraph:
    data_path = data_dir or DEFAULT_DATA_DIR
    graph = nx.DiGraph()

    roles = _load_json(data_path, "roles.json")
    skills = _load_json(data_path, "skills.json")
    certifications = _load_json(data_path, "certifications.json")
    employees = _load_json(data_path, "employees.json")
    contracts = _load_json(data_path, "contracts.json")
    systems = _load_json(data_path, "systems.json")
    scenarios = _load_json(data_path, "scenarios.json")
    work_signals = _load_json(data_path, "work_signals.json")

    for skill in skills:
        _add_node(graph, skill["id"], "Skill", **skill)

    for certification in certifications:
        _add_node(graph, certification["id"], "Certification", **certification)

    for role in roles:
        _add_node(graph, role["id"], "Role", **role)

    for system in systems:
        _add_node(graph, system["id"], "System", **system)

    for contract in contracts:
        _add_node(graph, contract["id"], "Contract", **contract)

    for employee in employees:
        _add_node(graph, employee["id"], "Employee", **employee)

    for scenario in scenarios:
        _add_node(graph, scenario["id"], "Scenario", **scenario)

    for signal in work_signals:
        signal_id = f"WS-{signal['learner_id']}"
        _add_node(graph, signal_id, "WorkSignal", id=signal_id, **signal)

    for skill in skills:
        for prerequisite_id in skill.get("prerequisites", []):
            _add_edge(graph, prerequisite_id, skill["id"], "prerequisite_of")

    for certification in certifications:
        for skill_id in certification.get("covers_skills", []):
            _add_edge(graph, certification["id"], skill_id, "covers")

    for role in roles:
        for skill_id in role.get("required_skills", []):
            _add_edge(graph, role["id"], skill_id, "requires_skill")
        for certification_id in role.get("required_certifications", []):
            _add_edge(graph, role["id"], certification_id, "requires_certification")

    for system in systems:
        for dependency_id in system.get("depends_on", []):
            _add_edge(graph, system["id"], dependency_id, "depends_on")

    for contract in contracts:
        for certification_id in contract.get("required_certifications", []):
            _add_edge(graph, contract["id"], certification_id, "requires_certification")
        for system_id in contract.get("depends_on_systems", []):
            _add_edge(graph, contract["id"], system_id, "depends_on")

    for employee in employees:
        for skill_id in employee.get("current_skills", []):
            _add_edge(graph, employee["id"], skill_id, "has_skill")
        for certification_id in employee.get("certifications", []):
            _add_edge(graph, employee["id"], certification_id, "holds")
        for contract_id in employee.get("assigned_contracts", []):
            _add_edge(graph, employee["id"], contract_id, "assigned_to")

    for scenario in scenarios:
        for system_id in scenario.get("impacted_systems", []):
            _add_edge(graph, scenario["id"], system_id, "impacts")

    return graph


def summarize_graph(graph: nx.DiGraph) -> dict:
    counts = Counter(attributes.get("node_type", "Unknown") for _, attributes in graph.nodes(data=True))
    return {
        "total_nodes": graph.number_of_nodes(),
        "total_edges": graph.number_of_edges(),
        "counts_by_node_type": dict(sorted(counts.items())),
    }


def affected_systems(graph: nx.DiGraph, initial_system_ids: list[str]) -> list[str]:
    affected: set[str] = set()
    stack = [system_id for system_id in initial_system_ids if graph.nodes.get(system_id, {}).get("node_type") == "System"]

    while stack:
        current = stack.pop()
        if current in affected:
            continue
        affected.add(current)
        for _, target, attributes in graph.out_edges(current, data=True):
            if attributes.get("relationship") == "depends_on":
                stack.append(target)

    return sorted(affected)


def revenue_at_risk(graph: nx.DiGraph, affected_system_ids: list[str]) -> float:
    affected = set(affected_system_ids)
    total = 0.0

    for contract_id, attributes in graph.nodes(data=True):
        if attributes.get("node_type") != "Contract":
            continue
        contract_systems = {
            target
            for _, target, edge_attributes in graph.out_edges(contract_id, data=True)
            if edge_attributes.get("relationship") == "depends_on"
        }
        if contract_systems & affected:
            total += float(attributes.get("revenue_per_hour", 0.0))

    return round(total, 2)


def _successors_by_relationship(graph: nx.DiGraph, node_id: str, relationship: str) -> set[str]:
    return {
        target
        for _, target, attributes in graph.out_edges(node_id, data=True)
        if attributes.get("relationship") == relationship
    }


def role_readiness(graph: nx.DiGraph, learner_id: str, role_id: str) -> dict:
    if learner_id not in graph:
        raise ValueError(f"Unknown learner: {learner_id}")
    if role_id not in graph:
        raise ValueError(f"Unknown role: {role_id}")

    required_skills = _successors_by_relationship(graph, role_id, "requires_skill")
    required_certifications = _successors_by_relationship(graph, role_id, "requires_certification")
    learner_skills = _successors_by_relationship(graph, learner_id, "has_skill")
    learner_certifications = _successors_by_relationship(graph, learner_id, "holds")

    certification_skills: set[str] = set()
    for certification_id in learner_certifications:
        certification_skills.update(_successors_by_relationship(graph, certification_id, "covers"))

    effective_skills = learner_skills | certification_skills
    missing_skills = required_skills - effective_skills
    missing_certifications = required_certifications - learner_certifications

    skill_score = (len(required_skills) - len(missing_skills)) / len(required_skills) if required_skills else 1.0
    certification_score = (
        (len(required_certifications) - len(missing_certifications)) / len(required_certifications)
        if required_certifications
        else 1.0
    )
    practice_score = float(graph.nodes[learner_id].get("practice_score", 0.0)) / 100.0
    readiness_score = round((skill_score * 0.45 + certification_score * 0.35 + practice_score * 0.20) * 100, 1)

    return {
        "learner_id": learner_id,
        "role_id": role_id,
        "readiness_score": readiness_score,
        "required_skills": sorted(required_skills),
        "effective_skills": sorted(effective_skills),
        "missing_skills": sorted(missing_skills),
        "required_certifications": sorted(required_certifications),
        "held_certifications": sorted(learner_certifications),
        "missing_certifications": sorted(missing_certifications),
        "practice_score": graph.nodes[learner_id].get("practice_score", 0),
    }
