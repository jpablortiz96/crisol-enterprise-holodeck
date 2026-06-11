# Product Scenarios

CRISOL scenario packs are JSON documents stored in one of two locations:

- Generated customer scenarios: `backend/app/data/workspace/scenario_packs`
- Versioned optional examples: `backend/app/data/examples/scenario_packs`

The product loads workspace scenarios first. Example scenarios are included only when `load_examples` is enabled. Packs use fictional identifiers and sanitized training data.

## Authoring Workflow

1. Start from the Scenario Studio starter JSON or load a scenario template.
2. Assign a unique fictional `SCN-*` identifier.
3. Use only system identifiers defined by the local ontology.
4. Define scenario-specific personas when needed, plus operational turns, options, expected outcomes, success criteria, and failure modes.
5. Reference approved local knowledge identifiers.
6. Save through Scenario Studio or `POST /workspace/scenarios`.
7. Run `python -m app.scenarios.importer` to validate the versioned example pack when examples change.
8. Review the workspace scenario in Scenario Library before use.

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
      "persona": "Customer Recovery Lead",
      "role": "Customer communication owner",
      "communication_style": "direct",
      "pressure_profile": "high",
      "voice_style": "urgent",
      "avatar_style": "customer"
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

`personas` is optional. When absent or empty, CRISOL creates a deterministic generic roster from the scenario role, industry, tags, and difficulty. Explicit personas are normalized so every reaction includes `persona`, `role`, `communication_style`, `pressure_profile`, `voice_style`, and `avatar_style`.

Voice selection is based on `voice_style` and pressure rather than persona names. Supported default styles are `calm`, `urgent`, `analytical`, and `supportive`.

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
