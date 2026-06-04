from typing import Any

from app.grounding.local_knowledge import answer_with_citations
from app.scoring.rubric import get_rubric


ACTION_IMPACTS = {
    "restart_checkout": {
        "triage": -10,
        "technical_correctness": -20,
        "data_layer_recovery": -15,
        "business_risk_control": -20,
    },
    "freeze_db_writes": {
        "triage": 15,
        "technical_correctness": 20,
        "data_layer_recovery": 20,
        "escalation_judgment": 10,
        "business_risk_control": 5,
    },
    "escalate_incident_command": {
        "communication": 20,
        "escalation_judgment": 20,
        "triage": 5,
        "business_risk_control": 10,
    },
    "correlate_observability": {
        "triage": 15,
        "technical_correctness": 10,
        "communication": 5,
    },
    "gradual_restore": {
        "technical_correctness": 10,
        "communication": 10,
        "data_layer_recovery": 15,
        "business_risk_control": 20,
    },
    "ignore_database_symptoms": {
        "triage": -15,
        "data_layer_recovery": -20,
        "business_risk_control": -10,
    },
    "failover_without_validation": {
        "technical_correctness": -15,
        "data_layer_recovery": -15,
        "escalation_judgment": -5,
    },
}


FAILURE_MODE_LABELS = {
    "unsafe_restart_before_db_validation": "Unsafe restart before database validation increased cascade risk.",
    "premature_failover": "Premature failover was attempted without validation evidence.",
    "weak_escalation": "Escalation did not happen early enough for the uncertainty and exposure level.",
    "missing_observability": "The response lacked enough observability correlation before action.",
    "late_business_risk_control": "Business risk control came after exposure had already expanded.",
}


def generate_competence_report(session: dict[str, Any]) -> dict[str, Any]:
    rubric = get_rubric()
    dimension_scores = _score_dimensions(session, rubric)
    overall = round(
        sum(dimension_scores[dimension_id] * rubric[dimension_id]["weight"] for dimension_id in rubric),
        1,
    )
    readiness_band = _readiness_band(overall)
    evidence_trail = _build_evidence_trail(session)
    failure_modes = _detect_failure_modes(session, dimension_scores)
    skill_gaps = _skill_gaps(session, rubric, dimension_scores)
    certification_alignment = _certification_alignment(rubric, dimension_scores)
    next_best_actions = _next_best_actions(skill_gaps, failure_modes)
    citations = _unique_citations(
        [
            *_collect_session_citations(session),
            *[citation for item in evidence_trail for citation in item["citations"]],
            *[citation for item in next_best_actions for citation in item["citations"]],
        ]
    )
    dimensions = {
        dimension_id: {
            "score": round(float(score), 1),
            "weight": rubric[dimension_id]["weight"],
            "label": rubric[dimension_id]["label"],
            "description": rubric[dimension_id]["description"],
            "linked_skills": rubric[dimension_id]["linked_skills"],
            "linked_certifications": rubric[dimension_id]["linked_certifications"],
        }
        for dimension_id, score in dimension_scores.items()
    }

    return {
        "report_id": f"RPT-{session['session_id']}",
        "session_id": session["session_id"],
        "overall_score": overall,
        "score": overall,
        "readiness_band": readiness_band,
        "executive_summary": _executive_summary(overall, readiness_band, failure_modes),
        "dimensions": dimensions,
        "evidence_trail": evidence_trail,
        "failure_modes": failure_modes,
        "skill_gaps": skill_gaps,
        "certification_alignment": certification_alignment,
        "next_best_actions": next_best_actions,
        "citations": citations,
    }


def _score_dimensions(session: dict[str, Any], rubric: dict[str, dict[str, Any]]) -> dict[str, float]:
    scores = {dimension_id: 62.0 for dimension_id in rubric}
    for turn in session.get("turns", []):
        action_type = turn["decision"].get("action_type", "")
        for dimension_id, delta in ACTION_IMPACTS.get(action_type, {}).items():
            scores[dimension_id] = max(0.0, min(100.0, scores[dimension_id] + delta))
        revenue_delta = float(turn["consequence"].get("revenue_delta", 0.0))
        if revenue_delta > 0:
            scores["business_risk_control"] = max(0.0, scores["business_risk_control"] - 5)
        elif revenue_delta < 0:
            scores["business_risk_control"] = min(100.0, scores["business_risk_control"] + 5)
    return scores


