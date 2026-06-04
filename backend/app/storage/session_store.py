import json
import re
from pathlib import Path
from typing import Any


SESSION_DIR = Path(__file__).resolve().parents[2] / ".crisol_sessions"


def save_session(session: dict[str, Any]) -> Path:
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    file_path = SESSION_DIR / f"{_safe_file_name(session['session_id'])}.json"
    file_path.write_text(json.dumps(session, indent=2), encoding="utf-8")
    return file_path


def load_session(session_id: str) -> dict[str, Any]:
    file_path = SESSION_DIR / f"{_safe_file_name(session_id)}.json"
    if not file_path.exists():
        raise FileNotFoundError(f"Session not found: {session_id}")
    return json.loads(file_path.read_text(encoding="utf-8"))


def list_sessions() -> list[dict[str, Any]]:
    if not SESSION_DIR.exists():
        return []

    summaries = []
    for file_path in sorted(SESSION_DIR.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True):
        session = json.loads(file_path.read_text(encoding="utf-8"))
        summaries.append(
            {
                "session_id": session["session_id"],
                "scenario_id": session["scenario"]["id"],
                "scenario_title": session["scenario"]["title"],
                "turn_count": len(session.get("turns", [])),
                "final_score": session.get("final_score", {}).get("score"),
                "saved_at": session.get("saved_at"),
                "file_name": file_path.name,
            }
        )
    return summaries


def _safe_file_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")
