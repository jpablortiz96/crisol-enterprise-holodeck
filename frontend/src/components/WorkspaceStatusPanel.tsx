"use client";

import { useEffect, useState } from "react";
import { Building2, Database, FileText, Library, Save, UserRound, Wrench } from "lucide-react";
import { useWarRoomStore } from "@/store/warRoomStore";

export function WorkspaceStatusPanel() {
  const {
    workspaceStatus,
    isWorkspaceSaving,
    setExamplesEnabled,
    configureOrganization,
  } = useWarRoomStore();
  const [organizationName, setOrganizationName] = useState("");
  const [industry, setIndustry] = useState("");
  const [workspaceName, setWorkspaceName] = useState("New CRISOL Workspace");

  useEffect(() => {
    if (!workspaceStatus) {
      return;
    }
    setOrganizationName(workspaceStatus.workspace.organization_name);
    setIndustry(workspaceStatus.workspace.industry);
    setWorkspaceName(workspaceStatus.workspace.workspace_name);
  }, [workspaceStatus]);

  if (!workspaceStatus) {
    return null;
  }

  const metrics = [
    { label: "Scenarios", value: workspaceStatus.scenario_count, icon: Library },
    { label: "Knowledge", value: workspaceStatus.knowledge_count, icon: FileText },
    { label: "Roles", value: workspaceStatus.role_count, icon: UserRound },
    { label: "Skills", value: workspaceStatus.skill_count, icon: Wrench },
    { label: "Profiles", value: workspaceStatus.profile_count, icon: Database },
  ];

  return (
    <section className="war-panel workspace-status-panel">
      <div className="panel-header">
        <div>
          <p className="panel-kicker">Active workspace</p>
          <h2 className="panel-title">
            {workspaceStatus.workspace.organization_name || "New Workspace"}
          </h2>
          <p className="workspace-status-context">{workspaceStatus.workspace.workspace_name}</p>
        </div>
        <label className="workspace-example-toggle">
          <input
            type="checkbox"
            checked={workspaceStatus.load_examples}
            disabled={isWorkspaceSaving}
            onChange={(event) => void setExamplesEnabled(event.target.checked)}
          />
          <span>Example pack</span>
        </label>
      </div>
      <div className="workspace-organization-form">
        <label className="technical-field">
          Organization name
          <input
            value={organizationName}
            placeholder="Organization name"
            onChange={(event) => setOrganizationName(event.target.value)}
          />
        </label>
        <label className="technical-field">
          Industry
          <input
            value={industry}
            placeholder="Industry"
            onChange={(event) => setIndustry(event.target.value)}
          />
        </label>
        <label className="technical-field">
          Workspace name
          <input
            value={workspaceName}
            onChange={(event) => setWorkspaceName(event.target.value)}
          />
        </label>
        <button
          type="button"
          className="control-button control-secondary workspace-organization-save"
          disabled={isWorkspaceSaving}
          onClick={() => void configureOrganization({
            organization_name: organizationName,
            industry,
            workspace_name: workspaceName,
          })}
        >
          <Save className="h-4 w-4" />
          Save Organization
        </button>
      </div>
      <div className="workspace-metrics">
        {metrics.map(({ label, value, icon: Icon }) => (
          <div key={label} className="workspace-metric">
            <Icon className="h-4 w-4" />
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </div>
      <p className="workspace-data-mode">
        <Building2 className="h-3.5 w-3.5" />
        {workspaceStatus.workspace.industry || "Industry not configured"}
        {" / "}
        Data mode: <strong>{workspaceStatus.workspace.data_mode}</strong>
      </p>
    </section>
  );
}
