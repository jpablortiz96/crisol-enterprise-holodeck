# Product Walkthrough

Command Center exposes a seven-step **Workspace Walkthrough** based on current backend state:

1. Configure workspace.
2. Add roles and skills.
3. Add knowledge.
4. Create scenarios.
5. Create evaluated profile.
6. Run evaluation.
7. Review results.

The backend contract is available at:

```text
GET /workspace/walkthrough
```

Each step is `complete` or `pending`. `next_recommended_action` points to the first incomplete step.

## Empty Workspace Flow

1. Initialize the empty workspace.
2. Open **Workspace Setup**.
3. Configure content manually or apply an optional template.
4. Return to **Command Center** to check progress.

## Creator Operations Flow

1. Apply **Creator Operations Readiness** in Workspace Setup.
2. Confirm the three Creator scenarios in Scenario Studio or Evaluation Room.
3. Run the launch-day scenario.
4. Open Results Center.
5. Return to Command Center and confirm the evaluation and results steps are complete.

## Operational Notes

- Templates are never applied automatically.
- Example scenarios remain disabled unless explicitly enabled.
- Personas are supplied by each scenario and survive package export and import.
- Workspace packages use sanitized training data only.
