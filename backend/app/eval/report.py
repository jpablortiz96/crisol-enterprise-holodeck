from datetime import datetime, timezone
from typing import Any


def build_eval_report(checks: list[dict[str, Any]]) -> dict[str, Any]:
    passed = sum(1 for check in checks if check["status"] == "pass")
    warned = sum(1 for check in checks if check["status"] == "warn")
    failed = sum(1 for check in checks if check["status"] == "fail")
    score = round((passed + warned * 0.5) / max(1, len(checks)) * 100)
    status = "fail" if failed else "warn" if warned else "pass"
    recommendations = [
        check["recommendation"]
        for check in checks
        if check["status"] != "pass" and check.get("recommendation")
    ]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "overall_status": status,
        "checks": checks,
        "score": score,
        "recommendations": recommendations,
    }


def check_result(
    check_id: str,
    status: str,
    summary: str,
    details: dict[str, Any],
    recommendation: str | None = None,
) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "status": status,
        "summary": summary,
        "details": details,
        "recommendation": recommendation,
    }
