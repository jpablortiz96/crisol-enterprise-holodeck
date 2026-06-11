from pathlib import Path
from typing import Any
from unittest.mock import patch

from app.eval.report import build_eval_report, check_result
from app.eval.test_cases import (
    FRONTEND_SOURCE,
    REQUIRED_CITATION_FIELDS,
    REQUIRED_MCP_TOOLS,
    UI_BANNED_TERMS,
)
from app.mcp_server.tools import (
    get_competence_report,
    get_situation,
    list_registered_tools,
    make_decision,
    start_simulacrum,
)
from app.orchestration.turn_loop import run_simulation
from app.replay.time_travel import branch_from_session
from app.scenarios.importer import validate_scenario_directory
from app.scenarios.library import list_scenarios
from app.telemetry.events import emit_event
from app.voice.speech import synthesize_npc_line
from app.workspace.config import with_examples_for_validation


@with_examples_for_validation
def run_eval_suite() -> dict[str, Any]:
    source_session = run_simulation(
        role_id="ROLE-SRE",
        scenario_seed="SCN-SRE-001",
        auto_mode=True,
    )
    checks = [
        _groundedness_check(source_session),
        _citation_integrity_check(source_session),
        _scenario_safety_check(),
        _tool_reliability_check(),
        _replay_consistency_check(source_session),
        _voice_fallback_check(),
        _ui_language_check(),
    ]
    report = build_eval_report(checks)
    emit_event(
        "eval_completed",
        {
            "status": report["overall_status"],
            "overall_status": report["overall_status"],
            "eval_score": report["score"],
            "check_count": len(checks),
        },
    )
    return report


def _groundedness_check(session: dict[str, Any]) -> dict[str, Any]:
    report = session["final_score"]
    claims = [
        *report.get("dimensions", {}).values(),
        *report.get("evidence_trail", []),
        *report.get("skill_gaps", []),
        *report.get("certification_alignment", []),
        *report.get("next_best_actions", []),
    ]
    missing = [
        item.get("evidence_id") or item.get("skill_id") or item.get("action_id")
        for item in claims
        if not item.get("citations")
    ]
    status = "pass" if claims and not missing and report.get("citations") else "fail"
    return check_result(
        "EVAL-GROUNDEDNESS",
        status,
        "Scored claims include cited evidence." if status == "pass" else "Some scored claims lack citations.",
        {"claims_checked": len(claims), "missing_citations": missing},
        "Attach at least one approved citation to every scored claim." if missing else None,
    )


def _citation_integrity_check(session: dict[str, Any]) -> dict[str, Any]:
    citations = [
        *session["final_score"].get("citations", []),
        *[
            citation
            for turn in session.get("turns", [])
            for citation in turn.get("citations", [])
        ],
    ]
    invalid = []
    for index, citation in enumerate(citations):
        required_present = all(citation.get(field) for field in REQUIRED_CITATION_FIELDS)
        has_title = bool(citation.get("title") or citation.get("file_name"))
        if not required_present or not has_title:
            invalid.append(index)
    status = "pass" if citations and not invalid else "fail"
    return check_result(
        "EVAL-CITATION-INTEGRITY",
        status,
        "Citation fields are complete." if status == "pass" else "Citation fields are incomplete.",
        {"citations_checked": len(citations), "invalid_indexes": invalid},
        "Provide doc_id, title or file_name, chunk_id, and quote for each citation." if invalid else None,
    )


def _scenario_safety_check() -> dict[str, Any]:
    report = validate_scenario_directory()
    status = "pass" if report["total"] >= 5 and report["invalid"] == 0 else "fail"
    return check_result(
        "EVAL-SCENARIO-SAFETY",
        status,
        "All scenario packs pass sanitization checks." if status == "pass" else "Scenario pack safety checks failed.",
        {
            "scenario_count": report["total"],
            "valid": report["valid"],
            "invalid": report["invalid"],
        },
        "Remove sensitive patterns and complete required scenario fields." if status == "fail" else None,
    )


