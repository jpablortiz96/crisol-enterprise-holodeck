import json
import re
from pathlib import Path
from typing import Any

from app.agents.npcs import normalize_personas
from app.scenarios.validators import validate_no_sensitive_content, validate_scenario_pack
from app.workspace.config import (
    EXAMPLE_SCENARIO_DIR,
    WORKSPACE_SCENARIO_DIR,
    ensure_workspace_directories,
    get_workspace_config,
    mark_workspace_configured,
)


SCENARIO_PACK_DIR = EXAMPLE_SCENARIO_DIR


def list_workspace_scenarios() -> list[dict[str, Any]]:
    return [_scenario_summary(pack, "workspace") for pack in _load_directory(WORKSPACE_SCENARIO_DIR)]


def list_example_scenarios() -> list[dict[str, Any]]:
    return [_scenario_summary(pack, "example") for pack in _load_directory(EXAMPLE_SCENARIO_DIR)]


def list_all_available_scenarios() -> list[dict[str, Any]]:
    packs = [
        *[_with_source(pack, "workspace") for pack in _load_directory(WORKSPACE_SCENARIO_DIR)],
    ]
    if get_workspace_config()["load_examples"]:
        workspace_ids = {pack["scenario_id"] for pack in packs}
        packs.extend(
            _with_source(pack, "example")
            for pack in _load_directory(EXAMPLE_SCENARIO_DIR)
            if pack["scenario_id"] not in workspace_ids
        )
    return packs


def list_scenarios() -> list[dict[str, Any]]:
    return [
        _scenario_summary(pack, pack.get("source", "workspace"))
        for pack in list_all_available_scenarios()
    ]


def get_scenario(scenario_id: str) -> dict[str, Any]:
    normalized = scenario_id.strip().upper()
    for pack in list_all_available_scenarios():
        if pack["scenario_id"].upper() == normalized:
            return json.loads(json.dumps(pack))
    raise FileNotFoundError(f"Scenario pack not found in the active workspace: {scenario_id}")


def save_workspace_scenario(pack: dict[str, Any]) -> dict[str, Any]:
    ensure_workspace_directories()
    errors = [*validate_scenario_pack(pack), *validate_no_sensitive_content(pack)]
    if errors:
        raise ValueError("; ".join(errors))
    scenario_id = str(pack["scenario_id"]).strip().upper()
    normalized = json.loads(json.dumps({**pack, "scenario_id": scenario_id}))
    file_name = re.sub(r"[^A-Za-z0-9_.-]+", "-", scenario_id.lower()).strip("-") + ".json"
    path = _safe_path(WORKSPACE_SCENARIO_DIR, file_name)
    path.write_text(json.dumps(normalized, indent=2) + "\n", encoding="utf-8")
    mark_workspace_configured()
    return _with_source(normalized, "workspace")


def select_scenario(
    role_id: str | None = None,
    scenario_id: str | None = None,
    difficulty: str | None = None,
) -> dict[str, Any]:
    if scenario_id:
        pack = get_scenario(scenario_id)
        if role_id and pack["role_id"] != role_id:
            raise ValueError(
                f"Scenario {scenario_id} is assigned to {pack['role_id']}, not {role_id}."
            )
        if difficulty and pack["difficulty"] != difficulty:
            raise ValueError(
                f"Scenario {scenario_id} has difficulty {pack['difficulty']}, not {difficulty}."
            )
        return pack

    candidates = [
        pack
        for pack in list_all_available_scenarios()
        if (not role_id or pack["role_id"] == role_id)
        and (not difficulty or pack["difficulty"] == difficulty)
    ]
    if not candidates:
        filters = ", ".join(
            value
            for value in (
                f"role_id={role_id}" if role_id else "",
                f"difficulty={difficulty}" if difficulty else "",
            )
            if value
        )
        raise FileNotFoundError(
            f"No active workspace scenario found for {filters or 'the requested filters'}."
        )
    return json.loads(json.dumps(candidates[0]))


def scenario_to_runtime_seed(scenario_pack: dict[str, Any]) -> dict[str, Any]:
    competencies = sorted(
        {
            competency
            for turn in scenario_pack["turns"]
            for option in turn["options"]
            for competency in option["competencies"]
        }
    )
    return {
        "id": scenario_pack["scenario_id"],
        "scenario_id": scenario_pack["scenario_id"],
        "title": scenario_pack["title"],
        "industry": scenario_pack["industry"],
        "role_id": scenario_pack["role_id"],
        "difficulty": scenario_pack["difficulty"],
        "estimated_minutes": scenario_pack["estimated_minutes"],
        "data_classification": scenario_pack["data_classification"],
        "business_context": scenario_pack["business_context"],
        "impacted_systems": list(scenario_pack["systems"]),
        "systems": list(scenario_pack["systems"]),
        "initial_stakes": scenario_pack["initial_stakes"],
        "personas": normalize_personas(scenario_pack),
        "options": scenario_pack["turns"][0]["options"],
        "expected_competencies": competencies,
        "runtime_turns": scenario_pack["turns"],
        "success_criteria": scenario_pack["success_criteria"],
        "failure_modes": scenario_pack["failure_modes"],
        "knowledge_refs": scenario_pack["knowledge_refs"],
        "tags": scenario_pack["tags"],
        "source": scenario_pack.get("source", "workspace"),
    }


def _load_directory(directory: Path) -> list[dict[str, Any]]:
    ensure_workspace_directories()
    packs = []
    for path in sorted(directory.glob("*.json")):
        try:
            pack = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid scenario JSON: {path.name}") from error
        errors = [*validate_scenario_pack(pack), *validate_no_sensitive_content(pack)]
        if errors:
            raise ValueError(f"Invalid scenario pack {path.name}: {'; '.join(errors)}")
        packs.append(pack)
    return packs


def _scenario_summary(pack: dict[str, Any], source: str) -> dict[str, Any]:
    return {
        "scenario_id": pack["scenario_id"],
        "title": pack["title"],
        "industry": pack["industry"],
        "role_id": pack["role_id"],
        "difficulty": pack["difficulty"],
        "estimated_minutes": pack["estimated_minutes"],
        "data_classification": pack["data_classification"],
        "tags": pack["tags"],
        "personas": normalize_personas(pack),
        "source": source,
    }


def _with_source(pack: dict[str, Any], source: str) -> dict[str, Any]:
    return {**json.loads(json.dumps(pack)), "source": source}


def _safe_path(directory: Path, file_name: str) -> Path:
    root = directory.resolve()
    target = (root / file_name).resolve()
    if target.parent != root:
        raise ValueError("Scenario path escapes the workspace scenario directory.")
    return target
