import argparse
import json
from pathlib import Path
from typing import Any

from app.scenarios.library import SCENARIO_PACK_DIR
from app.scenarios.validators import validate_no_sensitive_content, validate_scenario_pack


def import_scenario_pack(path: Path) -> dict[str, Any]:
    pack = json.loads(path.read_text(encoding="utf-8"))
    errors = [*validate_scenario_pack(pack), *validate_no_sensitive_content(pack)]
    return {
        "path": str(path),
        "scenario_id": pack.get("scenario_id"),
        "valid": not errors,
        "errors": errors,
        "pack": pack,
    }


def validate_scenario_directory(directory: Path = SCENARIO_PACK_DIR) -> dict[str, Any]:
    results = [import_scenario_pack(path) for path in sorted(directory.glob("*.json"))]
    return {
        "directory": str(directory),
        "total": len(results),
        "valid": sum(1 for result in results if result["valid"]),
        "invalid": sum(1 for result in results if not result["valid"]),
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate CRISOL scenario packs.")
    parser.add_argument("path", nargs="?", type=Path, help="Optional scenario pack path.")
    arguments = parser.parse_args()
    report = (
        {"results": [import_scenario_pack(arguments.path)]}
        if arguments.path
        else validate_scenario_directory()
    )
    failures = [result for result in report["results"] if not result["valid"]]
    if failures:
        for result in failures:
            print(f"FAIL {result['scenario_id'] or result['path']}: {'; '.join(result['errors'])}")
        raise SystemExit(1)
    print("PASS scenario pack validation")
    print(f"scenario_packs: {len(report['results'])}")
    print("scenario_ids: " + ", ".join(result["scenario_id"] for result in report["results"]))


if __name__ == "__main__":
    main()