def _build_evidence_trail(session: dict[str, Any]) -> list[dict[str, Any]]:
    evidence = []
    for turn in session.get("turns", []):
        consequence = turn["consequence"]
        action_type = turn["decision"].get("action_type", "")
        linked_dimension = _linked_dimension_for_action(action_type)
        observation = f"Turn {turn['turn_number']} decision: {turn['decision']['label']}."
        impact = (
            f"Severity changed by {consequence['severity_delta']} to {consequence['new_severity']}; "
            f"revenue delta {consequence['revenue_delta']}."
        )
        if consequence.get("newly_affected_systems"):
            impact += f" Newly affected systems: {', '.join(consequence['newly_affected_systems'])}."
        if consequence.get("recovered_systems"):
            impact += f" Recovered systems: {', '.join(consequence['recovered_systems'])}."
        evidence.append(
            {
                "evidence_id": f"EVD-{turn['turn_number']:03d}",
                "turn_number": turn["turn_number"],
                "observation": observation,
                "impact": impact,
                "linked_dimension": linked_dimension,
                "citations": _unique_citations(turn.get("citations", [])),
            }
        )
    return evidence


def _detect_failure_modes(session: dict[str, Any], dimension_scores: dict[str, float]) -> list[dict[str, Any]]:
    action_types = [turn["decision"].get("action_type") for turn in session.get("turns", [])]
    modes = []

    if "restart_checkout" in action_types:
        modes.append(_failure("unsafe_restart_before_db_validation", ["technical_correctness", "data_layer_recovery"]))
    if "failover_without_validation" in action_types:
        modes.append(_failure("premature_failover", ["technical_correctness", "data_layer_recovery"]))
    if _index_of(action_types, "escalate_incident_command") > 2:
        modes.append(_failure("weak_escalation", ["communication", "escalation_judgment"]))
    if _index_of(action_types, "correlate_observability") > 3:
        modes.append(_failure("missing_observability", ["triage", "technical_correctness"]))
    if any(turn["consequence"].get("revenue_delta", 0) > 0 for turn in session.get("turns", [])):
        modes.append(_failure("late_business_risk_control", ["business_risk_control"]))

    for dimension_id, score in dimension_scores.items():
        if score < 65 and not any(dimension_id in mode["linked_dimensions"] for mode in modes):
            modes.append(
                {
                    "mode_id": f"low_{dimension_id}",
                    "description": f"{dimension_id.replace('_', ' ').title()} needs more consistent evidence.",
                    "linked_dimensions": [dimension_id],
                }
            )

    return modes


def _skill_gaps(
    session: dict[str, Any],
    rubric: dict[str, dict[str, Any]],
    dimension_scores: dict[str, float],
) -> list[dict[str, Any]]:
    gaps = []
    for dimension_id, score in sorted(dimension_scores.items(), key=lambda item: item[1]):
        if score >= 88 and gaps:
            continue
        severity = "high" if score < 65 else "medium" if score < 80 else "low"
        for skill_id in rubric[dimension_id]["linked_skills"][:2]:
            gaps.append(
                {
                    "skill_id": skill_id,
                    "dimension_id": dimension_id,
                    "severity": severity,
                    "recommended_practice_scenario": session["scenario"]["id"],
                    "rationale": f"Score of {round(score, 1)} in {rubric[dimension_id]['label']} indicates practice value.",
                    "citations": answer_with_citations(_query_for_dimension(dimension_id), top_k=2)["citations"],
                }
            )
        if len(gaps) >= 5:
            break
    return gaps


def _certification_alignment(
    rubric: dict[str, dict[str, Any]],
    dimension_scores: dict[str, float],
) -> list[dict[str, Any]]:
    cert_scores: dict[str, list[float]] = {}
    for dimension_id, score in dimension_scores.items():
        for certification in rubric[dimension_id]["linked_certifications"]:
            cert_scores.setdefault(certification, []).append(score)

    alignment = []
    for certification_id, scores in sorted(cert_scores.items()):
        alignment_score = round(sum(scores) / len(scores), 1)
        alignment.append(
            {
                "certification_id": certification_id,
                "alignment_score": alignment_score,
                "risk": _risk_for_score(alignment_score),
                "note": "Synthetic readiness guidance only; not an official certification status.",
                "linked_dimensions": [
                    dimension_id
                    for dimension_id, dimension in rubric.items()
                    if certification_id in dimension["linked_certifications"]
                ],
                "citations": answer_with_citations(f"{certification_id} guide readiness", top_k=2)["citations"],
            }
        )
    return alignment


