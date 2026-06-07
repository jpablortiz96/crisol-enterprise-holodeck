# Product Scenarios

CRISOL scenario packs are manually authored JSON documents stored under `backend/app/data/scenario_packs`. Packs use fictional identifiers and sanitized training data.

## Authoring Workflow

1. Copy an existing pack.
2. Assign a unique fictional `SCN-*` identifier.
3. Use only system identifiers defined by the local ontology.
4. Define personas, five operational turns, options, expected outcomes, success criteria, and failure modes.
5. Reference approved local knowledge identifiers.
6. Run `python -m app.scenarios.importer`.
7. Review the scenario in the Scenario Library before distribution.

## Schema

```json
{
  "scenario_id": "SCN-ROLE-001",
  "title": "Sanitized operational scenario",
  "industry": "Fictional industry context",
  "role_id": "ROLE-SRE",
  "difficulty": "standard",
  "estimated_minutes": 8,
  "data_classification": "sanitized-training",
  "business_context": "Fictional and sanitized context.",
  "systems": ["SVC-checkout"],
  "initial_stakes": "Operational stakes without real customer details.",
  "personas": [
    {
      "persona": "VP Operations",
      "role": "Executive command",
      "communication_style": "urgent",
      "pressure_profile": "high"
    }
  ],
  "turns": [
    {
      "turn_id": "T1",
      "situation": "A sanitized operational condition.",
      "options": [
        {
          "id": "OPT-A",
          "label": "Evidence-based action",
          "description": "Action description.",
          "action_type": "custom_action",
          "competencies": ["SK-incident-triage"],
          "risk_effect": "decrease",
          "expected_outcome": "Modeled consequence."
        }
      ],
      "evaluation_focus": ["SK-incident-triage"]
    }
  ],
  "success_criteria": ["Evidence-based containment"],
  "failure_modes": ["Unvalidated state change"],
  "knowledge_refs": ["RUNBOOK-INCIDENT-ESCALATION"],
  "tags": ["operations"]
}
```

## Risk Effects

- `increase`: raises modeled severity and can expand affected dependencies.
- `decrease`: lowers modeled severity and can reduce affected systems.
- `neutral`: keeps modeled severity stable.

Known action types can use specialized consequence behavior. Other action types use `risk_effect`, `expected_outcome`, competencies, scenario systems, and knowledge references.

## Sanitization Rules

- Do not use real organizations, customers, employees, emails, phone numbers, domains, account numbers, incident identifiers, or production telemetry.
- Do not include credentials, tokens, passwords, keys, connection strings, or internal URLs.
- Do not paste confidential source material.
- Keep every identifier fictional and every business context general enough for training use.
- Treat importer success as a baseline check, followed by human review.
