import argparse
import json
from typing import Any

from app.maintenance.reset_local_state import reset_local_state
from app.scenarios.library import save_workspace_scenario
from app.workspace.config import (
    disable_examples,
    enable_examples,
    get_workspace_config,
    initialize_empty_workspace,
    save_workspace_config,
    workspace_status,
)
from app.workspace.storage import (
    save_knowledge_document,
    save_profile,
    save_role,
    save_skill,
)
from app.workspace.templates import workspace_template_by_id


def setup_empty_workspace() -> dict[str, Any]:
    status = initialize_empty_workspace()
    reset_local_state(seed_demo=False)
    return status


def setup_with_examples() -> dict[str, Any]:
    return enable_examples()


def apply_workspace_template(template_id: str) -> dict[str, Any]:
    template = workspace_template_by_id(template_id)
    if template["template_id"] == "template-empty":
        return setup_empty_workspace()
    initialize_empty_workspace()
    reset_local_state(seed_demo=False)
    current = get_workspace_config()
    workspace = template["workspace"]
    save_workspace_config(
        {
            **current,
            **workspace,
            "created_at": current["created_at"],
            "updated_at": current["updated_at"],
        }
    )
    for skill in template["skills"]:
        save_skill(skill)
    for role in template["roles"]:
        save_role(role)
    for file_name, content in template["knowledge"].items():
        save_knowledge_document(file_name, content)
    for profile in template["profiles"]:
        save_profile(profile)
    for scenario in template["scenarios"]:
        save_workspace_scenario(scenario)
    disable_examples()
    return {
        **workspace_status(),
        "template_id": template["template_id"],
        "created_counts": {
            "roles": len(template["roles"]),
            "skills": len(template["skills"]),
            "profiles": len(template["profiles"]),
            "knowledge": len(template["knowledge"]),
            "scenarios": len(template["scenarios"]),
        },
    }


def apply_eduky_template() -> dict[str, Any]:
    return apply_workspace_template("template-eduky")


def apply_creator_operations_template() -> dict[str, Any]:
    return apply_workspace_template("template-creator-operations")


def main() -> None:
    parser = argparse.ArgumentParser(description="Configure the local CRISOL workspace.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--empty", action="store_true", help="Initialize an empty workspace.")
    mode.add_argument(
        "--with-examples",
        action="store_true",
        help="Enable the optional example scenario and knowledge pack.",
    )
    mode.add_argument("--status", action="store_true", help="Print workspace status.")
    mode.add_argument(
        "--eduky-template",
        action="store_true",
        help="Apply the sanitized Eduky digital education workspace template.",
    )
    mode.add_argument(
        "--creator-operations-template",
        action="store_true",
        help="Apply the sanitized Creator Operations Readiness template.",
    )
    arguments = parser.parse_args()

    if arguments.empty:
        result = setup_empty_workspace()
        label = "PASS empty workspace initialized"
    elif arguments.with_examples:
        result = setup_with_examples()
        label = "PASS example pack enabled"
    elif arguments.eduky_template:
        result = apply_eduky_template()
        label = "PASS Eduky workspace template applied"
    elif arguments.creator_operations_template:
        result = apply_creator_operations_template()
        label = "PASS Creator Operations workspace template applied"
    else:
        result = workspace_status()
        label = "PASS workspace status"

    print(label)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
