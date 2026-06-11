"use client";

import { BookOpenCheck, Building2, FilePlus2, Layers3, Siren } from "lucide-react";
import { useWarRoomStore } from "@/store/warRoomStore";

export function WorkspaceOnboarding() {
  const {
    workspaceTemplates,
    isWorkspaceSaving,
    startEmptyWorkspace,
    applyTemplate,
    applyEdukyWorkspace,
    setExamplesEnabled,
    workspaceStatus,
    goToScenarioStudio,
  } = useWarRoomStore();
  const genericTemplates = workspaceTemplates?.workspace_templates.filter(
    (template) =>
      template.template_id !== "template-empty"
      && template.template_id !== "template-eduky",
  ) ?? [];

  return (
    <section className="workspace-onboarding">
      <div className="workspace-onboarding-copy">
        <p className="panel-kicker">Workspace templates</p>
        <h2>{workspaceStatus?.is_empty ? "Your workspace is empty." : "Start from a reusable configuration."}</h2>
        <p>
          {workspaceStatus?.is_empty
            ? "Configure your organization, roles, knowledge, scenarios, and evaluated profile."
            : "Applying a template replaces generated workspace content. Review the template before continuing."}
        </p>
      </div>
      <div className="workspace-onboarding-actions">
        <button
          type="button"
          className="workspace-action"
          disabled={isWorkspaceSaving}
          onClick={() => void startEmptyWorkspace()}
        >
          <FilePlus2 className="h-4 w-4" />
          <span>
            <strong>Start Empty</strong>
            <small>Open the configuration studios.</small>
          </span>
        </button>
        {genericTemplates.map((template) => (
          <button
            type="button"
            key={template.template_id}
            className={
              template.template_id === "template-creator-operations"
                ? "workspace-action workspace-action-primary"
                : "workspace-action"
            }
            disabled={isWorkspaceSaving}
            onClick={() => void applyTemplate(template.template_id)}
          >
            <Layers3 className="h-4 w-4" />
            <span>
              <strong>{template.name}</strong>
              <small>{template.description}</small>
            </span>
          </button>
        ))}
        <button
          type="button"
          className="workspace-action"
          onClick={goToScenarioStudio}
        >
          <Siren className="h-4 w-4" />
          <span>
            <strong>Operations Incident</strong>
            <small>Open the generic incident scenario starter.</small>
          </span>
        </button>
        <button
          type="button"
          className="workspace-action workspace-action-primary"
          disabled={isWorkspaceSaving}
          onClick={() => void applyEdukyWorkspace()}
        >
          <Building2 className="h-4 w-4" />
          <span>
            <strong>Optional Customer Pack</strong>
            <small>Apply the separate sanitized customer-specific workspace.</small>
          </span>
        </button>
        <button
          type="button"
          className="workspace-action"
          disabled={isWorkspaceSaving}
          onClick={() => void setExamplesEnabled(true)}
        >
          <BookOpenCheck className="h-4 w-4" />
          <span>
            <strong>Enable Example Pack</strong>
            <small>Browse optional generic product examples.</small>
          </span>
        </button>
      </div>
    </section>
  );
}
