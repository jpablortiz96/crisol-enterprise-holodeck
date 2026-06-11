from app.scenarios.importer import validate_scenario_directory
from app.scenarios.library import list_scenarios, save_workspace_scenario
from app.workspace.config import (
    WORKSPACE_SCENARIO_DIR,
    disable_examples,
    initialize_empty_workspace,
    workspace_status,
)
from app.workspace.setup import apply_eduky_template
from app.workspace.storage import (
    list_knowledge_documents,
    list_profiles,
    save_knowledge_document,
    save_profile,
    save_role,
    save_skill,
)
from app.workspace.templates import operations_incident_template


def main() -> None:
    initialize_empty_workspace()
    empty = workspace_status()
    assert empty["is_empty"], "Workspace must initialize empty."
    assert empty["scenario_count"] == 0, "Empty workspace must contain no scenarios."
    assert list_scenarios() == [], "Active Scenario Library must be empty by default."
    assert "eduky" not in str(list_scenarios()).lower()

    save_role(
        {
            "role_id": "ROLE-WORKSPACE-TEST",
            "title": "Workspace Test Operator",
            "description": "Fictional role used to validate configurable workspace storage.",
            "required_skills": ["SK-workspace-test"],
        }
    )
    save_skill(
        {
            "skill_id": "SK-workspace-test",
            "name": "Workspace configuration",
            "description": "Configure a sanitized training workspace safely.",
        }
    )
    save_knowledge_document(
        "workspace_test_guide.md",
        "# Workspace Test Guide\n\nUse evidence, assign an owner, and verify the next checkpoint.",
    )
    scenario = operations_incident_template()
    scenario["scenario_id"] = "SCN-WORKSPACE-TEST-001"
    scenario["role_id"] = "ROLE-WORKSPACE-TEST"
    save_workspace_scenario(scenario)
    save_profile(
        {
            "profile_id": "PROFILE-WORKSPACE-TEST",
            "display_name": "Workspace Test Operator",
            "role_id": "ROLE-WORKSPACE-TEST",
            "context": "Fictional evaluated profile for configurable workspace validation.",
        }
    )

    configured = workspace_status()
    assert configured["scenario_count"] == 1
    assert configured["knowledge_count"] == 1
    assert configured["role_count"] == 1
    assert configured["skill_count"] == 1
    assert configured["profile_count"] == 1
    scenario_report = validate_scenario_directory(WORKSPACE_SCENARIO_DIR)
    assert scenario_report["invalid"] == 0
    assert scenario_report["valid"] == 1

    eduky = apply_eduky_template()
    assert eduky["scenario_count"] == 3, "Eduky template must include three scenarios."
    assert eduky["knowledge_count"] == 6, "Eduky template must include six knowledge documents."
    assert eduky["role_count"] == 5, "Eduky template must include five roles."
    assert eduky["skill_count"] == 10, "Eduky template must include ten skills."
    assert any(
        profile["profile_id"] == "PROFILE-FOUNDER-001"
        for profile in list_profiles()
    ), "Eduky Founder Operator profile is missing."
    assert len(list_knowledge_documents()) == 6

    disable_examples()
    final_status = workspace_status()
    assert final_status["load_examples"] is False
    assert final_status["scenario_count"] == 3
    assert len(list_scenarios()) == 3

    print("PASS empty workspace validation")
    print(f"empty_scenario_count: {empty['scenario_count']}")
    print(f"manual_workspace_scenario_count: {configured['scenario_count']}")
    print(f"eduky_scenario_count: {final_status['scenario_count']}")
    print(f"eduky_knowledge_count: {final_status['knowledge_count']}")
    print(f"eduky_role_count: {final_status['role_count']}")
    print(f"eduky_skill_count: {final_status['skill_count']}")
    print(f"eduky_profile_count: {final_status['profile_count']}")


if __name__ == "__main__":
    main()