def _tool_reliability_check() -> dict[str, Any]:
    tools = {tool["name"] for tool in list_registered_tools()}
    started = start_simulacrum(role="ROLE-SRE", scenario_seed="SCN-SRE-001")
    situation = get_situation(started["session_id"])
    decision = make_decision(
        started["session_id"],
        "Freeze writes and identify primary database writer",
    )
    report = get_competence_report(started["session_id"])["report"]
    fields_ok = bool(
        started.get("session_id")
        and situation.get("citations")
        and decision.get("consequence")
        and "overall_score" in report
    )
    missing_tools = sorted(REQUIRED_MCP_TOOLS - tools)
    status = "pass" if not missing_tools and fields_ok else "fail"
    return check_result(
        "EVAL-TOOL-RELIABILITY",
        status,
        "MCP tools return their expected core fields." if status == "pass" else "MCP tool contract check failed.",
        {"registered_tools": len(tools), "missing_tools": missing_tools, "fields_ok": fields_ok},
        "Restore required MCP tools and output fields." if status == "fail" else None,
    )


def _replay_consistency_check(session: dict[str, Any]) -> dict[str, Any]:
    node = next(node for node in session["timeline"]["nodes"] if node["turn_number"] == 1)
    branch = branch_from_session(
        session["session_id"],
        node["node_id"],
        "Freeze writes and identify primary database writer",
    )
    status = "pass" if branch.get("comparison") and branch.get("citations") else "fail"
    return check_result(
        "EVAL-REPLAY-CONSISTENCY",
        status,
        "Replay returns a cited branch comparison." if status == "pass" else "Replay comparison is incomplete.",
        {
            "source_session_id": session["session_id"],
            "branch_session_id": branch.get("new_session_id"),
            "citation_count": len(branch.get("citations", [])),
        },
        "Return both comparison metrics and citations for every replay branch." if status == "fail" else None,
    )


def _voice_fallback_check() -> dict[str, Any]:
    with patch.dict(
        "os.environ",
        {"AZURE_SPEECH_KEY": "", "AZURE_SPEECH_REGION": ""},
    ):
        result = synthesize_npc_line(
            "Sanitized fallback verification.",
            "Operations Lead",
            session_id="SES-EVAL-VOICE",
            event_id="EVT-EVAL-VOICE",
            voice_style="calm",
        )
    status = "pass" if result["provider"] == "text-only" and not result["enabled"] else "fail"
    return check_result(
        "EVAL-VOICE-FALLBACK",
        status,
        "Text fallback remains available without Azure Speech credentials." if status == "pass" else "Voice fallback contract failed.",
        {"provider": result["provider"], "enabled": result["enabled"]},
        "Preserve text-only output when Speech configuration is absent." if status == "fail" else None,
    )


def _ui_language_check() -> dict[str, Any]:
    findings = []
    source_files = [
        *FRONTEND_SOURCE.rglob("*.tsx"),
        *FRONTEND_SOURCE.rglob("*.ts"),
    ]
    for path in sorted(source_files):
        text = path.read_text(encoding="utf-8").lower()
        for term in UI_BANNED_TERMS:
            if term in text:
                findings.append({"file": str(path.relative_to(FRONTEND_SOURCE)), "term": term})
    status = "pass" if not findings else "fail"
    return check_result(
        "EVAL-UI-LANGUAGE",
        status,
        "Product UI is free of prohibited event language." if status == "pass" else "Prohibited product language remains.",
        {"files_scanned": len(source_files), "findings": findings},
        "Replace prohibited user-facing language with product terminology." if findings else None,
    )


def main() -> None:
    report = run_eval_suite()
    if report["overall_status"] == "fail":
        for check in report["checks"]:
            if check["status"] == "fail":
                print(f"FAIL {check['check_id']}: {check['summary']}")
        raise SystemExit(1)
    print("PASS evaluation suite")
    print(f"score: {report['score']}")
    print(f"overall_status: {report['overall_status']}")
    print(f"checks: {len(report['checks'])}")
    print(f"scenario_library_count: {len(list_scenarios())}")


if __name__ == "__main__":
    main()
