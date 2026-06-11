from typing import Any


PERSONA_FIELDS = (
    "persona",
    "role",
    "communication_style",
    "pressure_profile",
    "voice_style",
    "avatar_style",
)
PRESSURE_OFFSETS = {
    "low": -1,
    "medium": 0,
    "high": 1,
    "critical": 2,
}


def normalize_personas(scenario: dict[str, Any]) -> list[dict[str, str]]:
    raw_personas = scenario.get("personas")
    if not isinstance(raw_personas, list) or not raw_personas:
        return fallback_personas_for_scenario(scenario)

    normalized = []
    for index, raw_persona in enumerate(raw_personas, start=1):
        if isinstance(raw_persona, str):
            raw_persona = {"persona": raw_persona}
        if not isinstance(raw_persona, dict):
            continue
        name = str(raw_persona.get("persona", "")).strip()
        if not name:
            continue
        communication_style = (
            str(raw_persona.get("communication_style", "")).strip()
            or "direct and measured"
        )
        pressure_profile = _pressure_profile(
            str(raw_persona.get("pressure_profile", "")).strip()
        )
        normalized.append(
            {
                "persona": name,
                "role": (
                    str(raw_persona.get("role", "")).strip()
                    or f"Scenario stakeholder {index}"
                ),
                "communication_style": communication_style,
                "pressure_profile": pressure_profile,
                "voice_style": (
                    str(raw_persona.get("voice_style", "")).strip()
                    or _voice_style(communication_style, pressure_profile)
                ),
                "avatar_style": (
                    str(raw_persona.get("avatar_style", "")).strip()
                    or _avatar_style(index)
                ),
            }
        )

    return normalized or fallback_personas_for_scenario(scenario)


def fallback_personas_for_scenario(scenario: dict[str, Any]) -> list[dict[str, str]]:
    role_label = _title_from_identifier(str(scenario.get("role_id", "ROLE-OPERATOR")))
    industry = str(scenario.get("industry", "")).strip() or "Business Operations"
    tags = {
        str(tag).strip().lower()
        for tag in scenario.get("tags", [])
        if str(tag).strip()
    }
    difficulty = str(scenario.get("difficulty", "standard")).strip().lower()
    pressure = "high" if difficulty in {"advanced", "hard", "critical"} else "medium"

    personas = [
        {
            "persona": f"{role_label} Counterpart",
            "role": f"{role_label} decision counterpart",
            "communication_style": "direct and evidence-focused",
            "pressure_profile": pressure,
            "voice_style": "analytical",
            "avatar_style": "holographic-operator",
        },
        {
            "persona": f"{industry} Stakeholder",
            "role": "Business impact owner",
            "communication_style": "calm but outcome-focused",
            "pressure_profile": "medium",
            "voice_style": "calm",
            "avatar_style": "holographic-stakeholder",
        },
    ]

    if tags & {"customer", "customer-operations", "support", "retention", "student-success"}:
        personas.append(
            {
                "persona": "Customer Experience Lead",
                "role": "Customer impact and communication owner",
                "communication_style": "supportive and urgent",
                "pressure_profile": pressure,
                "voice_style": "supportive",
                "avatar_style": "holographic-customer",
            }
        )
    elif tags & {"security", "incident-response", "phishing", "risk"}:
        personas.append(
            {
                "persona": "Risk Response Lead",
                "role": "Risk containment owner",
                "communication_style": "analytical and urgent",
                "pressure_profile": pressure,
                "voice_style": "urgent",
                "avatar_style": "holographic-risk",
            }
        )
    elif tags & {"finance", "reconciliation", "controls", "revenue-risk"}:
        personas.append(
            {
                "persona": "Controls Lead",
                "role": "Control integrity owner",
                "communication_style": "precise and analytical",
                "pressure_profile": pressure,
                "voice_style": "analytical",
                "avatar_style": "holographic-controls",
            }
        )
    else:
        personas.append(
            {
                "persona": "Service Delivery Lead",
                "role": "Operational continuity owner",
                "communication_style": "focused and practical",
                "pressure_profile": pressure,
                "voice_style": "calm",
                "avatar_style": "holographic-service",
            }
        )

    return personas


def generate_npc_reactions(
    turn_context: dict[str, Any],
    decision: dict[str, Any],
    consequence: dict[str, Any],
) -> list[dict[str, Any]]:
    severity = int(consequence["new_severity"])
    delta = int(consequence["severity_delta"])
    reactions = []

    for persona in turn_context["active_npcs"]:
        pressure_level = max(
            1,
            min(
                5,
                severity + PRESSURE_OFFSETS.get(persona["pressure_profile"], 0),
            ),
        )
        reactions.append(
            {
                **{field: persona[field] for field in PERSONA_FIELDS},
                "tone": _tone(persona, delta, severity),
                "message": _message(persona, decision, consequence),
                "pressure_level": pressure_level,
            }
        )

    return reactions


def _tone(persona: dict[str, str], delta: int, severity: int) -> str:
    style = persona["communication_style"].lower()
    if delta > 0 or severity >= 5:
        return "urgent"
    if "analytical" in style or "technical" in style or "precise" in style:
        return "analytical"
    if delta < 0:
        return "focused"
    if "support" in style or "empathetic" in style:
        return "supportive"
    return "concerned"


def _message(
    persona: dict[str, str],
    decision: dict[str, Any],
    consequence: dict[str, Any],
) -> str:
    role = persona["role"]
    style = persona["communication_style"]
    action = decision.get("label") or decision.get("description") or "The selected action"
    affected = ", ".join(consequence["affected_systems"][:3]) or "the active workflow"
    outcome = consequence.get("world_delta", "The scenario state has changed.")
    delta = int(consequence["severity_delta"])

    if delta > 0:
        return (
            f"As {role}, I see risk increasing across {affected}. "
            f"{action} needs a safer boundary and a named next checkpoint. "
            f"My response is {style}."
        )
    if delta < 0:
        return (
            f"As {role}, I can support this direction. {outcome} "
            f"Keep the evidence, owner, and next checkpoint explicit."
        )
    return (
        f"As {role}, I need clearer evidence before the next decision. "
        f"{outcome} Confirm what changes for {affected} and who owns the checkpoint."
    )


def _pressure_profile(value: str) -> str:
    normalized = value.lower()
    return normalized if normalized in PRESSURE_OFFSETS else "medium"


def _voice_style(communication_style: str, pressure_profile: str) -> str:
    style = communication_style.lower()
    if "support" in style or "empathetic" in style:
        return "supportive"
    if "analytical" in style or "technical" in style or "precise" in style:
        return "analytical"
    if "urgent" in style or pressure_profile in {"high", "critical"}:
        return "urgent"
    return "calm"


def _avatar_style(index: int) -> str:
    return (
        "holographic-operator",
        "holographic-stakeholder",
        "holographic-specialist",
        "holographic-observer",
    )[(index - 1) % 4]


def _title_from_identifier(value: str) -> str:
    normalized = value.removeprefix("ROLE-").replace("-", " ").replace("_", " ")
    return normalized.title() or "Operator"
