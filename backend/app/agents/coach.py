from typing import Any

from app.grounding.local_knowledge import answer_with_citations


GAP_PLANS = {
    "triage": [
        {
            "step": 1,
            "title": "Separate symptoms from evidence",
            "activity": "Write the symptom, suspected root cause, and missing evidence for the first incident checkpoint.",
            "estimated_minutes": 15,
            "success_criteria": "The first action is based on observed evidence rather than service symptoms alone.",
        },
        {
            "step": 2,
            "title": "Run a first-action drill",
            "activity": "Choose the stabilizing action for checkout, orders, and database uncertainty.",
            "estimated_minutes": 15,
            "success_criteria": "The decision protects consistency before changing traffic or workers.",
        },
    ],
    "technical_correctness": [
        {
            "step": 1,
            "title": "Review restart safety gates",
            "activity": "List the checks required before restarting checkout during data uncertainty.",
            "estimated_minutes": 15,
            "success_criteria": "The checklist blocks unsafe restarts until database ownership is known.",
        },
        {
            "step": 2,
            "title": "Practice validation-first recovery",
            "activity": "Replay the incident and explain why each recovery action is technically safe.",
            "estimated_minutes": 20,
            "success_criteria": "Each action has a trace, dependency, or database-health justification.",
        },
    ],
    "communication": [
        {
            "step": 1,
            "title": "Draft the checkpoint update",
            "activity": "Write a status update with impact, owner, next action, and next checkpoint.",
            "estimated_minutes": 15,
            "success_criteria": "Support can reuse the update without adding missing context.",
        },
        {
            "step": 2,
            "title": "Frame uncertainty clearly",
            "activity": "Write one sentence that states what is known and what is still being validated.",
            "estimated_minutes": 10,
            "success_criteria": "The statement does not overpromise recovery timing.",
        },
    ],
    "escalation_judgment": [
        {
            "step": 1,
            "title": "Name escalation triggers",
            "activity": "Define when database lead and incident command must join the response.",
            "estimated_minutes": 15,
            "success_criteria": "Escalation happens before uncertainty blocks recovery.",
        },
        {
            "step": 2,
            "title": "Assign decision owners",
            "activity": "Map each major recovery decision to a responsible persona.",
            "estimated_minutes": 10,
            "success_criteria": "No critical decision is left without an accountable owner.",
        },
    ],
    "data_layer_recovery": [
        {
            "step": 1,
            "title": "Validate primary writer",
            "activity": "Practice the database ownership checks before reopening writes.",
            "estimated_minutes": 20,
            "success_criteria": "The learner can explain writer ownership and replication health.",
        },
        {
            "step": 2,
            "title": "Freeze writes before recovery",
            "activity": "Replay the incident and freeze risky write paths before restarts.",
            "estimated_minutes": 15,
            "success_criteria": "Recovery preserves order consistency before traffic restoration.",
        },
    ],
    "business_risk_control": [
        {
            "step": 1,
            "title": "Quantify exposure",
            "activity": "Write the affected contracts, revenue-at-risk, and current mitigation.",
            "estimated_minutes": 15,
            "success_criteria": "The update names exposure and how the team is reducing it.",
        },
        {
            "step": 2,
            "title": "Plan staged recovery",
            "activity": "Define the checks needed before gradually restoring traffic.",
            "estimated_minutes": 15,
            "success_criteria": "Revenue risk decreases without hiding remaining system impact.",
        },
    ],
}


def generate_coach_plan(score_report: dict[str, Any], session: dict[str, Any]) -> dict[str, Any]:
    skill_gaps = score_report.get("skill_gaps", [])
    if skill_gaps:
        primary_gap = skill_gaps[0]
        top_gap = primary_gap["skill_id"]
        top_gap_dimension = primary_gap["dimension_id"]
    else:
        dimensions = score_report["dimensions"]
        top_gap_dimension = min(dimensions.items(), key=lambda item: item[1]["score"])[0]
        top_gap = top_gap_dimension

    grounding = answer_with_citations(_query_for_gap(top_gap_dimension), top_k=4)

    return {
        "top_gap": top_gap,
        "top_gap_dimension": top_gap_dimension,
        "micro_plan": GAP_PLANS[top_gap_dimension],
        "practice_scenario": session["scenario"]["id"],
        "manager_note": _manager_note(score_report, top_gap_dimension),
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
    if top_gap == "business_risk_control":
        return "revenue at risk incident escalation contract"
    return "manager readiness rubric incident triage"


def _manager_note(score_report: dict[str, Any], top_gap_dimension: str) -> str:
    band = score_report.get("readiness_band", "developing")
    score = score_report.get("score", score_report.get("overall_score", 0))
    return (
        f"Synthetic readiness is {band} at {score}. "
        f"Prioritize practice in {top_gap_dimension.replace('_', ' ')} before raising scenario difficulty."
    )
