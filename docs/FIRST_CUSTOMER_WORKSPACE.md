# First Customer Workspace

CRISOL starts with an empty, generic workspace. The optional Creator Operations Readiness template provides a sanitized starting point for digital education, creator, and online training operations.

## Start Empty

From `backend`:

```powershell
python -m app.workspace.setup --empty
python -m app.workspace.setup --status
```

The empty workspace has no roles, skills, profiles, knowledge documents, or scenarios. Examples remain disabled.

## Apply Creator Operations Readiness

Use the setup command:

```powershell
python -m app.workspace.setup --creator-operations-template
```

Or call the API while the backend is running:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/workspace/apply-template/creator-operations
```

In the browser, open **Workspace Setup** and select **Creator Operations Readiness**. Applying the template replaces generated workspace content and does not enable examples.

The pack includes:

- Five operational roles.
- Ten evaluated skills.
- One fictional Founder Operator profile.
- Six sanitized policy and playbook documents.
- Three scenarios covering launch failure, refund escalation, and content backlash.

## Configure Manually

Use **Workspace Setup** to enter the workspace name, organization, and industry, then add roles, skills, knowledge, and an evaluated profile. Use **Scenario Studio** to create a scenario and its role-specific personas and decisions.

Only sanitized or synthetic training content belongs in a workspace. Do not enter credentials, personal data, customer records, payment data, or confidential incidents.

## Run The First Evaluation

1. Open **Evaluation Room**.
2. Select `Launch day checkout and access failure`.
3. Select the Founder Operator profile.
4. Run the one-shot evaluation or start live playback.
5. Confirm the scenario shows Launch Coordinator, Student Success Lead, Payment Operations Analyst, and Brand Communications Lead.

## Review Results

Open **Results Center** after the run. Review the competence score, cited evidence, coaching plan, decision timeline, and available branch comparison.

The **Workspace Walkthrough** in Command Center reports setup progress and the next recommended action.
