import json
import re
from typing import Any


REQUIRED_FIELDS = {
    "scenario_id",
    "title",
    "industry",
    "role_id",
    "difficulty",
    "estimated_minutes",
    "data_classification",
    "business_context",
    "systems",
    "initial_stakes",
    "turns",
    "success_criteria",
    "failure_modes",
    "knowledge_refs",
    "tags",
}
OPTION_FIELDS = {
    "id",
    "label",
    "description",
    "action_type",
    "competencies",
    "risk_effect",
    "expected_outcome",
}
RISK_EFFECTS = {"increase", "decrease", "neutral"}
BANNED_PHRASES = {
    "confidential customer",
    "real client",
    "production password",
    "secret key",
}
EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
DOMAIN_PATTERN = re.compile(
    r"\b(?:https?://|www\.)[^\s]+|\b[a-z0-9-]+\.(?:com|net|org|io|co|gov|edu)\b",
    re.IGNORECASE,
)
PHONE_PATTERN = re.compile(r"(?<!\w)(?:\+?\d[\d .()-]{8,}\d)(?!\w)")
TOKEN_PATTERN = re.compile(
    r"\b(?:api[_-]?key|token|password|secret)\s*[:=]\s*[A-Za-z0-9_\-./+=]{8,}\b",
    re.IGNORECASE,
)
CARD_PATTERN = re.compile(r"\b(?:\d[ -]*?){13,19}\b")


def validate_scenario_pack(pack: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_FIELDS - set(pack))
    if missing:
        errors.append(f"Missing required fields: {', '.join(missing)}")
        return errors

    if not re.fullmatch(r"SCN-[A-Z0-9-]+", str(pack["scenario_id"])):
        errors.append("scenario_id must use the SCN-* fictional identifier format.")
    if pack["data_classification"] != "sanitized-training":
        errors.append("data_classification must be sanitized-training.")
    if not isinstance(pack["estimated_minutes"], int) or pack["estimated_minutes"] < 1:
        errors.append("estimated_minutes must be a positive integer.")
    if not isinstance(pack["systems"], list) or not pack["systems"]:
        errors.append("systems must be a non-empty list.")
    if "personas" in pack and not isinstance(pack["personas"], list):
        errors.append("personas must be a list when provided.")
    if not isinstance(pack["turns"], list) or not pack["turns"]:
        errors.append("turns must be a non-empty list.")
        return errors

    turn_ids = set()
    for index, turn in enumerate(pack["turns"], start=1):
        location = f"turn {index}"
        turn_id = turn.get("turn_id")
        if not turn_id:
            errors.append(f"{location} is missing turn_id.")
        elif turn_id in turn_ids:
            errors.append(f"Duplicate turn_id: {turn_id}.")
        else:
            turn_ids.add(turn_id)
        if not turn.get("situation"):
            errors.append(f"{location} is missing situation.")
        if not turn.get("evaluation_focus"):
            errors.append(f"{location} must include evaluation_focus.")
        options = turn.get("options")
        if not isinstance(options, list) or not options:
            errors.append(f"{location} must include at least one option.")
            continue
        option_ids = set()
        for option in options:
            option_missing = sorted(OPTION_FIELDS - set(option))
            if option_missing:
                errors.append(
                    f"{location} option is missing fields: {', '.join(option_missing)}."
                )
                continue
            if option["id"] in option_ids:
                errors.append(f"{location} has duplicate option id {option['id']}.")
            option_ids.add(option["id"])
            if option["risk_effect"] not in RISK_EFFECTS:
                errors.append(
                    f"{location} option {option['id']} has invalid risk_effect."
                )
    return errors


def validate_no_sensitive_content(pack: dict[str, Any]) -> list[str]:
    serialized = json.dumps(pack, ensure_ascii=True)
    lowered = serialized.lower()
    errors = []
    for phrase in sorted(BANNED_PHRASES):
        if phrase in lowered:
            errors.append(f"Sensitive phrase detected: {phrase}.")
    patterns = (
        ("email-like value", EMAIL_PATTERN),
        ("public domain or URL", DOMAIN_PATTERN),
        ("phone-like value", PHONE_PATTERN),
        ("token-like value", TOKEN_PATTERN),
        ("payment-card-like value", CARD_PATTERN),
    )
    for label, pattern in patterns:
        if pattern.search(serialized):
            errors.append(f"Potential {label} detected.")
    return errors
