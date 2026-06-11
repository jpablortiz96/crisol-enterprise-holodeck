from typing import Any

from app.storage.session_store import list_sessions
from app.workspace.config import workspace_status


def workspace_walkthrough() -> dict[str, Any]:
    status = workspace_status()
    workspace = status["workspace"]
    sessions = list_sessions()
    has_completed_evaluation = any(
        session.get("final_score") is not None for session in sessions
    )
    steps = [
        _step(
            1,
            "Configure workspace",
            bool(workspace["organization_name"]),
        ),
        _step(
            2,
            "Add roles and skills",
            status["role_count"] > 0 and status["skill_count"] > 0,
        ),
        _step(3, "Add knowledge", status["knowledge_count"] > 0),
        _step(4, "Create scenarios", status["scenario_count"] > 0),
        _step(5, "Create evaluated profile", status["profile_count"] > 0),
        _step(6, "Run evaluation", bool(sessions)),
        _step(7, "Review results", has_completed_evaluation),
    ]
    actions = {
        1: "Configure the workspace name, organization, and industry.",
        2: "Add the roles and skills this readiness program will evaluate.",
        3: "Add sanitized policies and playbooks for grounded practice.",
        4: "Create a scenario with role-specific decisions and dynamic personas.",
        5: "Create the evaluated profile that will run the scenario.",
        6: "Select a scenario and run the first evaluation.",
        7: "Open Results Center and review the competence evidence.",
    }
    pending = next((step for step in steps if step["status"] == "pending"), None)
    return {
        "steps": steps,
        "next_recommended_action": (
            actions[pending["step"]]
            if pending
            else "Review results and continue scenario practice."
        ),
    }


def _step(step: int, title: str, complete: bool) -> dict[str, Any]:
    return {
        "step": step,
        "title": title,
        "status": "complete" if complete else "pending",
    }
