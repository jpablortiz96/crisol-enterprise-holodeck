from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any

from app.scoring.competence_report import generate_competence_report
from app.storage.session_store import list_sessions, load_session


def build_fragility_map() -> dict[str, Any]:
    sessions = [_load(summary["session_id"]) for summary in list_sessions()]
    sessions = [session for session in sessions if session]

    if not sessions:
        return _empty_state()

    reports = [_report_for_session(session) for session in sessions]
    scores = [float(report.get("overall_score", report.get("score", 0))) for report in reports]
    band_distribution = Counter(report.get("readiness_band", "unknown") for report in reports)
    highest_risk_dimension = _highest_risk_dimension(reports)
    highest_risk_skill = _highest_risk_skill(reports)

    return {
        "generated_at": _now(),
        "session_count": len(sessions),
        "team_readiness": {
            "average_score": round(sum(scores) / len(scores), 1),
            "band_distribution": dict(sorted(band_distribution.items())),
            "highest_risk_dimension": highest_risk_dimension,
            "highest_risk_skill": highest_risk_skill,
        },
        "role_risk": _role_risk(sessions, reports),
        "skill_fragility": _skill_fragility(reports),
        "certification_readiness": _certification_readiness(reports),
        "privacy_note": "Sanitized aggregate training data. No PII.",
    }


def _load(session_id: str) -> dict[str, Any] | None:
    try:
        return load_session(session_id)
    except FileNotFoundError:
        return None


def _report_for_session(session: dict[str, Any]) -> dict[str, Any]:
    report = session.get("final_score")
    if not report or "skill_gaps" not in report or "certification_alignment" not in report:
        return generate_competence_report(session)
    return report


def _empty_state() -> dict[str, Any]:
    return {
        "generated_at": _now(),
        "session_count": 0,
        "team_readiness": {
            "average_score": 0.0,
            "band_distribution": {},
            "highest_risk_dimension": None,
            "highest_risk_skill": None,
        },
        "role_risk": [],
        "skill_fragility": [],
        "certification_readiness": [],
        "privacy_note": "Sanitized aggregate training data. No PII. Run a scenario first to populate manager insights.",
    }


def _highest_risk_dimension(reports: list[dict[str, Any]]) -> str | None:
    averages = _dimension_averages(reports)
    if not averages:
        return None
    return min(averages.items(), key=lambda item: item[1])[0]


def _highest_risk_skill(reports: list[dict[str, Any]]) -> str | None:
    counter = Counter()
    for report in reports:
        for gap in report.get("skill_gaps", []):
            counter[gap["skill_id"]] += {"high": 3, "medium": 2, "low": 1}.get(gap.get("severity"), 1)
    if not counter:
        return None
    return counter.most_common(1)[0][0]


def _role_risk(sessions: list[dict[str, Any]], reports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    for session, report in zip(sessions, reports):
        grouped[session["scenario"].get("role_id", "unknown")].append((session, report))

    output = []
    for role_id, items in sorted(grouped.items()):
        role_reports = [report for _, report in items]
        scores = [float(report.get("overall_score", report.get("score", 0))) for report in role_reports]
        dimension_averages = _dimension_averages(role_reports)
        weak_dimensions = [
            dimension_id
            for dimension_id, average in sorted(dimension_averages.items(), key=lambda item: item[1])
            if average < 85
        ][:3]
        average_score = round(sum(scores) / len(scores), 1)
        output.append(
            {
                "role_id": role_id,
                "sessions": len(items),
                "average_score": average_score,
                "risk_band": _risk_band(average_score),
                "weak_dimensions": weak_dimensions,
                "recommended_manager_action": _manager_action(weak_dimensions),
            }
        )
    return sorted(output, key=lambda item: (item["average_score"], item["role_id"]))


def _skill_fragility(reports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for report in reports:
        for gap in report.get("skill_gaps", []):
            skill_id = gap["skill_id"]
            entry = grouped.setdefault(
                skill_id,
                {
                    "skill_id": skill_id,
                    "linked_dimension": gap["dimension_id"],
                    "risk_total": 0,
                    "evidence_count": 0,
                },
            )
            entry["risk_total"] += {"high": 90, "medium": 65, "low": 35}.get(gap.get("severity"), 35)
            entry["evidence_count"] += 1

    output = []
    for entry in grouped.values():
        risk_score = round(entry["risk_total"] / entry["evidence_count"], 1)
        output.append(
            {
                "skill_id": entry["skill_id"],
                "linked_dimension": entry["linked_dimension"],
                "risk_score": risk_score,
                "evidence_count": entry["evidence_count"],
                "recommended_intervention": _skill_intervention(entry["linked_dimension"]),
            }
        )
    return sorted(output, key=lambda item: (-item["risk_score"], item["skill_id"]))[:10]


def _certification_readiness(reports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for report in reports:
        for alignment in report.get("certification_alignment", []):
            grouped[alignment["certification_id"]].append(float(alignment["alignment_score"]))

    return [
        {
            "certification_id": certification_id,
            "alignment_score": round(sum(scores) / len(scores), 1),
            "risk": _risk_for_alignment(sum(scores) / len(scores)),
            "note": "Sanitized training readiness signal only.",
        }
        for certification_id, scores in sorted(grouped.items())
    ]


def _dimension_averages(reports: list[dict[str, Any]]) -> dict[str, float]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for report in reports:
        for dimension_id, dimension in report.get("dimensions", {}).items():
            grouped[dimension_id].append(float(dimension["score"]))
    return {
        dimension_id: round(sum(scores) / len(scores), 1)
        for dimension_id, scores in grouped.items()
    }


def _risk_band(score: float) -> str:
    if score < 70:
        return "high"
    if score < 85:
        return "medium"
    return "low"


def _risk_for_alignment(score: float) -> str:
    if score < 65:
        return "high"
    if score < 80:
        return "medium"
    return "low"


def _manager_action(weak_dimensions: list[str]) -> str:
    if not weak_dimensions:
        return "Maintain current practice cadence and rotate scenario difficulty."
    first = weak_dimensions[0].replace("_", " ")
    return f"Schedule a focused practice scenario for {first} and review cited evidence after the run."


def _skill_intervention(dimension_id: str) -> str:
    if dimension_id == "data_layer_recovery":
        return "Run database-first recovery drills with writer validation."
    if dimension_id == "business_risk_control":
        return "Practice revenue-at-risk updates and staged restoration."
    if dimension_id == "communication":
        return "Use checkpoint templates for support and operations updates."
    if dimension_id == "escalation_judgment":
        return "Practice escalation triggers and decision-owner assignment."
    if dimension_id == "technical_correctness":
        return "Review recovery guardrails before state-changing actions."
    return "Run first-action triage drills with evidence review."


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
