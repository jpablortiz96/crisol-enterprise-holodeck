import json
import re
from pathlib import Path
from typing import Any

from app.scenarios.validators import validate_no_sensitive_content
from app.workspace.config import (
    WORKSPACE_KNOWLEDGE_DIR,
    WORKSPACE_PROFILE_DIR,
    WORKSPACE_ROLE_DIR,
    WORKSPACE_SKILL_DIR,
    ensure_workspace_directories,
    mark_workspace_configured,
)


def save_knowledge_document(file_name: str, content: str) -> dict[str, Any]:
    ensure_workspace_directories()
    safe_name = _safe_markdown_name(file_name)
    normalized_content = content.strip()
    if not normalized_content:
        raise ValueError("Knowledge content cannot be empty.")
    _validate_safe_content({"file_name": safe_name, "content": normalized_content})
    path = _workspace_path(WORKSPACE_KNOWLEDGE_DIR, safe_name)
    path.write_text(normalized_content + "\n", encoding="utf-8")
    mark_workspace_configured()
    return {
        "file_name": path.name,
        "title": _markdown_title(normalized_content, path.stem),
        "size": path.stat().st_size,
        "data_classification": "sanitized-training",
    }


def list_knowledge_documents() -> list[dict[str, Any]]:
    ensure_workspace_directories()
    documents = []
    for path in sorted(WORKSPACE_KNOWLEDGE_DIR.glob("*.md")):
        content = path.read_text(encoding="utf-8")
        documents.append(
            {
                "file_name": path.name,
                "title": _markdown_title(content, path.stem),
                "content": content,
                "size": path.stat().st_size,
                "data_classification": "sanitized-training",
            }
        )
    return documents


def save_role(role: dict[str, Any]) -> dict[str, Any]:
    required = {"role_id", "title", "required_skills"}
    _validate_required(role, required, "Role")
    role_id = str(role["role_id"]).strip().upper()
    if not re.fullmatch(r"ROLE-[A-Z0-9-]+", role_id):
        raise ValueError("role_id must use the ROLE-* identifier format.")
    normalized = {
        **role,
        "role_id": role_id,
        "title": str(role["title"]).strip(),
        "description": str(role.get("description", "")).strip(),
        "required_skills": _string_list(role["required_skills"], "required_skills"),
        "data_classification": "sanitized-training",
    }
    return _save_json_record(WORKSPACE_ROLE_DIR, role_id, normalized)


def list_roles() -> list[dict[str, Any]]:
    return _list_json_records(WORKSPACE_ROLE_DIR)


def save_skill(skill: dict[str, Any]) -> dict[str, Any]:
    required = {"skill_id", "name"}
    _validate_required(skill, required, "Skill")
    skill_id = str(skill["skill_id"]).strip()
    if not re.fullmatch(r"SK-[A-Za-z0-9-]+", skill_id):
        raise ValueError("skill_id must use the SK-* identifier format.")
    normalized = {
        **skill,
        "skill_id": skill_id,
        "name": str(skill["name"]).strip(),
        "description": str(skill.get("description", "")).strip(),
        "data_classification": "sanitized-training",
    }
    return _save_json_record(WORKSPACE_SKILL_DIR, skill_id, normalized)


def list_skills() -> list[dict[str, Any]]:
    return _list_json_records(WORKSPACE_SKILL_DIR)


def save_profile(profile: dict[str, Any]) -> dict[str, Any]:
    required = {"profile_id", "display_name", "role_id", "context"}
    _validate_required(profile, required, "Profile")
    profile_id = str(profile["profile_id"]).strip().upper()
    if not re.fullmatch(r"PROFILE-[A-Z0-9-]+", profile_id):
        raise ValueError("profile_id must use the PROFILE-* identifier format.")
    normalized = {
        **profile,
        "profile_id": profile_id,
        "display_name": str(profile["display_name"]).strip(),
        "role_id": str(profile["role_id"]).strip().upper(),
        "context": str(profile["context"]).strip(),
        "data_classification": "sanitized-training",
    }
    return _save_json_record(WORKSPACE_PROFILE_DIR, profile_id, normalized)


def list_profiles() -> list[dict[str, Any]]:
    return _list_json_records(WORKSPACE_PROFILE_DIR)


def _save_json_record(directory: Path, identifier: str, value: dict[str, Any]) -> dict[str, Any]:
    ensure_workspace_directories()
    _validate_safe_content(value)
    file_name = re.sub(r"[^A-Za-z0-9_.-]+", "-", identifier).strip("-") + ".json"
    path = _workspace_path(directory, file_name)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    mark_workspace_configured()
    return json.loads(json.dumps(value))


def _list_json_records(directory: Path) -> list[dict[str, Any]]:
    ensure_workspace_directories()
    records = []
    for path in sorted(directory.glob("*.json")):
        try:
            records.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid workspace record: {path.name}") from error
    return records


def _validate_safe_content(value: dict[str, Any]) -> None:
    errors = validate_no_sensitive_content(value)
    if errors:
        raise ValueError("; ".join(errors))


def _validate_required(value: dict[str, Any], required: set[str], label: str) -> None:
    missing = sorted(field for field in required if not value.get(field))
    if missing:
        raise ValueError(f"{label} is missing required fields: {', '.join(missing)}")


def _string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field_name} must be a non-empty list.")
    return [str(item).strip() for item in value if str(item).strip()]


def _safe_markdown_name(file_name: str) -> str:
    candidate = Path(file_name.strip()).name
    if not candidate:
        raise ValueError("Knowledge file name is required.")
    if not candidate.lower().endswith(".md"):
        candidate += ".md"
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*\.md", candidate):
        raise ValueError("Knowledge file name contains unsupported characters.")
    return candidate.lower()


def _workspace_path(directory: Path, file_name: str) -> Path:
    root = directory.resolve()
    target = (root / file_name).resolve()
    if target.parent != root:
        raise ValueError("Workspace path escapes the configured storage directory.")
    return target


def _markdown_title(content: str, fallback: str) -> str:
    for line in content.splitlines():
        if line.strip().startswith("# "):
            return line.strip()[2:].strip()
    return fallback.replace("_", " ").replace("-", " ").title()
