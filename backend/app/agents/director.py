from typing import Any

from app.agents.npcs import normalize_personas
from app.grounding.local_knowledge import answer_with_citations
from app.scenarios.library import (
    scenario_to_runtime_seed,
    select_scenario as select_scenario_pack,
)


AUTO_DECISION_PLAN = [
    {
        "id": "DEC-RESTART-CHECKOUT",
        "label": "Restart checkout service",
        "description": "Restart checkout workers before resolving database writer uncertainty.",
        "competencies": ["SK-incident-triage"],
        "action_type": "restart_checkout",
    },
    {
        "id": "DEC-FREEZE-WRITES",
        "label": "Freeze writes and identify primary database writer",
        "description": "Pause risky write paths, confirm the primary writer, and protect order consistency.",
        "competencies": ["SK-incident-triage", "SK-database-recovery", "SK-escalation-judgment"],
        "action_type": "freeze_db_writes",
    },
    {
        "id": "DEC-ESCALATE-COMMAND",
        "label": "Escalate to database lead and incident command",
        "description": "Create a shared incident channel, assign owners, and communicate risk checkpoints.",
        "competencies": ["SK-communication", "SK-escalation-judgment"],
        "action_type": "escalate_incident_command",
    },
    {
        "id": "DEC-CORRELATE-SIGNALS",
        "label": "Correlate traces across checkout, orders, and database",
        "description": "Use observability evidence to validate whether writes and retries are stabilizing.",
        "competencies": ["SK-observability", "SK-incident-triage"],
        "action_type": "correlate_observability",
    },
    {
        "id": "DEC-GRADUAL-RESTORE",
        "label": "Restore traffic gradually after consistency checks",
        "description": "Reopen traffic in stages after database ownership and order integrity checks pass.",
        "competencies": ["SK-database-recovery", "SK-communication"],
        "action_type": "gradual_restore",
    },
]


DISTRACTOR_OPTIONS = [
    {
        "id": "DEC-IGNORE-DB",
        "label": "Ignore database symptoms",
        "description": "Treat the issue as a checkout-only outage and defer database investigation.",
        "competencies": ["SK-incident-triage"],
        "action_type": "ignore_database_symptoms",
    },
    {
        "id": "DEC-FAST-FAILOVER",
        "label": "Fail over database immediately",
        "description": "Force failover before confirming replication health or writer ownership.",
        "competencies": ["SK-database-recovery"],
        "action_type": "failover_without_validation",
    },
]


TURN_QUERIES = [
    "checkout outage database recovery split brain",
    "database recovery identify primary writer",
    "incident escalation stakeholder communication",
    "checkout observability orders database",
    "database recovery traffic restoration",
]


class ScenarioDirector:
    def select_scenario(self, role_id: str, scenario_seed: str | None = None) -> dict[str, Any]:
        try:
            return scenario_to_runtime_seed(
                select_scenario_pack(role_id=role_id, scenario_id=scenario_seed)
            )
        except FileNotFoundError as error:
            raise ValueError(
                "No scenario is configured for this role. Create a workspace scenario "
                "or enable the optional example pack."
            ) from error

    def start_session(self, role_id: str, scenario_seed: str | None = None) -> dict[str, Any]:
        scenario = self.select_scenario(role_id, scenario_seed)
        scenario["personas"] = normalize_personas(scenario)
        grounding_query = " ".join(
            scenario.get("knowledge_refs", [])
            or scenario.get("tags", [])
            or ["incident response operational recovery"]
        )
        intro = answer_with_citations(grounding_query, top_k=3)
        max_turns = len(scenario.get("runtime_turns", [])) or 5
        return {
            "session_id": f"SES-{role_id}-{scenario['id']}",
            "role_id": role_id,
            "scenario": {**scenario, "intro": intro["answer"], "citations": intro["citations"]},
            "turn_index": 0,
            "min_turns": max_turns,
            "max_turns": max_turns,
            "severity": 4,
            "impacted_systems": scenario["impacted_systems"],
            "history": [],
        }

    def build_turn_context(self, state: dict[str, Any]) -> dict[str, Any]:
        turn_index = state["turn_index"]
        runtime_turns = state["scenario"].get("runtime_turns", [])
        if runtime_turns:
            return self._build_library_turn_context(state, runtime_turns[turn_index])

        query = TURN_QUERIES[min(turn_index, len(TURN_QUERIES) - 1)]
        grounding = answer_with_citations(query, top_k=3)
        auto_decision = AUTO_DECISION_PLAN[min(turn_index, len(AUTO_DECISION_PLAN) - 1)]
        available_options = [auto_decision, *DISTRACTOR_OPTIONS]

        return {
            "turn_number": turn_index + 1,
            "scenario_id": state["scenario"]["id"],
            "severity": state["severity"],
            "affected_systems": state["impacted_systems"],
            "situation": self._build_situation(state, grounding["answer"]),
            "active_npcs": state["scenario"]["personas"],
            "available_options": available_options,
            "auto_decision": auto_decision,
            "citations": grounding["citations"],
        }

    def should_continue(self, state: dict[str, Any]) -> bool:
        return state["turn_index"] < state["max_turns"]

    def _build_situation(self, state: dict[str, Any], grounded_fact: str) -> str:
        return (
            f"Severity {state['severity']} incident across {', '.join(state['impacted_systems'])}. "
            f"{grounded_fact}"
        )

    def _build_library_turn_context(
        self,
        state: dict[str, Any],
        turn: dict[str, Any],
    ) -> dict[str, Any]:
        scenario = state["scenario"]
        query = " ".join(
            [
                *scenario.get("knowledge_refs", []),
                *scenario.get("tags", []),
                *turn.get("evaluation_focus", []),
            ]
        )
        grounding = answer_with_citations(query, top_k=3)
        options = turn["options"]
        return {
            "turn_number": state["turn_index"] + 1,
            "scenario_id": scenario["id"],
            "severity": state["severity"],
            "affected_systems": state["impacted_systems"],
            "situation": (
                f"Severity {state['severity']} across {', '.join(state['impacted_systems'])}. "
                f"{turn['situation']} {grounding['answer']}"
            ),
            "active_npcs": scenario["personas"],
            "available_options": options,
            "auto_decision": options[0],
            "citations": grounding["citations"],
        }
