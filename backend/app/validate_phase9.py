from app.eval.harness import run_eval_suite
from app.orchestration.turn_loop import run_simulation
from app.scenarios.importer import validate_scenario_directory
from app.scenarios.library import list_scenarios
from app.scoring.competence_report import generate_competence_report
from app.streaming.sse import build_stream_events
from app.telemetry.events import telemetry_summary
from app.workspace.config import with_examples_for_validation


@with_examples_for_validation
def main() -> None:
    scenario_report = validate_scenario_directory()
    assert scenario_report["total"] >= 5, "Expected at least five scenario packs."
    assert scenario_report["invalid"] == 0, "All scenario packs must pass validation."

    selected = next(
        scenario for scenario in list_scenarios() if scenario["scenario_id"] == "SCN-SRE-001"
    )
    session = run_simulation(
        role_id=selected["role_id"],
        scenario_seed=selected["scenario_id"],
        auto_mode=True,
    )
    assert len(session["turns"]) >= 5, "Scenario Library run must contain at least five turns."

    events = build_stream_events(session)
    assert events[0]["event"] == "session_started", "Stream must start with session_started."
    assert events[-1]["event"] == "session_completed", "Stream must end with session_completed."

    report = generate_competence_report(session)
    assert report["overall_score"] >= 0, "Competence report must include a score."
    assert report["citations"], "Competence report must include citations."

    evaluation = run_eval_suite()
    assert evaluation["score"] >= 80, "Evaluation score must be at least 80."
    ui_check = next(
        check for check in evaluation["checks"] if check["check_id"] == "EVAL-UI-LANGUAGE"
    )
    assert ui_check["status"] == "pass", "Product UI contains prohibited language."

    telemetry = telemetry_summary()
    assert telemetry["event_count"] > 0, "Telemetry must contain lifecycle events."

    print("PASS phase9 validation")
    print(f"scenario_packs: {scenario_report['total']}")
    print(f"selected_scenario: {selected['scenario_id']}")
    print(f"turns: {len(session['turns'])}")
    print(f"stream_events: {len(events)}")
    print(f"competence_score: {report['overall_score']}")
    print(f"eval_score: {evaluation['score']}")
    print(f"eval_status: {evaluation['overall_status']}")
    print(f"telemetry_events: {telemetry['event_count']}")


if __name__ == "__main__":
    main()
