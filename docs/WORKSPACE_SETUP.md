# Workspace Setup

CRISOL supports an empty workspace, generic workspace packs, optional examples, and an optional sanitized Eduky customer pack.

## Command Line

Run commands from `backend`:

```powershell
python -m app.workspace.setup --empty
python -m app.workspace.setup --with-examples
python -m app.workspace.setup --status
python -m app.workspace.setup --eduky-template
```

### Empty

`--empty` resets generated workspace content and runtime artifacts. It does not delete source examples.

### Optional Examples

`--with-examples` sets `load_examples` to `true`. Example scenarios and knowledge become available at runtime while remaining separate from customer workspace files.

Use the API or browser toggle to disable them:

```text
POST /workspace/disable-examples
```

### Eduky Template

`--eduky-template` is a compatibility command for the optional Eduky customer pack. It resets the generated workspace and writes sanitized roles, skills, knowledge, profiles, and scenario packs. Examples remain disabled.

### Generic Workspace Templates

The browser and API expose these workspace templates:

- `template-empty`: Start Empty
- `template-digital-education`: Digital Education Operator
- `template-customer-support`: Customer Support Operations
- `template-finance-controls`: Finance Controls
- `template-eduky`: optional Eduky Customer Pack

The generic templates leave `organization_name` blank. Use organization configuration to set the customer-facing workspace identity.

Scenario Studio also exposes seven generic scenario starters:

- Customer escalation and service recovery
- Launch or release failure
- Finance reconciliation control
- Operations incident control
- Strategic sales objection
- Data quality incident
- Security response coordination

## Browser Setup

1. Start the backend and frontend.
2. Open `http://localhost:3000`.
3. Choose Start Empty, a generic workspace template, the optional Eduky customer pack, or Enable Example Pack.
4. Set organization name, industry, and workspace name in Workspace Status.
5. Use the studios to add or update workspace content.
6. Select a scenario in Scenario Library.
7. Run the scenario or start synchronized live playback.

## Workspace API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/workspace/status` | Return workspace configuration and counts |
| POST | `/workspace/initialize-empty` | Reset generated workspace and runtime state |
| POST | `/workspace/enable-examples` | Enable optional source examples |
| POST | `/workspace/disable-examples` | Disable optional source examples |
| POST | `/workspace/apply-template/{template_id}` | Apply an empty, generic, or optional customer template |
| POST | `/workspace/apply-template/eduky` | Compatibility alias for the optional Eduky customer pack |
| POST | `/workspace/configure-organization` | Set organization name, industry, and workspace name |
| GET/POST | `/workspace/knowledge` | List or save knowledge documents |
| GET/POST | `/workspace/roles` | List or save roles |
| GET/POST | `/workspace/skills` | List or save skills |
| GET/POST | `/workspace/profiles` | List or save evaluated profiles |
| GET/POST | `/workspace/scenarios` | List or save workspace scenarios |
| GET | `/workspace/templates` | List workspace templates |
| GET | `/workspace/scenario-templates` | List the seven generic scenario starters |

All saved content passes sensitive-content validation and receives the `sanitized-training` classification.
