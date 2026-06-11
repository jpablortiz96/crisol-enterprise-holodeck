import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.scenarios.library import (
    get_scenario,
    list_workspace_scenarios,
    save_workspace_scenario,
)
from app.scenarios.validators import validate_no_sensitive_content, validate_scenario_pack
from app.workspace.config import get_workspace_config, save_workspace_config, workspace_status
from app.workspace.setup import setup_empty_workspace
from app.workspace.storage import (
    list_knowledge_documents,
    list_profiles,
    list_roles,
    list_skills,
    save_knowledge_document,
    save_profile,
    save_role,
    save_skill,
)


BACKEND_ROOT = Path(__file__).resolve().parents[2]
EXPORT_ROOT = BACKEND_ROOT / ".crisol_exports"
PACKAGE_CLASSIFICATION = "sanitized-training"
PACKAGE_FIELDS = {
    "package_id",
    "workspace",
    "roles",
    "skills",
    "profiles",
    "knowledge",
    "scenarios",
    "exported_at",
    "data_classification",
}


def export_workspace(output_path: Path | None = None) -> dict[str, Any]:
    package_id = f"WPK-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}"
    scenarios = []
    for summary in list_workspace_scenarios():
        scenario = get_scenario(summary["scenario_id"])
        scenario.pop("source", None)
        scenarios.append(scenario)

    package = {
        "package_id": package_id,
        "workspace": get_workspace_config(),
        "roles": list_roles(),
        "skills": list_skills(),
        "profiles": list_profiles(),
        "knowledge": [
            {
                "file_name": document["file_name"],
                "content": document.get("content", ""),
            }
            for document in list_knowledge_documents()
        ],
        "scenarios": scenarios,
        "exported_at": _now(),
        "data_classification": PACKAGE_CLASSIFICATION,
    }
    errors = validate_workspace_package(package)
    if errors:
        raise ValueError("Workspace package validation failed: " + "; ".join(errors))

    target = _export_path(output_path, package_id)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
    return package


def import_workspace(package_path: Path) -> dict[str, Any]:
    source = package_path.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Workspace package not found: {source}")
    try:
        package = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Workspace package is not valid JSON: {source.name}") from error

    errors = validate_workspace_package(package)
    if errors:
        raise ValueError("Workspace package validation failed: " + "; ".join(errors))

    setup_empty_workspace()
    summary = workspace_package_summary(package)
    imported_workspace = {
        **package["workspace"],
        "load_examples": False,
        "data_mode": (
            "workspace"
            if any(summary["counts"].values())
            else "empty"
        ),
    }
    save_workspace_config(imported_workspace)
    for skill in package["skills"]:
        save_skill(skill)
    for role in package["roles"]:
        save_role(role)
    for document in package["knowledge"]:
        save_knowledge_document(document["file_name"], document["content"])
    for profile in package["profiles"]:
        save_profile(profile)
    for scenario in package["scenarios"]:
        save_workspace_scenario(scenario)

    status = workspace_status()
    return {
        **status,
        "package_id": package["package_id"],
        "imported_counts": summary["counts"],
    }


