"use client";

import {
  BarChart3,
  BriefcaseBusiness,
  Building2,
  Gauge,
  ShieldCheck,
  SlidersHorizontal,
} from "lucide-react";
import { useWarRoomStore } from "@/store/warRoomStore";
import type { AppSection } from "@/lib/types";

const NAV_ITEMS: Array<{
  section: AppSection;
  label: string;
  icon: typeof Gauge;
}> = [
  { section: "command-center", label: "Command Center", icon: Gauge },
  { section: "workspace-setup", label: "Workspace Setup", icon: Building2 },
  { section: "scenario-studio", label: "Scenario Studio", icon: BriefcaseBusiness },
  { section: "evaluation-room", label: "Evaluation Room", icon: SlidersHorizontal },
  { section: "results-center", label: "Results Center", icon: BarChart3 },
  { section: "tools-readiness", label: "Tools & Readiness", icon: ShieldCheck },
];

export function NavigationSidebar() {
  const { activeSection, setActiveSection, workspaceStatus } = useWarRoomStore();

  return (
    <aside className="navigation-sidebar">
      <div className="sidebar-brand">
        <span className="brand-mark"><ShieldCheck className="h-5 w-5" /></span>
        <span>
          <strong>CRISOL</strong>
          <small>Readiness platform</small>
        </span>
      </div>

      <nav className="sidebar-nav" aria-label="Product sections">
        {NAV_ITEMS.map(({ section, label, icon: Icon }) => (
          <button
            type="button"
            key={section}
            className={activeSection === section ? "sidebar-link sidebar-link-active" : "sidebar-link"}
            onClick={() => setActiveSection(section)}
            aria-current={activeSection === section ? "page" : undefined}
          >
            <Icon className="h-4 w-4" />
            <span>{label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-boundary">
        <p>Active workspace</p>
        <strong>{workspaceStatus?.workspace.organization_name || "New Workspace"}</strong>
        <span>{workspaceStatus?.workspace.workspace_name || "Loading workspace"}</span>
      </div>
    </aside>
  );
}
