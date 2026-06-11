from app.orchestration.turn_loop import run_simulation
from app.workspace.config import with_examples_for_validation


@with_examples_for_validation
def main() -> None:
    session = run_simulation(role_id="ROLE-SRE", auto_mode=True)
    turns = session["turns"]
    timeline = session.get("timeline")
    first_consequence = turns[0]["consequence"]
    final_score = session["final_score"]

    assert len(turns) >= 5, "Expected at least 5 turns."
    assert timeline, "Expected timeline in session."
    assert timeline["summary"]["total_nodes"] >= 6, "Expected root plus at least 5 decision nodes."
    assert len(timeline["nodes"]) == timeline["summary"]["total_nodes"], "Timeline node count mismatch."
    assert all(node["parent_node_id"] for node in timeline["nodes"] if node["turn_number"] > 0), (
        "Every non-root node must have a parent_node_id."
    )
    assert len(first_consequence["newly_affected_systems"]) >= 2, (
        "First turn must show at least 2 newly affected systems."
    )
    assert timeline["summary"]["max_severity"] > timeline["summary"]["final_severity"], (
        "Max severity must be greater than final severity."
    )
    assert 0 <= final_score["score"] <= 100, "Final score must be between 0 and 100."
    assert final_score["citations"], "Final score must include citations."

    required_consequence_fields = {
        "newly_affected_systems",
        "recovered_systems",
        "cascade_paths",
        "contract_exposure",
        "revenue_delta",
    }
    for turn in turns:
        missing = required_consequence_fields - set(turn["consequence"])
        assert not missing, f"Turn {turn['turn_number']} missing consequence fields: {sorted(missing)}"

    print("PASS phase4 validation")
    print(f"session_id: {session['session_id']}")
    print(f"turns: {len(turns)}")
    print(f"timeline_nodes: {timeline['summary']['total_nodes']}")
    print(f"max_severity: {timeline['summary']['max_severity']}")
    print(f"final_severity: {timeline['summary']['final_severity']}")
    print(f"first_turn_newly_affected: {len(first_consequence['newly_affected_systems'])}")
    print(f"final_score: {final_score['score']}")


if __name__ == "__main__":
    main()
