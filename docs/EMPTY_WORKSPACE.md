# Empty Workspace Mode

CRISOL starts with an empty local workspace. No example scenarios, knowledge documents, roles, skills, or evaluated profiles are active until a user configures them.

## Initialize

```powershell
cd D:\hackathons\crisol\backend
python -m app.workspace.setup --empty
```

This command:

- Creates the workspace storage directories.
- Removes generated workspace content.
- Clears generated sessions, audio, and telemetry.
- Disables the optional example pack.
- Preserves all source examples under `backend/app/data/examples`.

Check the resulting state:

```powershell
python -m app.workspace.setup --status
```

The status should report zero scenarios, knowledge documents, roles, skills, and profiles with `is_empty` set to `true`.

## Browser Behavior

An empty workspace shows the setup panel with these actions:

- **Start Empty** opens Role & Skill Builder, Knowledge Editor, Scenario Editor, and Profile Setup.
- **Digital Education Operator** creates a generic digital education workspace.
- **Customer Support Operations** creates a generic support and service recovery workspace.
- **Finance Controls** creates a generic reconciliation and controls workspace.
- **Apply Eduky Template** creates the optional sanitized first-customer workspace.
- **Enable Example Pack** exposes the optional product examples without copying them into workspace storage.

Run and Play Live Simulation remain disabled until a scenario is created or an example pack is enabled.

The incident room displays `No personas loaded` until a selected scenario supplies personas or CRISOL derives a generic fallback roster.

## Storage Boundary

Generated workspace content is written only under:

```text
backend/app/data/workspace/
```

These generated files are ignored by Git. Source example packs remain versioned under:

```text
backend/app/data/examples/
```

Do not place credentials, production telemetry, customer records, or personal data in workspace content.
