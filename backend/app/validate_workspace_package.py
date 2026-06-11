from app.orchestration.turn_loop import run_simulation
from app.scenarios.library import get_scenario, list_workspace_scenarios
from app.workspace.config import workspace_status
from app.workspace.package import (
    EXPORT_ROOT,
    export_workspace,
    import_workspace,
    validate_workspace_package,
    workspace_package_summary,
)
from app.workspace.setup import apply_creator_operations_template, setup_empty_workspace
from app.workspace.storage import (
    list_knowledge_documents,
    list_profiles,
    list_roles,
    list_skills,
)


LAUNCH_SCENARIO_ID = "SCN-CREATOR-LAUNCH-001"


def main() -> None:
    export_path = EXPORT_ROOT / "validation-workspace-package.json"
    if export_path.exists():
        export_path.unlink()

    empty = setup_empty_workspace()
    assert empty["scenario_count"] == 0
    assert list_workspace_scenarios() == []

    configured = apply_creator_operations_template()
    assert configured["role_count"] == 5
    assert configured["skill_count"] == 10
    assert configured["profile_count"] == 1
    assert configured["knowledge_count"] == 6
    assert configured["scenario_count"] == 3
    assert len(list_roles()) == 5
    assert len(list_skills()) == 10
    assert len(list_profiles()) == 1
    assert len(list_knowledge_documents()) == 6

    scenario = get_scenario(LAUNCH_SCENARIO_ID)
    expected_personas = [persona["persona"] for persona in scenario["personas"]]
    assert expected_personas == [
        "Launch Coordinator",
        "Student Success Lead",
        "Payment Operations Analyst",
        "Brand Communications Lead",
    ]
    first_session = _run_launch_scenario()
    assert _session_personas(first_session) == expected_personas

    package = export_workspace(export_path)
    assert export_path.is_file()
    assert validate_workspace_package(package) == []
    summary = workspace_package_summary(package)
    original_scenario_ids = set(summary["scenario_ids"])
    assert original_scenario_ids == {
        "SCN-CREATOR-LAUNCH-001",
        "SCN-CREATOR-SUPPORT-001",
        "SCN-CREATOR-CONTENT-001",
    }

    reset = setup_empty_workspace()
    assert reset["scenario_count"] == 0
    imported = import_workspace(export_path)
    assert imported["scenario_count"] == 3
    assert imported["load_examples"] is False
    imported_scenario_ids = {
        scenario["scenario_id"] for scenario in list_workspace_scenarios()
    }
    assert imported_scenario_ids == original_scenario_ids

    restored_scenario = get_scenario(LAUNCH_SCENARIO_ID)
    restored_personas = [
        persona["persona"] for persona in restored_scenario["personas"]
    ]
    assert restored_personas == expected_personas
    second_session = _run_launch_scenario()
    assert _session_personas(second_session) == expected_personas
    assert workspace_status()["scenario_count"] == 3

    export_path.unlink(missing_ok=True)
    print("PASS workspace package validation")
    print("empty_scenario_count: 0")
    print("creator_role_count: 5")
    print("creator_skill_count: 10")
    print("creator_profile_count: 1")
    print("creator_knowledge_count: 6")
    print("creator_scenario_count: 3")
    print(f"launch_personas: {', '.join(expected_personas)}")
    print(f"exported_package_id: {package['package_id']}")
    print("imported_scenario_count: 3")
    print("rerun_status: complete")


def _run_launch_scenario() -> dict:
    return run_simulation(
        role_id="ROLE-FOUNDER-OPERATOR",
        scenario_seed=LAUNCH_SCENARIO_ID,
        auto_mode=True,
    )


def _session_personas(session: dict) -> list[str]:
    names = [persona["persona"] for persona in session["scenario"]["personas"]]
    for turn in session["turns"]:
        assert [reaction["persona"] for reaction in turn["npc_reactions"]] == names
    return names


if __name__ == "__main__":
    main()
