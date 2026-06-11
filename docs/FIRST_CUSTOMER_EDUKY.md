# First Customer Workspace: Eduky

Eduky is an optional sanitized setup template for a fictional digital education operations workspace. It is not loaded by default and is not required for generic CRISOL operation.

## Initialize Empty

```powershell
cd D:\hackathons\crisol\backend
python -m app.workspace.setup --empty
python -m app.workspace.setup --status
```

## Apply The Template

```powershell
python -m app.workspace.setup --eduky-template
python -m app.workspace.setup --status
```

The resulting workspace uses organization `Eduky`, industry `Digital Education`, and keeps the optional example pack disabled.

The same template is available through `POST /workspace/apply-template/template-eduky`. The `/workspace/apply-template/eduky` route remains as a compatibility alias.

## Configured Roles

- `ROLE-FOUNDER-OPERATOR`
- `ROLE-STUDENT-SUCCESS`
- `ROLE-LAUNCH-MANAGER`
- `ROLE-CONTENT-STRATEGIST`
- `ROLE-AUTOMATION-SPECIALIST`

## Configured Skills

- `SK-prioritization-under-pressure`
- `SK-customer-communication`
- `SK-escalation-judgment`
- `SK-revenue-risk-control`
- `SK-launch-decision-making`
- `SK-operational-diagnosis`
- `SK-automation-thinking`
- `SK-brand-protection`
- `SK-student-success`
- `SK-data-informed-decision`

## Configured Knowledge

- `eduky_support_policy.md`
- `eduky_refund_handling_guide.md`
- `eduky_launch_playbook.md`
- `eduky_student_success_playbook.md`
- `eduky_content_risk_playbook.md`
- `eduky_brand_voice_guide.md`

## Configured Scenarios

- `SCN-EDUKY-SUPPORT-001`: Student refund escalation under public pressure
- `SCN-EDUKY-LAUNCH-001`: Launch day checkout and access failure
- `SCN-EDUKY-CONTENT-001`: Viral content backlash response

Each scenario contains five turns, uses fictional operational conditions, and is classified as sanitized training data.

## Founder Operator Evaluation

The configured profile is `PROFILE-FOUNDER-001`, displayed as Founder Operator and assigned to `ROLE-FOUNDER-OPERATOR`.

The profile context covers decisions across student support, launches, content, automation, and revenue risk. Scenario options link evidence to configured skills. The completed session produces a competence report, coaching plan, timeline, revenue-risk signals, and manager readiness aggregates. The profile label appears in the session summary when its role matches the selected scenario.

## Live Product Walkthrough

1. Start from the empty workspace screen.
2. Apply the Eduky template.
3. Confirm workspace counts: 3 scenarios, 6 knowledge documents, 5 roles, 10 skills, and 1 profile.
4. Open each studio to show editable sanitized configuration.
5. Select the launch-day scenario and confirm its source is `workspace`.
6. Start Play Live Simulation and show synchronized NPC pressure, timeline changes, and revenue exposure.
7. Review the cited competence report and Founder Operator profile in the session summary.
8. Use Time-Travel Replay on a completed decision.
9. Show the MCP Tool Preview and Azure Speech status.
10. Return to workspace status and confirm examples remain disabled.
