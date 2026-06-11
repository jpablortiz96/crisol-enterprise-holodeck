import json
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Iterator
from functools import wraps

from app.scenarios.validators import validate_no_sensitive_content


DATA_ROOT = Path(__file__).resolve().parents[1] / "data"
WORKSPACE_ROOT = DATA_ROOT / "workspace"
WORKSPACE_CONFIG_DIR = WORKSPACE_ROOT / "config"
WORKSPACE_CONFIG_FILE = WORKSPACE_CONFIG_DIR / "workspace.json"
WORKSPACE_SCENARIO_DIR = WORKSPACE_ROOT / "scenario_packs"
WORKSPACE_KNOWLEDGE_DIR = WORKSPACE_ROOT / "knowledge"
WORKSPACE_ROLE_DIR = WORKSPACE_ROOT / "roles"
WORKSPACE_SKILL_DIR = WORKSPACE_ROOT / "skills"
WORKSPACE_PROFILE_DIR = WORKSPACE_ROOT / "profiles"
EXAMPLES_ROOT = DATA_ROOT / "examples"
EXAMPLE_SCENARIO_DIR = EXAMPLES_ROOT / "scenario_packs"
EXAMPLE_KNOWLEDGE_DIR = EXAMPLES_ROOT / "knowledge"

WORKSPACE_CONTENT_DIRECTORIES = (
    WORKSPACE_SCENARIO_DIR,
    WORKSPACE_KNOWLEDGE_DIR,
    WORKSPACE_ROLE_DIR,
    WORKSPACE_SKILL_DIR,
    WORKSPACE_PROFILE_DIR,
)
_LOCK = RLock()


def get_workspace_config() -> dict[str, Any]:
    ensure_workspace_directories()
    with _LOCK:
        if not WORKSPACE_CONFIG_FILE.exists():
            return save_workspace_config(_empty_config())
        try:
            config = json.loads(WORKSPACE_CONFIG_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError("Workspace configuration is not valid JSON.") from error
    return _normalize_config(config)


def save_workspace_config(config: dict[str, Any]) -> dict[str, Any]:
    ensure_workspace_directories()
    normalized = _normalize_config(config)
    with _LOCK:
        WORKSPACE_CONFIG_FILE.write_text(
            json.dumps(normalized, indent=2) + "\n",
            encoding="utf-8",
        )
    return normalized


def initialize_empty_workspace() -> dict[str, Any]:
    ensure_workspace_directories()
    with _LOCK:
        for directory in WORKSPACE_CONTENT_DIRECTORIES:
            for path in directory.iterdir():
                if path.is_file():
                    path.unlink()
        config = _empty_config()
        WORKSPACE_CONFIG_FILE.write_text(
            json.dumps(config, indent=2) + "\n",
            encoding="utf-8",
        )
    return workspace_status()


def enable_examples() -> dict[str, Any]:
    config = get_workspace_config()
    config["load_examples"] = True
    config["data_mode"] = (
        "workspace-with-examples" if _workspace_item_count() else "examples"
    )
    config["updated_at"] = _now()
    save_workspace_config(config)
    return workspace_status()


def disable_examples() -> dict[str, Any]:
    config = get_workspace_config()
    config["load_examples"] = False
    config["data_mode"] = "workspace" if _workspace_item_count() else "empty"
    config["updated_at"] = _now()
    save_workspace_config(config)
    return workspace_status()


def mark_workspace_configured() -> dict[str, Any]:
    config = get_workspace_config()
    config["data_mode"] = (
        "workspace-with-examples" if config["load_examples"] else "workspace"
    )
    config["updated_at"] = _now()
    return save_workspace_config(config)


def configure_organization(organization: dict[str, Any]) -> dict[str, Any]:
    values = {
        "organization_name": str(organization.get("organization_name", "")).strip(),
        "industry": str(organization.get("industry", "")).strip(),
        "workspace_name": str(organization.get("workspace_name", "")).strip(),
    }
    errors = validate_no_sensitive_content(values)
    if errors:
        raise ValueError("; ".join(errors))
    if not values["workspace_name"]:
        values["workspace_name"] = "New CRISOL Workspace"

    config = get_workspace_config()
    config.update(values)
    config["updated_at"] = _now()
    save_workspace_config(config)
    return workspace_status()


def workspace_status() -> dict[str, Any]:
    config = get_workspace_config()
    counts = {
        "scenario_count": _count_files(WORKSPACE_SCENARIO_DIR, "*.json"),
        "knowledge_count": _count_files(WORKSPACE_KNOWLEDGE_DIR, "*.md"),
        "role_count": _count_files(WORKSPACE_ROLE_DIR, "*.json"),
        "skill_count": _count_files(WORKSPACE_SKILL_DIR, "*.json"),
        "profile_count": _count_files(WORKSPACE_PROFILE_DIR, "*.json"),
    }
    is_empty = not any(counts.values())
    return {
        "workspace": config,
        **counts,
        "load_examples": bool(config["load_examples"]),
        "is_empty": is_empty,
    }


def ensure_workspace_directories() -> None:
    WORKSPACE_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    EXAMPLE_SCENARIO_DIR.mkdir(parents=True, exist_ok=True)
    EXAMPLE_KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    for directory in WORKSPACE_CONTENT_DIRECTORIES:
        directory.mkdir(parents=True, exist_ok=True)


@contextmanager
def examples_enabled_for_validation() -> Iterator[None]:
    original = get_workspace_config()
    try:
        updated = {**original, "load_examples": True, "updated_at": _now()}
        save_workspace_config(updated)
        yield
    finally:
        save_workspace_config(original)


def with_examples_for_validation(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        with examples_enabled_for_validation():
            return function(*args, **kwargs)

    return wrapped


def _empty_config() -> dict[str, Any]:
    timestamp = _now()
    return {
        "workspace_id": "WS-LOCAL",
        "workspace_name": "New CRISOL Workspace",
        "organization_name": "",
        "industry": "",
        "data_mode": "empty",
        "load_examples": False,
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def _normalize_config(config: dict[str, Any]) -> dict[str, Any]:
    required = {
        "workspace_id",
        "workspace_name",
        "organization_name",
        "industry",
        "data_mode",
        "load_examples",
        "created_at",
        "updated_at",
    }
    missing = sorted(required - set(config))
    if missing:
        raise ValueError(f"Workspace configuration is missing: {', '.join(missing)}")
    normalized = {
        "workspace_id": str(config["workspace_id"]).strip() or "WS-LOCAL",
        "workspace_name": str(config["workspace_name"]).strip() or "New CRISOL Workspace",
        "organization_name": str(config["organization_name"]).strip(),
        "industry": str(config["industry"]).strip(),
        "data_mode": str(config["data_mode"]).strip() or "empty",
        "load_examples": bool(config["load_examples"]),
        "created_at": str(config["created_at"]).strip() or _now(),
        "updated_at": str(config["updated_at"]).strip() or _now(),
    }
    if not normalized["workspace_id"].startswith("WS-"):
        raise ValueError("workspace_id must use the WS-* identifier format.")
    return normalized


def _count_files(directory: Path, pattern: str) -> int:
    return sum(1 for path in directory.glob(pattern) if path.is_file())


def _workspace_item_count() -> int:
    return sum(
        _count_files(directory, "*.md" if directory == WORKSPACE_KNOWLEDGE_DIR else "*.json")
        for directory in WORKSPACE_CONTENT_DIRECTORIES
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
