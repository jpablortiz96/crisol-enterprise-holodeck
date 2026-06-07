import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any


TELEMETRY_DIR = Path(__file__).resolve().parents[2] / ".crisol_telemetry"
EVENT_FILE = TELEMETRY_DIR / "events.jsonl"
_LOCK = RLock()
_ALLOWED_KEYS = {
    "session_id",
    "source_session_id",
    "scenario_id",
    "role_id",
    "status",
    "turn_number",
    "severity",
    "severity_delta",
    "revenue_at_risk",
    "revenue_delta",
    "score",
    "readiness_band",
    "tool_name",
    "provider",
    "voice_enabled",
    "check_count",
    "eval_score",
    "overall_status",
    "branch_session_id",
    "citation_count",
    "event_count",
}


def emit_event(event_type: str, payload: dict[str, Any]) -> None:
    event = {
        "event_type": _compact(event_type, 80),
        "timestamp": _utc_now(),
        "payload": _sanitize_payload(payload),
    }
    with _LOCK:
        TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)
        with EVENT_FILE.open("a", encoding="utf-8") as target:
            target.write(json.dumps(event, separators=(",", ":")) + "\n")


def list_recent_events(limit: int = 100) -> list[dict[str, Any]]:
    bounded_limit = max(1, min(int(limit), 500))
    if not EVENT_FILE.exists():
        return []
    with _LOCK:
        lines = EVENT_FILE.read_text(encoding="utf-8").splitlines()
    events = []
    for line in lines[-bounded_limit:]:
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def telemetry_summary() -> dict[str, Any]:
    events = list_recent_events(limit=500)
    counts = Counter(event.get("event_type", "unknown") for event in events)
    latest_eval = next(
        (event for event in reversed(events) if event.get("event_type") == "eval_completed"),
        None,
    )
    return {
        "status": "active",
        "evaluation_status": (
            latest_eval.get("payload", {}).get("overall_status")
            if latest_eval
            else "not-run"
        ),
        "evaluation_score": (
            latest_eval.get("payload", {}).get("eval_score")
            if latest_eval
            else None
        ),
        "data_mode": "sanitized-training",
        "production_changes": False,
        "event_count": len(events),
        "event_types": dict(sorted(counts.items())),
        "latest_event": events[-1] if events else None,
        "storage": "local-jsonl",
    }


def _sanitize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    sanitized = {}
    for key, value in payload.items():
        if key not in _ALLOWED_KEYS:
            continue
        if isinstance(value, bool | int | float) or value is None:
            sanitized[key] = value
        elif isinstance(value, str):
            sanitized[key] = _compact(value, 160)
    return sanitized


def _compact(value: str, limit: int) -> str:
    return " ".join(str(value).split())[:limit]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
