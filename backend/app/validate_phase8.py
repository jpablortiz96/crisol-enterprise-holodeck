from app.grounding.learn_mcp import search_learn_docs
from app.mcp_server.tools import (
    get_competence_report,
    get_situation,
    list_registered_tools,
    make_decision,
    run_local_demo,
    start_simulacrum,
)
from app.orchestration.turn_loop import run_simulation
from app.replay.time_travel import branch_from_session
from app.workspace.config import with_examples_for_validation


@with_examples_for_validation
def main() -> None:
    tools = list_registered_tools()
    assert len(tools) >= 6, "Expected at least six registered CRISOL tools."

    demo = run_local_demo()
    assert demo["started"]["session_id"], "MCP demo must start a session."

    started = start_simulacrum(role="ROLE-SRE", difficulty="standard")
    session_id = started["session_id"]
    situation = get_situation(session_id)
    assert situation["citations"], "Current situation must include citations."

    decision = make_decision(
        session_id,
        "Freeze writes and identify primary database writer",
    )
    assert decision["consequence"], "Decision result must include a consequence."

    report = get_competence_report(session_id)["report"]
    assert "overall_score" in report, "Competence report must include an overall score."

    learn_result = search_learn_docs("AZ-400 monitoring CI/CD")
    assert learn_result["mode"] in {
        "learn-mcp",
        "local-fallback",
    }, "Learn adapter must return live or fallback mode."

    source_session = run_simulation(role_id="ROLE-SRE", auto_mode=True)
    decision_node = next(
        node
        for node in source_session["timeline"]["nodes"]
        if node["turn_number"] == 1
    )
    branch = branch_from_session(
        source_session["session_id"],
        decision_node["node_id"],
        "Freeze writes and identify primary database writer",
    )
    assert branch["comparison"], "Replay branch must include comparison data."
    assert branch["citations"], "Replay branch must include citations."

    print("PASS phase8 validation")
    print(f"registered_tools: {len(tools)}")
    print(f"demo_session_id: {demo['started']['session_id']}")
    print(f"learn_mode: {learn_result['mode']}")
    print(f"source_session_id: {source_session['session_id']}")
    print(f"branch_session_id: {branch['new_session_id']}")
    print(f"original_score: {branch['comparison']['original_final_score']}")
    print(f"alternative_score: {branch['comparison']['alternative_projected_score']}")
    print(f"branch_citations: {len(branch['citations'])}")


if __name__ == "__main__":
    main()
