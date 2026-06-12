# CRISOL Documentation Assets

The screenshots in `screenshots/` are captured from the public production
frontend and backend. They contain only sanitized training data.

| Asset | Contents |
| --- | --- |
| `00-command-center.png` | Configured Creator Operations command center. |
| `01-empty-workspace.png` | Production empty-workspace state captured before applying a template. |
| `02-workspace-setup.png` | Organization, roles, skills, knowledge, profiles, and templates. |
| `03-scenario-studio.png` | Scenario library and guided scenario authoring. |
| `04-evaluation-room.png` | Completed sanitized evaluation with personas, consequences, and evidence. |
| `05-results-center.png` | Competence report, coach plan, manager insights, and replay. |
| `06-tools-readiness.png` | Health, MCP tools, telemetry, and release boundaries. |
| `07-grounding-status.png` | Readable rendering of the live grounding status response. |
| `backend-health.json` | Exact public backend health response. |
| `grounding-status.json` | Exact public grounding status response. |
| `azure-resource-group-placeholder.md` | Manual Azure Portal capture instructions. |

## Refresh screenshots

From the repository root:

```powershell
npm install --prefix tools
npm exec --prefix tools playwright install chromium
npm run --prefix tools capture:screenshots
```

Optional endpoint overrides:

```powershell
$env:CRISOL_FRONTEND_URL="https://<frontend-host>"
$env:CRISOL_BACKEND_URL="https://<backend-host>"
npm run --prefix tools capture:screenshots
```

The capture script:

1. Saves the backend health and grounding JSON.
2. Captures the empty workspace if production is empty.
3. Applies only Creator Operations Readiness when an empty workspace needs a
   configured capture.
4. Runs one sanitized synthetic evaluation.
5. Captures every primary product section.
6. Preserves an existing `01-empty-workspace.png` after the workspace becomes
   configured.

Review every image before publication. Refresh assets after material UI,
navigation, Azure status, or scenario changes.

## Manual Azure Portal asset

Follow `screenshots/azure-resource-group-placeholder.md`. Do not expose
subscription IDs, tenant IDs, access keys, costs, identities, or private tags.
