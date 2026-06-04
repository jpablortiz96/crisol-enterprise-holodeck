from typing import Any


RUBRIC = {
    "triage": {
        "id": "triage",
        "label": "Incident triage",
        "weight": 0.20,
        "description": "Separates symptoms from root-cause evidence and chooses a stabilizing first action.",
        "positive_signals": [
            "Names the affected systems and validates impact before changing state.",
            "Uses evidence to narrow the fault domain.",
        ],
        "negative_signals": [
            "Restarts services before validating database state.",
            "Treats downstream symptoms as isolated failures.",
        ],
        "linked_skills": ["SK-incident-triage", "SK-observability"],
        "linked_certifications": ["AZ-400", "SC-200"],
    },
    "technical_correctness": {
        "id": "technical_correctness",
        "label": "Technical correctness",
        "weight": 0.20,
        "description": "Chooses technically safe recovery actions for service and dependency state.",
        "positive_signals": [
            "Validates guardrails before restarting or failing over systems.",
            "Uses trace and dependency evidence before restoration.",
        ],
        "negative_signals": [
            "Restarts checkout during database uncertainty.",
            "Forces failover without replication health evidence.",
        ],
        "linked_skills": ["SK-api-development", "SK-ci-cd", "SK-observability"],
        "linked_certifications": ["AZ-204", "AZ-400", "AZ-305"],
    },
    "communication": {
        "id": "communication",
        "label": "Stakeholder communication",
        "weight": 0.15,
        "description": "Communicates impact, uncertainty, action owners, and checkpoint timing.",
        "positive_signals": [
            "Frames customer impact and next update clearly.",
            "Keeps support and operations aligned.",
        ],
        "negative_signals": [
            "Leaves support without an approved customer-facing message.",
            "Misses checkpoint and owner details.",
        ],
        "linked_skills": ["SK-communication"],
        "linked_certifications": ["AZ-204", "AZ-400"],
    },
    "escalation_judgment": {
        "id": "escalation_judgment",
        "label": "Escalation judgment",
        "weight": 0.15,
        "description": "Escalates at the right time to the right accountable specialist or command channel.",
        "positive_signals": [
            "Activates incident command when uncertainty blocks recovery.",
            "Names specialist owners for data and service decisions.",
        ],
        "negative_signals": [
            "Delays database escalation during split-brain risk.",
            "Escalates without a clear decision owner.",
        ],
        "linked_skills": ["SK-escalation-judgment", "SK-communication"],
        "linked_certifications": ["AZ-305", "SC-200"],
    },
    "data_layer_recovery": {
        "id": "data_layer_recovery",
        "label": "Data-layer recovery",
        "weight": 0.20,
        "description": "Protects data consistency while recovering database-backed services.",
        "positive_signals": [
            "Freezes risky writes before retry traffic expands.",
            "Validates primary writer and replication health.",
        ],
        "negative_signals": [
            "Ignores database symptoms during checkout errors.",
            "Restores traffic before consistency checks pass.",
        ],
        "linked_skills": ["SK-database-recovery", "SK-data-engineering", "SK-observability"],
        "linked_certifications": ["DP-203", "AZ-305"],
    },
    "business_risk_control": {
        "id": "business_risk_control",
        "label": "Business risk control",
        "weight": 0.10,
        "description": "Controls revenue exposure and customer impact while technical recovery proceeds.",
        "positive_signals": [
            "Reduces revenue-at-risk through staged recovery.",
            "Explains contract exposure and remaining risk.",
        ],
        "negative_signals": [
            "Allows revenue exposure to rise without mitigation.",
            "Misses critical contract impact in the response plan.",
        ],
        "linked_skills": ["SK-escalation-judgment", "SK-communication"],
        "linked_certifications": ["AZ-305", "AZ-400"],
    },
}


def get_rubric() -> dict[str, dict[str, Any]]:
    return RUBRIC


def validate_weights() -> bool:
    return round(sum(dimension["weight"] for dimension in RUBRIC.values()), 5) == 1.0


def dimension_for_skill(skill_id: str) -> list[str]:
    return [
        dimension_id
        for dimension_id, dimension in RUBRIC.items()
        if skill_id in dimension["linked_skills"]
    ]


def certifications_for_dimension(dimension_id: str) -> list[str]:
    return list(RUBRIC.get(dimension_id, {}).get("linked_certifications", []))
