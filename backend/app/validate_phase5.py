from app.insights.manager import build_fragility_map
from app.orchestration.turn_loop import run_simulation
from app.scoring.competence_report import generate_competence_report
from app.scoring.rubric import validate_weights
from app.storage.session_store import list_sessions, load_session
from app.workspace.config import with_examples_for_validation


@with_examples_for_validation
def main() -> None:
    assert validate_weights(), "Rubric weights must sum to 1.0."

    sessions = [
        run_simulation(role_id="ROLE-SRE", auto_mode=True),
        run_simulation(role_id="ROLE-DEVOPS", auto_mode=True),
        run_simulation(role_id="ROLE-DATA", auto_mode=True),
    ]
    assert len(sessions) == 3, "Expected three simulation runs."

    latest_summary = list_sessions()[0]
    latest_session = load_session(latest_summary["session_id"])
    report = generate_competence_report(latest_session)

    required_report_fields = {
        "report_id",
        "overall_score",
        "readiness_band",
        "evidence_trail",
        "skill_gaps",
        "certification_alignment",
        "next_best_actions",
        "citations",
    }
    missing_report_fields = required_report_fields - set(report)
    assert not missing_report_fields, f"Missing report fields: {sorted(missing_report_fields)}"
    assert report["evidence_trail"], "Competence report must include evidence trail."
    assert report["skill_gaps"], "Competence report must include skill gaps."
    assert report["certification_alignment"], "Competence report must include certification alignment."
    assert report["next_best_actions"], "Competence report must include next best actions."
    assert report["citations"], "Competence report must include citations."

    fragility_map = build_fragility_map()
    required_manager_fields = {
        "session_count",
        "team_readiness",
        "role_risk",
        "skill_fragility",
        "certification_readiness",
        "privacy_note",
    }
    missing_manager_fields = required_manager_fields - set(fragility_map)
    assert not missing_manager_fields, f"Missing manager fields: {sorted(missing_manager_fields)}"
    assert fragility_map["session_count"] >= 3, "Manager map must include at least three sessions."
    assert fragility_map["team_readiness"], "Manager map must include team readiness."
    assert fragility_map["role_risk"], "Manager map must include role risk."
    assert fragility_map["skill_fragility"], "Manager map must include skill fragility."
    assert fragility_map["certification_readiness"], "Manager map must include certification readiness."
    assert "No PII" in fragility_map["privacy_note"], "Manager map must include privacy note."

    print("PASS phase5 validation")
    print(f"sessions_created: {len(sessions)}")
    print(f"saved_session_count: {fragility_map['session_count']}")
    print(f"latest_report_id: {report['report_id']}")
    print(f"latest_readiness_band: {report['readiness_band']}")
    print(f"latest_overall_score: {report['overall_score']}")
    print(f"evidence_items: {len(report['evidence_trail'])}")
    print(f"skill_gaps: {len(report['skill_gaps'])}")
    print(f"manager_average_score: {fragility_map['team_readiness']['average_score']}")
    print(f"highest_risk_dimension: {fragility_map['team_readiness']['highest_risk_dimension']}")


if __name__ == "__main__":
    main()