def validate_workspace_package(package: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(package, dict):
        return ["Package must be a JSON object."]

    missing = sorted(PACKAGE_FIELDS - set(package))
    if missing:
        errors.append(f"Package is missing required fields: {', '.join(missing)}.")
        return errors
    if not re.fullmatch(r"WPK-[A-Za-z0-9-]+", str(package["package_id"])):
        errors.append("package_id must use the WPK-* identifier format.")
    if package["data_classification"] != PACKAGE_CLASSIFICATION:
        errors.append("Package data_classification must be sanitized-training.")
    if not str(package["exported_at"]).strip():
        errors.append("exported_at is required.")

    workspace = package["workspace"]
    required_workspace_fields = {
        "workspace_id",
        "workspace_name",
        "organization_name",
        "industry",
        "data_mode",
        "load_examples",
        "created_at",
        "updated_at",
    }
    if not isinstance(workspace, dict):
        errors.append("workspace must be an object.")
    else:
        workspace_missing = sorted(required_workspace_fields - set(workspace))
        if workspace_missing:
            errors.append(
                f"workspace is missing required fields: {', '.join(workspace_missing)}."
            )
        elif not str(workspace["workspace_id"]).startswith("WS-"):
            errors.append("workspace_id must use the WS-* identifier format.")

    roles = _package_list(package, "roles", errors)
    skills = _package_list(package, "skills", errors)
    profiles = _package_list(package, "profiles", errors)
    knowledge = _package_list(package, "knowledge", errors)
    scenarios = _package_list(package, "scenarios", errors)

    skill_ids: set[str] = set()
    for index, skill in enumerate(skills, start=1):
        location = f"skills[{index}]"
        if not isinstance(skill, dict):
            errors.append(f"{location} must be an object.")
            continue
        skill_id = str(skill.get("skill_id", ""))
        if not re.fullmatch(r"SK-[A-Za-z0-9-]+", skill_id):
            errors.append(f"{location}.skill_id must use the SK-* identifier format.")
        if not str(skill.get("name", "")).strip():
            errors.append(f"{location}.name is required.")
        if skill_id in skill_ids:
            errors.append(f"Duplicate skill_id: {skill_id}.")
        skill_ids.add(skill_id)
        _classification_error(skill, location, errors)

    role_ids: set[str] = set()
    for index, role in enumerate(roles, start=1):
        location = f"roles[{index}]"
        if not isinstance(role, dict):
            errors.append(f"{location} must be an object.")
            continue
        role_id = str(role.get("role_id", ""))
        if not re.fullmatch(r"ROLE-[A-Z0-9-]+", role_id):
            errors.append(f"{location}.role_id must use the ROLE-* identifier format.")
        required_skills = role.get("required_skills")
        if not isinstance(required_skills, list) or not required_skills:
            errors.append(f"{location}.required_skills must be a non-empty list.")
        else:
            unknown = sorted(set(map(str, required_skills)) - skill_ids)
            if unknown:
                errors.append(f"{location} references unknown skills: {', '.join(unknown)}.")
        if not str(role.get("title", "")).strip():
            errors.append(f"{location}.title is required.")
        if role_id in role_ids:
            errors.append(f"Duplicate role_id: {role_id}.")
        role_ids.add(role_id)
        _classification_error(role, location, errors)

    profile_ids: set[str] = set()
    for index, profile in enumerate(profiles, start=1):
        location = f"profiles[{index}]"
        if not isinstance(profile, dict):
            errors.append(f"{location} must be an object.")
            continue
        profile_id = str(profile.get("profile_id", ""))
        if not re.fullmatch(r"PROFILE-[A-Z0-9-]+", profile_id):
            errors.append(
                f"{location}.profile_id must use the PROFILE-* identifier format."
            )
        if str(profile.get("role_id", "")) not in role_ids:
            errors.append(f"{location} references an unknown role.")
        if not str(profile.get("display_name", "")).strip():
            errors.append(f"{location}.display_name is required.")
        if not str(profile.get("context", "")).strip():
            errors.append(f"{location}.context is required.")
        if profile_id in profile_ids:
            errors.append(f"Duplicate profile_id: {profile_id}.")
        profile_ids.add(profile_id)
        _classification_error(profile, location, errors)

    knowledge_names: set[str] = set()
    for index, document in enumerate(knowledge, start=1):
        location = f"knowledge[{index}]"
        if not isinstance(document, dict):
            errors.append(f"{location} must be an object.")
            continue
        file_name = str(document.get("file_name", ""))
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*\.md", file_name):
            errors.append(f"{location}.file_name must be a safe Markdown file name.")
        if not str(document.get("content", "")).strip():
            errors.append(f"{location}.content is required.")
        if file_name.lower() in knowledge_names:
            errors.append(f"Duplicate knowledge file: {file_name}.")
        knowledge_names.add(file_name.lower())

    scenario_ids: set[str] = set()
    for index, scenario in enumerate(scenarios, start=1):
        location = f"scenarios[{index}]"
        if not isinstance(scenario, dict):
            errors.append(f"{location} must be an object.")
            continue
        for error in validate_scenario_pack(scenario):
            errors.append(f"{location}: {error}")
        scenario_id = str(scenario.get("scenario_id", ""))
        if scenario_id in scenario_ids:
            errors.append(f"Duplicate scenario_id: {scenario_id}.")
        scenario_ids.add(scenario_id)
        if str(scenario.get("role_id", "")) not in role_ids:
            errors.append(f"{location} references an unknown role.")

    for error in validate_no_sensitive_content(package):
        errors.append(f"Package safety validation: {error}")
    return errors


def workspace_package_summary(package: dict[str, Any]) -> dict[str, Any]:
    return {
        "package_id": package.get("package_id"),
        "workspace_id": package.get("workspace", {}).get("workspace_id"),
        "workspace_name": package.get("workspace", {}).get("workspace_name"),
        "organization_name": package.get("workspace", {}).get("organization_name"),
        "exported_at": package.get("exported_at"),
        "data_classification": package.get("data_classification"),
        "counts": {
            "roles": len(package.get("roles", [])),
            "skills": len(package.get("skills", [])),
            "profiles": len(package.get("profiles", [])),
            "knowledge": len(package.get("knowledge", [])),
            "scenarios": len(package.get("scenarios", [])),
        },
        "scenario_ids": [
            scenario.get("scenario_id")
            for scenario in package.get("scenarios", [])
            if isinstance(scenario, dict)
        ],
    }


def _package_list(
    package: dict[str, Any],
    field: str,
    errors: list[str],
) -> list[Any]:
    value = package.get(field)
    if not isinstance(value, list):
        errors.append(f"{field} must be a list.")
        return []
    return value


def _classification_error(
    record: dict[str, Any],
    location: str,
    errors: list[str],
) -> None:
    if record.get("data_classification") != PACKAGE_CLASSIFICATION:
        errors.append(f"{location}.data_classification must be sanitized-training.")


def _export_path(output_path: Path | None, package_id: str) -> Path:
    if output_path is None:
        return EXPORT_ROOT / f"{package_id.lower()}.json"
    candidate = output_path.expanduser()
    if not candidate.is_absolute():
        candidate = EXPORT_ROOT / candidate
    return candidate.resolve()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export, import, or inspect CRISOL workspaces.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--export",
        dest="export_path",
        nargs="?",
        const="",
        metavar="PATH",
        help="Export the active workspace to backend/.crisol_exports/.",
    )
    mode.add_argument("--import", dest="import_path", metavar="PATH")
    mode.add_argument("--summary", dest="summary_path", metavar="PATH")
    arguments = parser.parse_args()

    if arguments.export_path is not None:
        requested = Path(arguments.export_path) if arguments.export_path else None
        package = export_workspace(requested)
        target = _export_path(requested, package["package_id"])
        print("PASS workspace exported")
        print(f"path: {target}")
        print(json.dumps(workspace_package_summary(package), indent=2))
        return

    package_path = Path(arguments.import_path or arguments.summary_path)
    if arguments.import_path:
        result = import_workspace(package_path)
        print("PASS workspace imported")
        print(json.dumps(result, indent=2))
        return

    try:
        package = json.loads(package_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Workspace package is not valid JSON: {package_path.name}") from error
    errors = validate_workspace_package(package)
    if errors:
        raise ValueError("Workspace package validation failed: " + "; ".join(errors))
    print("PASS workspace package valid")
    print(json.dumps(workspace_package_summary(package), indent=2))


if __name__ == "__main__":
    main()
