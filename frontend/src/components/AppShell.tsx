"use client";

import type { ReactNode } from "react";
import { NavigationSidebar } from "@/components/NavigationSidebar";
import { TopBar } from "@/components/TopBar";
import { CommandCenterPage } from "@/components/pages/CommandCenterPage";
import { WorkspaceSetupPage } from "@/components/pages/WorkspaceSetupPage";
import { ScenarioStudioPage } from "@/components/pages/ScenarioStudioPage";
import { EvaluationRoomPage } from "@/components/pages/EvaluationRoomPage";
import { ResultsCenterPage } from "@/components/pages/ResultsCenterPage";
import { ToolsReadinessPage } from "@/components/pages/ToolsReadinessPage";
import { useWarRoomStore } from "@/store/warRoomStore";
import type { AppSection } from "@/lib/types";

const PAGES: Record<AppSection, ReactNode> = {
  "command-center": <CommandCenterPage />,
  "workspace-setup": <WorkspaceSetupPage />,
  "scenario-studio": <ScenarioStudioPage />,
  "evaluation-room": <EvaluationRoomPage />,
  "results-center": <ResultsCenterPage />,
  "tools-readiness": <ToolsReadinessPage />,
};

export function AppShell() {
  const { activeSection, error } = useWarRoomStore();

  return (
    <main className="app-shell">
      <NavigationSidebar />
      <div className="app-main">
        <TopBar />
        {error && <div className="error-banner">{error}</div>}
        <div className="page-viewport">{PAGES[activeSection]}</div>
        <footer className="enterprise-boundary-footer">
          Training environment | Sanitized training data | No production changes
        </footer>
      </div>
    </main>
  );
}
