"use client";

import { Activity, Database, ShieldCheck, Volume2, VolumeX } from "lucide-react";
import { StatusPill } from "@/components/StatusPill";
import { useWarRoomStore } from "@/store/warRoomStore";

const SECTION_TITLES = {
  "command-center": "Command Center",
  "workspace-setup": "Workspace Setup",
  "scenario-studio": "Scenario Studio",
  "evaluation-room": "Evaluation Room",
  "results-center": "Results Center",
  "tools-readiness": "Tools & Readiness",
};

export function TopBar() {
  const {
    activeSection,
    health,
    voiceStatus,
    voiceEnabled,
    toggleVoice,
    workspaceStatus,
  } = useWarRoomStore();

  return (
    <header className="top-bar">
      <div className="top-bar-title">
        <p>{workspaceStatus?.workspace.organization_name || "New Workspace"}</p>
        <h1>{SECTION_TITLES[activeSection]}</h1>
      </div>
      <div className="top-bar-status">
        <StatusPill
          label={health?.status === "ok" ? "Backend online" : "Backend unavailable"}
          status={health?.status === "ok" ? "ok" : "warn"}
        />
        <StatusPill label="Sanitized training data" status="ok" />
        <StatusPill label="No production changes" status="neutral" />
        <button
          type="button"
          className="icon-control"
          onClick={toggleVoice}
          aria-pressed={voiceEnabled}
          title={voiceEnabled ? "Turn Voice Off" : "Turn Voice On"}
        >
          {voiceEnabled && voiceStatus.configured
            ? <Volume2 className="h-4 w-4" />
            : <VolumeX className="h-4 w-4" />}
        </button>
      </div>
      <div className="top-bar-context">
        <Activity className="h-4 w-4" />
        <span>{workspaceStatus?.scenario_count ?? 0} scenarios</span>
        <Database className="h-4 w-4" />
        <span>{workspaceStatus?.profile_count ?? 0} profiles</span>
        <ShieldCheck className="h-4 w-4" />
        <span>{voiceStatus.configured ? "Azure Speech ready" : "Text fallback"}</span>
      </div>
    </header>
  );
}
