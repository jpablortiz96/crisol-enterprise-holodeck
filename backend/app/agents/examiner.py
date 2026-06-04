from typing import Any

from app.scoring.competence_report import generate_competence_report


def score_session(session: dict[str, Any]) -> dict[str, Any]:
    report = generate_competence_report(session)
    return {
        **report,
        "score": report["overall_score"],
    }
