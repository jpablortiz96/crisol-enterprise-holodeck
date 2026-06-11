"use client";

import { CheckCircle2 } from "lucide-react";
import { WorkspaceStatusPanel } from "@/components/WorkspaceStatusPanel";
import { WorkspaceOnboarding } from "@/components/WorkspaceOnboarding";
import { RoleSkillBuilder } from "@/components/RoleSkillBuilder";
import { KnowledgeEditor } from "@/components/KnowledgeEditor";
import { ProfileSetup } from "@/components/ProfileSetup";
import { useWarRoomStore } from "@/store/warRoomStore";

export function WorkspaceSetupPage() {
  const { workspaceStatus } = useWarRoomStore();
  const steps = [
    Boolean(workspaceStatus?.workspace.organization_name),
    Boolean(workspaceStatus?.role_count),
    Boolean(workspaceStatus?.skill_count),
    Boolean(workspaceStatus?.knowledge_count),
    Boolean(workspaceStatus?.profile_count),
  ];
  const complete = steps.filter(Boolean).length;

  return (
    <section className="product-page">
      <header className="page-header page-header-with-progress">
        <div>
          <p>Configuration workflow</p>
          <h2>Build your training workspace</h2>
          <span>Complete the organization model before evaluating candidates.</span>
        </div>
        <div className="setup-progress">
          <strong>{complete}/{steps.length}</strong>
          <span>setup steps complete</span>
        </div>
      </header>

      <div className="setup-step-stack">
        <SetupStep number={1} title="Organization" complete={steps[0]}><WorkspaceStatusPanel /></SetupStep>
        <SetupStep number={2} title="Roles and Skills" complete={steps[1] && steps[2]}><RoleSkillBuilder /></SetupStep>
        <SetupStep number={3} title="Knowledge Documents" complete={steps[3]}><KnowledgeEditor /></SetupStep>
        <SetupStep number={4} title="Evaluated Profiles" complete={steps[4]}><ProfileSetup /></SetupStep>
        <SetupStep number={5} title="Templates" complete={!workspaceStatus?.is_empty}><WorkspaceOnboarding /></SetupStep>
      </div>
    </section>
  );
}

function SetupStep({ number, title, complete, children }: { number: number; title: string; complete: boolean; children: React.ReactNode }) {
  return (
    <section className="setup-step">
      <div className="setup-step-label">
        <span>{number}</span>
        <div><p>Step {number}</p><h3>{title}</h3></div>
        {complete && <CheckCircle2 className="h-5 w-5 text-emerald-300" />}
      </div>
      <div className="setup-step-content">{children}</div>
    </section>
  );
}
