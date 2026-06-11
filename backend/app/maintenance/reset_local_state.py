import argparse
import shutil
from pathlib import Path
from typing import Any

from app.insights.manager import build_fragility_map
from app.orchestration.turn_loop import run_simulation
from app.scenarios.library import list_scenarios
from app.workspace.config import examples_enabled_for_validation


BACKEND_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_DIRECTORIES = (
    BACKEND_ROOT / ".crisol_sessions",
    BACKEND_ROOT / ".crisol_audio",
    BACKEND_ROOT / ".crisol_telemetry",
)
SEED_SCENARIO_IDS = (
    "SCN-SRE-001",
    "SCN-SEC-001",
    "SCN-DATA-001",
)


def reset_local_state(seed_demo: bool = False) -> dict[str, Any]:
    cleaned = []
    for directory in RUNTIME_DIRECTORIES:
        target = _validated_runtime_directory(directory)
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)
        cleaned.append(str(target.relative_to(BACKEND_ROOT)))

    sessions = _seed_sessions() if seed_demo else []
    fragility_map = build_fragility_map() if seed_demo else None
    return {
        "cleaned": cleaned,
        "seeded_session_ids": [session["session_id"] for session in sessions],
        "manager_baseline": (
            {
                "session_count": fragility_map["session_count"],
                "average_score": fragility_map["team_readiness"]["average_score"],
            }
            if fragility_map
            else None
        ),
    }


def _validated_runtime_directory(directory: Path) -> Path:
    target = directory.resolve()
    backend_root = BACKEND_ROOT.resolve()
    allowed_names = {path.name for path in RUNTIME_DIRECTORIES}
    if target.parent != backend_root or target.name not in allowed_names:
        raise ValueError(f"Refusing to clean non-runtime path: {target}")
    return target


def _seed_sessions() -> list[dict[str, Any]]:
    with examples_enabled_for_validation():
        scenarios = {scenario["scenario_id"]: scenario for scenario in list_scenarios()}
        sessions = []
        for scenario_id in SEED_SCENARIO_IDS:
            scenario = scenarios.get(scenario_id)
            if scenario is None:
                raise ValueError(f"Required seed scenario is unavailable: {scenario_id}")
            sessions.append(
                run_simulation(
                    role_id=scenario["role_id"],
                    scenario_seed=scenario_id,
                    auto_mode=True,
                )
            )
        return sessions


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reset ignored CRISOL runtime sessions, audio, and telemetry."
    )
    parser.add_argument(
        "--seed-demo",
        action="store_true",
        help="Create three clean scenario-library sessions after reset.",
    )
    arguments = parser.parse_args()
    result = reset_local_state(seed_demo=arguments.seed_demo)

    print("PASS local state reset")
    print("cleaned: " + ", ".join(result["cleaned"]))
    if result["seeded_session_ids"]:
        print("seeded_sessions: 3")
        for session_id in result["seeded_session_ids"]:
            print(f"session_id: {session_id}")
        print(
            "manager_baseline: "
            f"{result['manager_baseline']['average_score']} "
            f"across {result['manager_baseline']['session_count']} sessions"
        )


if __name__ == "__main__":
    main()
