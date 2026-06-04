from typing import Any

from app.grounding.local_knowledge import answer_with_citations


GAP_PLANS = {
    "triage": [
        "Replay the first 10 minutes and write the symptom, hypothesis, and evidence list.",
        "Practice separating checkout symptoms from database consistency signals.",
        "Run one timed incident drill focused on first stabilizing action.",
    ],
    "technical_correctness": [
        "Review rollback, retry, and failover guardrails before making service changes.",
        "Practice explaining why a restart can worsen a split-brain cascade.",
        "Write a validation checklist for each recovery action.",
    ],
    "communication": [
        "Draft status updates with impact, action owner, next checkpoint, and uncertainty.",
        "Practice a support-facing customer impact statement.",
        "Use the incident channel format before each major recovery step.",
    ],
    "escalation_judgment": [
        "Define escalation triggers before the next drill starts.",
        "Practice naming the exact specialist needed and the decision they own.",
        "Review revenue-at-risk thresholds for incident command activation.",
    ],
    "data_layer_recovery": [
        "Study primary writer validation and replication health checks.",
        "Practice freezing writes before service restarts.",
        "Run the split-brain scenario again with a database-first recovery plan.",
    ],
}


def generate_coach_plan(score_report: dict[str, Any], session: dict[str, Any]) -> dict[str, Any]:
    dimensions = score_report["dimensions"]
    top_gap = min(dimensions.items(), key=lambda item: item[1]["score"])[0]
    grounding = answer_with_citations(_query_for_gap(top_gap), top_k=4)

    return {
        "top_gap": top_gap,
        "micro_plan": GAP_PLANS[top_gap],
        "practice_scenario": session["scenario"]["id"],
        "citations": grounding["citations"],
    }


def _query_for_gap(top_gap: str) -> str:
    if top_gap == "data_layer_recovery":
        return "database recovery split brain primary writer"
    if top_gap == "technical_correctness":
        return "checkout outage split brain recovery"
    if top_gap == "communication":
        return "incident escalation stakeholder communication"
    if top_gap == "escalation_judgment":
        return "incident escalation revenue at risk"
    return "manager readiness rubric incident triage"
