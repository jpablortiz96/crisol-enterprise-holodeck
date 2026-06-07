import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.scenarios.validators import validate_no_sensitive_content, validate_scenario_pack


SCENARIO_PACK_DIR = Path(__file__).resolve().parents[1] / "data" / "scenario_packs"


@lru_cache(maxsize=1)
def _load_scenario_packs() -> tuple[dict[str, Any], ...]:
    packs = []
    for path in sorted(SCENARIO_PACK_DIR.glob("*.json")):
        pack = json.loads(path.read_text(encoding="utf-8"))
        errors = [*validate_scenario_pack(pack), *validate_no_sensitive_content(pack)]
        if errors:
            raise ValueError(f"Invalid scenario pack {path.name}: {'; '.join(errors)}")
        packs.append(pack)
    return tuple(packs)


def list_scenarios() -> list[dict[str, Any]]:
    return [
        {
            "scenario_id": pack["scenario_id"],
            "title": pack["title"],
            "industry": pack["industry"],
            "role_id": pack["role_id"],
            "difficulty": pack["difficulty"],
            "estimated_minutes": pack["estimated_minutes"],
            "data_classification": pack["data_classification"],
            "tags": pack["tags"],
        }
        for pack in _load_scenario_packs()
    ]


def get_scenario(scenario_id: str) -> dict[str, Any]:
    normalized = scenario_id.strip().upper()
    for pack in _load_scenario_packs():
        if pack["scenario_id"].upper() == normalized:
            return json.loads(json.dumps(pack))
    raise FileNotFoundError(f"Scenario pack not found: {scenario_id}")


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
        for pack in _load_scenario_packs()
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
        raise FileNotFoundError(f"No scenario pack found for {filters or 'the requested filters'}.")
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
        "personas": scenario_pack["personas"],
        "options": scenario_pack["turns"][0]["options"],
        "expected_competencies": competencies,
        "runtime_turns": scenario_pack["turns"],
        "success_criteria": scenario_pack["success_criteria"],
        "failure_modes": scenario_pack["failure_modes"],
        "knowledge_refs": scenario_pack["knowledge_refs"],
        "tags": scenario_pack["tags"],
        "source": "scenario-library",
    }
