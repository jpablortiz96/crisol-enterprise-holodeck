from app.orchestration.turn_loop import run_simulation
from app.streaming.sse import build_stream_events
from app.voice.speech import is_speech_configured, synthesize_npc_line
from app.workspace.config import with_examples_for_validation


REQUIRED_EVENT_TYPES = {
    "session_started",
    "scenario_intro",
    "turn_started",
    "decision_selected",
    "npc_reaction",
    "consequence_delta",
    "timeline_updated",
    "score_final",
    "coach_plan",
    "manager_snapshot",
    "session_completed",
}


@with_examples_for_validation
def main() -> None:
    session = run_simulation(role_id="ROLE-SRE", auto_mode=True)
    assert session.get("timeline"), "Expected timeline in simulated session."

    events = build_stream_events(session)
    event_types = {event["event"] for event in events}
    missing = REQUIRED_EVENT_TYPES - event_types
    assert not missing, f"Missing stream event types: {sorted(missing)}"
    assert len(events) >= 20, "Expected at least 20 stream events."
    assert events[0]["event"] == "session_started", "First event must start the session."
    assert events[1]["event"] == "scenario_intro", "Second event must introduce the scenario."
    assert events[-1]["event"] == "session_completed", "Last event must complete the session."
    reaction_event = next(event for event in events if event["event"] == "npc_reaction")
    for field in (
        "persona",
        "role",
        "communication_style",
        "pressure_profile",
        "voice_style",
        "avatar_style",
        "message",
        "pressure_level",
        "voice",
    ):
        assert field in reaction_event["data"], f"Missing persona metadata: {field}"

    speech_configured = is_speech_configured()
    voice_test = synthesize_npc_line(
        "Synthetic test line.",
        "Operations Lead",
        "SES-VOICE-TEST",
        "EVT-001",
        voice_style="calm",
    )

    if speech_configured:
        assert voice_test["provider"] in {
            "azure-speech",
            "azure-speech-fallback",
        }, "Configured speech must use Azure Speech or its safe fallback."
        if voice_test["provider"] == "azure-speech-fallback":
            print("WARNING Azure Speech synthesis failed; text fallback remains active.")
    else:
        assert voice_test["provider"] == "text-only", "Missing speech config must use text-only provider."

    print("PASS phase7 validation")
    print(f"session_id: {session['session_id']}")
    print(f"turns: {len(session['turns'])}")
    print(f"timeline_nodes: {session['timeline']['summary']['total_nodes']}")
    print(f"stream_events: {len(events)}")
    print(f"speech_configured: {str(speech_configured).lower()}")
    print(f"speech_provider: {voice_test['provider']}")
    print(f"voice_test_audio_url: {voice_test['audio_url']}")
    print(f"scenario_personas: {len(session['scenario']['personas'])}")


if __name__ == "__main__":
    main()
