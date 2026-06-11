"use client";

import {
  BarChart3,
  BookOpenCheck,
  BriefcaseBusiness,
  Building2,
  CheckCircle2,
  Circle,
  Database,
  FilePlus2,
  Layers3,
  ListChecks,
  Play,
  ShieldCheck,
  UserRoundCheck,
  Wrench,
} from "lucide-react";
import { useWarRoomStore } from "@/store/warRoomStore";

export function CommandCenterPage() {
  const {
    workspaceStatus,
    workspaceWalkthrough,
    latestReport,
    isWorkspaceSaving,
    startEmptyWorkspace,
    setExamplesEnabled,
    goToSetup,
    goToScenarioStudio,
    goToEvaluation,
    goToResults,
  } = useWarRoomStore();

  if (!workspaceStatus) {
    return <div className="page-loading">Loading command center...</div>;
  }

  const checks = [
    ["Organization configured", Boolean(workspaceStatus.workspace.organization_name), Building2],
    ["Roles configured", workspaceStatus.role_count > 0, BriefcaseBusiness],
    ["Skills configured", workspaceStatus.skill_count > 0, Wrench],
    ["Knowledge documents added", workspaceStatus.knowledge_count > 0, BookOpenCheck],
    ["Scenarios configured", workspaceStatus.scenario_count > 0, Layers3],
    ["Evaluated profiles configured", workspaceStatus.profile_count > 0, UserRoundCheck],
  ] as const;
  const completed = checks.filter(([, ready]) => ready).length;

  return (
    <section className="product-page">
      <PageHeader
        eyebrow="Training environment"
        title={workspaceStatus.workspace.workspace_name}
        description="Configure readiness programs, run scenario-driven evaluations, and review cited evidence without affecting production systems."
      />

      {workspaceStatus.is_empty && !workspaceStatus.load_examples && (
        <section className="command-empty-state">
          <div>
            <p className="panel-kicker">Workspace starting point</p>
            <h2>Your CRISOL workspace is empty.</h2>
            <p>
              Start by configuring your organization, roles, knowledge, scenarios, and evaluated profiles.
            </p>
          </div>
          <div className="command-empty-actions">
            <button className="control-button control-primary" disabled={isWorkspaceSaving} onClick={() => void startEmptyWorkspace()}>
              <FilePlus2 className="h-4 w-4" /> Start Empty
            </button>
            <button className="control-button control-secondary" onClick={goToSetup}>
              <Layers3 className="h-4 w-4" /> Apply Template
            </button>
            <button className="control-button control-secondary" disabled={isWorkspaceSaving} onClick={() => void setExamplesEnabled(true)}>
              <BookOpenCheck className="h-4 w-4" /> Enable Example Pack
            </button>
          </div>
        </section>
      )}

      <div className="command-metric-grid">
        <CommandMetric label="Scenarios" value={workspaceStatus.scenario_count} icon={Layers3} />
        <CommandMetric label="Profiles" value={workspaceStatus.profile_count} icon={UserRoundCheck} />
        <CommandMetric label="Knowledge" value={workspaceStatus.knowledge_count} icon={Database} />
        <CommandMetric
          label="Latest score"
          value={latestReport ? latestReport.overall_score.toFixed(1) : "Pending"}
          icon={BarChart3}
        />
      </div>

      {workspaceWalkthrough && (
        <section className="war-panel workspace-walkthrough-panel">
          <div className="panel-header">
            <div>
              <p className="panel-kicker">Guided setup</p>
              <h2 className="panel-title">Workspace Walkthrough</h2>
            </div>
            <ListChecks className="h-5 w-5 text-cyan-300" />
          </div>
          <div className="workspace-walkthrough-steps">
            {workspaceWalkthrough.steps.map((step) => (
              <div
                key={step.step}
                className={
                  step.status === "complete"
                    ? "workspace-walkthrough-step workspace-walkthrough-step-complete"
                    : "workspace-walkthrough-step"
                }
              >
                <span>{step.step}</span>
                <strong>{step.title}</strong>
                {step.status === "complete"
                  ? <CheckCircle2 className="h-4 w-4" />
                  : <Circle className="h-4 w-4" />}
              </div>
            ))}
          </div>
          <div className="workspace-walkthrough-next">
            <span>Next recommended action</span>
            <strong>{workspaceWalkthrough.next_recommended_action}</strong>
          </div>
        </section>
      )}

      <div className="command-layout">
        <section className="war-panel command-readiness-panel">
          <div className="panel-header">
            <div>
              <p className="panel-kicker">Workspace readiness</p>
              <h2 className="panel-title">{completed} of {checks.length} configured</h2>
            </div>
            <ShieldCheck className="h-5 w-5 text-emerald-300" />
          </div>
          <div className="readiness-progress"><span style={{ width: `${(completed / checks.length) * 100}%` }} /></div>
          <div className="command-checklist">
            {checks.map(([label, ready, Icon]) => (
              <div key={label} className={ready ? "command-check command-check-ready" : "command-check"}>
                <Icon className="h-4 w-4" />
                <span>{label}</span>
                {ready ? <CheckCircle2 className="h-4 w-4" /> : <Circle className="h-4 w-4" />}
              </div>
            ))}
          </div>
        </section>

        <section className="quick-action-grid">
          <QuickAction title="Configure Workspace" description="Set organization, roles, skills, knowledge, and profiles." icon={Building2} onClick={goToSetup} />
          <QuickAction title="Create Scenario" description="Build a guided scenario with dynamic personas and decisions." icon={BriefcaseBusiness} onClick={goToScenarioStudio} />
          <QuickAction title="Evaluate Candidate" description="Run a focused live or one-shot evaluation." icon={Play} onClick={goToEvaluation} />
          <QuickAction title="View Results" description="Review competence evidence, coaching, and branch comparisons." icon={BarChart3} onClick={goToResults} />
        </section>
      </div>
    </section>
  );
}

function PageHeader({ eyebrow, title, description }: { eyebrow: string; title: string; description: string }) {
  return (
    <header className="page-header">
      <p>{eyebrow}</p>
      <h2>{title}</h2>
      <span>{description}</span>
    </header>
  );
}

function CommandMetric({ label, value, icon: Icon }: { label: string; value: string | number; icon: typeof Layers3 }) {
  return (
    <div className="command-metric-card">
      <Icon className="h-5 w-5" />
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function QuickAction({
  title,
  description,
  icon: Icon,
  onClick,
}: {
  title: string;
  description: string;
  icon: typeof Building2;
  onClick: () => void;
}) {
  return (
    <button type="button" className="quick-action-card" onClick={onClick}>
      <Icon className="h-5 w-5" />
      <span><strong>{title}</strong><small>{description}</small></span>
    </button>
  );
}
