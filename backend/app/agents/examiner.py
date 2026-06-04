from typing import Any

from app.grounding.local_knowledge import answer_with_citations


DIMENSIONS = {
    "triage": {"weight": 0.25, "base": 60},
    "technical_correctness": {"weight": 0.25, "base": 60},
    "communication": {"weight": 0.20, "base": 60},
    "escalation_judgment": {"weight": 0.15, "base": 60},
    "data_layer_recovery": {"weight": 0.15, "base": 60},
}


ACTION_IMPACTS = {
    "restart_checkout": {
        "triage": -10,
        "technical_correctness": -20,
        "data_layer_recovery": -15,
    },
    "freeze_db_writes": {
        "triage": 15,
        "technical_correctness": 20,
        "data_layer_recovery": 20,
        "escalation_judgment": 10,
    },
    "escalate_incident_command": {
        "communication": 20,
        "escalation_judgment": 20,
        "triage": 5,
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
    },
    "ignore_database_symptoms": {
        "triage": -15,
        "data_layer_recovery": -20,
    },
    "failover_without_validation": {
        "technical_correctness": -15,
        "data_layer_recovery": -15,
        "escalation_judgment": -5,
    },
}


def score_session(session: dict[str, Any]) -> dict[str, Any]:
    dimension_scores = {name: spec["base"] for name, spec in DIMENSIONS.items()}

    for turn in session["turns"]:
        action_type = turn["decision"].get("action_type", "")
        for dimension, delta in ACTION_IMPACTS.get(action_type, {}).items():
            dimension_scores[dimension] = max(0, min(100, dimension_scores[dimension] + delta))

    dimensions = {
        name: {
            "score": round(float(dimension_scores[name]), 1),
            "weight": DIMENSIONS[name]["weight"],
        }
        for name in DIMENSIONS
    }
    final_score = round(
        sum(dimensions[name]["score"] * dimensions[name]["weight"] for name in DIMENSIONS),
        1,
    )
    failure_modes = _failure_modes(dimensions, session)
    grounding = answer_with_citations(
        "manager readiness rubric checkout outage database recovery incident escalation",
        top_k=4,
    )

    return {
        "score": final_score,
        "dimensions": dimensions,
        "failure_modes": failure_modes,
        "citations": grounding["citations"],
    }


def _failure_modes(dimensions: dict[str, dict[str, float]], session: dict[str, Any]) -> list[str]:
    failures = []
    action_types = [turn["decision"].get("action_type") for turn in session["turns"]]
    if "restart_checkout" in action_types:
        failures.append("Early checkout restart increased cascade risk before database ownership was validated.")
    if dimensions["technical_correctness"]["score"] < 70:
        failures.append("Technical recovery decisions need stronger validation before action.")
    if dimensions["data_layer_recovery"]["score"] < 70:
        failures.append("Database ownership and consistency risk must be handled earlier.")
    if dimensions["communication"]["score"] < 70:
        failures.append("Stakeholder updates need clearer impact, owner, and checkpoint structure.")
    if dimensions["escalation_judgment"]["score"] < 70:
        failures.append("Escalation should happen before uncertainty blocks recovery.")
    if dimensions["triage"]["score"] < 70:
        failures.append("Initial triage should separate symptoms from root-cause evidence.")
    return failures