def _next_best_actions(skill_gaps: list[dict[str, Any]], failure_modes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    primary_gap = skill_gaps[0] if skill_gaps else None
    actions = [
        {
            "action_id": "NBA-001",
            "title": "Run a database-first recovery replay",
            "rationale": "The strongest readiness gain comes from validating writer ownership before service restarts.",
            "estimated_minutes": 20,
            "citations": answer_with_citations("database recovery primary writer split brain", top_k=2)["citations"],
        },
        {
            "action_id": "NBA-002",
            "title": "Write a revenue-risk checkpoint update",
            "rationale": "Manager and support stakeholders need exposure, owner, action, and next checkpoint in one update.",
            "estimated_minutes": 15,
            "citations": answer_with_citations("incident escalation revenue at risk communication", top_k=2)["citations"],
        },
        {
            "action_id": "NBA-003",
            "title": "Build a trace correlation checklist",
            "rationale": "Observability evidence should precede recovery steps that change system state.",
            "estimated_minutes": 15,
            "citations": answer_with_citations("checkout observability orders database", top_k=2)["citations"],
        },
    ]
    if primary_gap:
        actions.insert(
            0,
            {
                "action_id": "NBA-000",
                "title": f"Close the {primary_gap['skill_id']} practice gap",
                "rationale": primary_gap["rationale"],
                "estimated_minutes": 15,
                "citations": primary_gap["citations"],
            },
        )
    if any(mode["mode_id"] == "unsafe_restart_before_db_validation" for mode in failure_modes):
        actions.append(
            {
                "action_id": "NBA-004",
                "title": "Practice restart safety gates",
                "rationale": "The report found restart risk before database validation.",
                "estimated_minutes": 10,
                "citations": answer_with_citations("checkout outage split brain failover validation", top_k=2)["citations"],
            }
        )
    return actions[:5]


def _failure(mode_id: str, linked_dimensions: list[str]) -> dict[str, Any]:
    return {
        "mode_id": mode_id,
        "description": FAILURE_MODE_LABELS[mode_id],
        "linked_dimensions": linked_dimensions,
    }


def _index_of(values: list[str], target: str) -> int:
    try:
        return values.index(target) + 1
    except ValueError:
        return 999


def _linked_dimension_for_action(action_type: str) -> str:
    if action_type in {"restart_checkout", "failover_without_validation"}:
        return "technical_correctness"
    if action_type == "freeze_db_writes":
        return "data_layer_recovery"
    if action_type == "escalate_incident_command":
        return "escalation_judgment"
    if action_type == "correlate_observability":
        return "triage"
    if action_type == "gradual_restore":
        return "business_risk_control"
    return "triage"


def _readiness_band(score: float) -> str:
    if score < 55:
        return "critical"
    if score < 75:
        return "developing"
    if score < 90:
        return "ready"
    return "advanced"


def _risk_for_score(score: float) -> str:
    if score < 65:
        return "high"
    if score < 80:
        return "medium"
    return "low"


def _executive_summary(score: float, readiness_band: str, failure_modes: list[dict[str, Any]]) -> str:
    if failure_modes:
        first_mode = failure_modes[0]["description"]
        return f"Readiness is {readiness_band} at {score}. Primary concern: {first_mode}"
    return f"Readiness is {readiness_band} at {score}, with no critical failure mode detected in this synthetic run."


def _query_for_dimension(dimension_id: str) -> str:
    queries = {
        "triage": "manager readiness rubric incident triage",
        "technical_correctness": "checkout outage split brain recovery validation",
        "communication": "incident escalation stakeholder communication",
        "escalation_judgment": "incident escalation revenue at risk",
        "data_layer_recovery": "database recovery primary writer replication",
        "business_risk_control": "revenue at risk incident escalation contract",
    }
    return queries.get(dimension_id, "manager readiness rubric")


def _collect_session_citations(session: dict[str, Any]) -> list[dict[str, Any]]:
    citations = list(session.get("scenario", {}).get("citations", []))
    for turn in session.get("turns", []):
        citations.extend(turn.get("citations", []))
    return citations


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
