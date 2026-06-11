from typing import Any


__all__ = [
    "get_scenario",
    "list_scenarios",
    "scenario_to_runtime_seed",
    "select_scenario",
    "validate_no_sensitive_content",
    "validate_scenario_pack",
]

_LIBRARY_EXPORTS = {
    "get_scenario",
    "list_scenarios",
    "scenario_to_runtime_seed",
    "select_scenario",
}
_VALIDATOR_EXPORTS = {
    "validate_no_sensitive_content",
    "validate_scenario_pack",
}


def __getattr__(name: str) -> Any:
    if name in _LIBRARY_EXPORTS:
        from app.scenarios import library

        return getattr(library, name)
    if name in _VALIDATOR_EXPORTS:
        from app.scenarios import validators

        return getattr(validators, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
