from typing import Any


def generate_npc_reactions(
    turn_context: dict[str, Any],
    decision: dict[str, Any],
    consequence: dict[str, Any],
) -> list[dict[str, Any]]:
    severity = consequence["new_severity"]
    delta = consequence["severity_delta"]
    action_type = decision.get("action_type", "")
    reactions = []

    for persona in turn_context["active_npcs"]:
        reactions.append(
            {
                "persona": persona,
                "tone": _tone(persona, delta, severity),
                "message": _message(persona, action_type, consequence),
                "pressure_level": max(1, min(5, severity + (1 if persona == "VP Operations" else 0))),
            }
        )

    return reactions


def _tone(persona: str, delta: int, severity: int) -> str:
    if delta > 0 or severity >= 5:
        return "urgent"
    if persona == "Database Lead":
        return "technical"
    if delta < 0:
        return "focused"
    return "concerned"


def _message(persona: str, action_type: str, consequence: dict[str, Any]) -> str:
    affected = ", ".join(consequence["affected_systems"][:4])

    if persona == "VP Operations":
        if action_type == "restart_checkout":
            return "Restarting before database ownership is clear increases business exposure. I need a safer recovery path now."
        if consequence["severity_delta"] < 0:
            return "The risk is moving in the right direction. Keep the update cadence tight and quantify remaining exposure."
        return f"Current exposure still touches {affected}. State the next decision point clearly."

    if persona == "Product Manager":
        if action_type == "gradual_restore":
            return "A staged restore gives us a customer-safe message. Confirm what user paths remain blocked."
        if consequence["severity_delta"] > 0:
            return "The customer impact story is getting worse. We need a clear explanation before the next status update."
        return "I can work with this plan if we keep support informed and avoid overpromising recovery time."

    if persona == "Database Lead":
        if action_type == "freeze_db_writes":
            return "Freezing writes is the right control. I will validate the primary writer and replication health."
        if action_type in {"restart_checkout", "ignore_database_symptoms", "failover_without_validation"}:
            return "That path risks data inconsistency. We need writer ownership evidence before more traffic changes."
        return "I need traces, write conflict counts, and replication status to confirm the recovery path."

    if action_type == "escalate_incident_command":
        return "Support can align customer messaging once owners, checkpoints, and known impact are explicit."
    if consequence["severity_delta"] > 0:
        return "Tickets are rising and the explanation is not stable yet. Give us the current customer-facing statement."
    return "Support can hold the line if the next update includes impact, action owner, and checkpoint time."
