import asyncio
import json
from typing import Any, AsyncIterator

from app.branching.timeline import build_timeline
from app.insights.manager import build_fragility_map
from app.orchestration.turn_loop import run_simulation
from app.voice.speech import synthesize_npc_line


def build_stream_events(session: dict[str, Any], manager_snapshot: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    sequence = 1
    session_id = session["session_id"]

    def add(event: str, data: dict[str, Any]) -> None:
        nonlocal sequence
        events.append(
            {
                "event": event,
                "session_id": session_id,
                "sequence": sequence,
                "data": data,
            }
        )
        sequence += 1

    add(
        "session_started",
        {
            "session_id": session_id,
            "role_id": session["scenario"].get("role_id"),
            "status": "live",
        },
    )
    add("scenario_intro", {"scenario": session["scenario"]})

    timeline_nodes = session["timeline"]["nodes"]
    for turn in session["turns"]:
        turn_number = turn["turn_number"]
        add(
            "turn_started",
            {
                "turn_number": turn_number,
                "situation": turn["situation"],
                "citations": turn["citations"],
            },
        )
        add(
            "decision_selected",
            {
                "turn_number": turn_number,
                "decision": turn["decision"],
            },
        )
        for reaction_index, reaction in enumerate(turn["npc_reactions"], start=1):
            event_id = f"EVT-T{turn_number:02d}-NPC{reaction_index:02d}"
            voice = synthesize_npc_line(
                reaction["message"],
                reaction["persona"],
                session_id=session_id,
                event_id=event_id,
            )
            add(
                "npc_reaction",
                {
                    "turn_number": turn_number,
                    "reaction": reaction,
                    "voice": voice,
                    "speech": voice,
                },
            )
        add(
            "consequence_delta",
            {
                "turn_number": turn_number,
                "consequence": turn["consequence"],
            },
        )
        add(
            "timeline_updated",
            {
                "turn_number": turn_number,
                "timeline": build_timeline(timeline_nodes[: turn_number + 1]),
            },
        )

    add("score_final", {"final_score": session["final_score"]})
    add("coach_plan", {"coach_plan": session["coach_plan"]})
    add("manager_snapshot", {"manager_snapshot": manager_snapshot or build_fragility_map()})
    add("session_completed", {"session": session, "status": "completed"})

    return events


async def scenario_event_stream(
    role_id: str = "ROLE-SRE",
    scenario_id: str | None = None,
    delay_seconds: float = 0.25,
) -> AsyncIterator[str]:
    session = run_simulation(role_id=role_id, scenario_seed=scenario_id, auto_mode=True)
    events = build_stream_events(session, manager_snapshot=build_fragility_map())

    for event in events:
        yield encode_sse_event(event)
        await asyncio.sleep(delay_seconds)


def encode_sse_event(payload: dict[str, Any]) -> str:
    return f"event: {payload['event']}\ndata: {json.dumps(payload)}\n\n"
