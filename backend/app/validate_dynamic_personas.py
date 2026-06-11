import json
from unittest.mock import patch

from app.agents.npcs import fallback_personas_for_scenario
from app.orchestration.turn_loop import run_simulation
from app.scenarios.library import list_scenarios, save_workspace_scenario
from app.streaming.sse import build_stream_events
from app.workspace.setup import apply_eduky_template, setup_empty_workspace
from app.workspace.templates import customer_escalation_template


def main() -> None:
    setup_empty_workspace()
    assert list_scenarios() == [], "The default workspace must expose no scenarios."
    assert "eduky" not in json.dumps(list_scenarios()).lower()

    scenario = customer_escalation_template()
    scenario["scenario_id"] = "SCN-DYNAMIC-PERSONAS-001"
    scenario["role_id"] = "ROLE-SERVICE-RECOVERY-LEAD"
    scenario["personas"] = [
        {
            "persona": "Customer Recovery Lead",
            "role": "Escalation owner",
            "communication_style": "empathetic but urgent",
            "pressure_profile": "high",
            "voice_style": "supportive",
            "avatar_style": "holographic-customer",
        },
        {
            "persona": "Service Reliability Partner",
            "role": "Recovery evidence owner",
            "communication_style": "analytical and measured",
            "pressure_profile": "medium",
            "voice_style": "analytical",
            "avatar_style": "holographic-specialist",
        },
    ]
    save_workspace_scenario(scenario)
    session = run_simulation(
        role_id=scenario["role_id"],
        scenario_seed=scenario["scenario_id"],
        auto_mode=True,
    )
    expected_names = [persona["persona"] for persona in scenario["personas"]]
    session_names = [persona["persona"] for persona in session["scenario"]["personas"]]
    assert session_names == expected_names
    for turn in session["turns"]:
        reaction_names = [reaction["persona"] for reaction in turn["npc_reactions"]]
        assert reaction_names == expected_names
        for reaction in turn["npc_reactions"]:
            assert reaction["role"]
            assert reaction["communication_style"]
            assert reaction["pressure_profile"]
            assert reaction["voice_style"]
            assert reaction["avatar_style"]

    with patch.dict(
        "os.environ",
        {"AZURE_SPEECH_KEY": "", "AZURE_SPEECH_REGION": ""},
    ):
        events = build_stream_events(session)
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
        assert field in reaction_event["data"], f"Missing streamed persona field: {field}"

    fallback = fallback_personas_for_scenario(
        {
            "role_id": "ROLE-GENERIC-OPERATOR",
            "industry": "Professional Services",
            "tags": ["operations"],
            "difficulty": "advanced",
        }
    )
    assert fallback
    assert all(persona["persona"] not in expected_names for persona in fallback)

    apply_eduky_template()
    eduky_scenarios = list_scenarios()
    assert len(eduky_scenarios) == 3
    assert all(item["scenario_id"].startswith("SCN-EDUKY-") for item in eduky_scenarios)
    eduky = eduky_scenarios[0]
    eduky_session = run_simulation(
        role_id=eduky["role_id"],
        scenario_seed=eduky["scenario_id"],
        auto_mode=True,
    )
    eduky_names = [
        persona["persona"]
        for persona in eduky_session["scenario"]["personas"]
    ]
    assert eduky_names
    assert eduky_names != expected_names
    assert any(
        name in {"Founder Operator", "Student Success Lead", "Content Strategist"}
        for name in eduky_names
    )

    print("PASS dynamic persona validation")
    print(f"generic_personas: {', '.join(expected_names)}")
    print(f"generic_reaction_count: {len(session['turns'][0]['npc_reactions'])}")
    print(f"fallback_persona_count: {len(fallback)}")
    print(f"eduky_scenario_count: {len(eduky_scenarios)}")
    print(f"eduky_personas: {', '.join(eduky_names)}")


if __name__ == "__main__":
    main()
