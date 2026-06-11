import type {
  CompetenceReport,
  HealthResponse,
  ManagerFragilityMap,
  McpDemoResponse,
  McpToolsResponse,
  ReadinessSummary,
  ReplayBranchResult,
  ScenarioSummary,
  SimulationRun,
  TelemetrySummary,
  TimelineResponse,
  VoiceStatusResponse,
  WorkspaceStatus,
  WorkspaceWalkthrough,
  KnowledgeDocument,
  WorkspaceProfile,
  WorkspaceRole,
  WorkspaceSkill,
  WorkspaceTemplates,
  ScenarioValidationResult,
} from "@/lib/types";

export const API_BASE = process.env.NEXT_PUBLIC_CRISOL_API_URL || "http://127.0.0.1:8000";

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      ...(init.body ? { "Content-Type": "application/json" } : {}),
      ...init.headers,
    },
  });

  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const payload = await response.json() as { detail?: string };
      if (payload.detail) {
        detail = payload.detail;
      }
    } catch {
      // The response did not include a JSON error body.
    }
    throw new Error(`Request failed: ${detail}`);
  }

  return response.json() as Promise<T>;
}

export function runScenario(roleId = "ROLE-SRE"): Promise<SimulationRun> {
  return request<SimulationRun>(`/scenario/run?role_id=${encodeURIComponent(roleId)}`);
}

export function getScenarios(): Promise<ScenarioSummary[]> {
  return request<ScenarioSummary[]>("/scenarios");
}

export function getWorkspaceStatus(): Promise<WorkspaceStatus> {
  return request<WorkspaceStatus>("/workspace/status");
}

export function getWorkspaceWalkthrough(): Promise<WorkspaceWalkthrough> {
  return request<WorkspaceWalkthrough>("/workspace/walkthrough");
}

export function initializeEmptyWorkspace(): Promise<WorkspaceStatus> {
  return request<WorkspaceStatus>("/workspace/initialize-empty", { method: "POST" });
}

export function enableWorkspaceExamples(): Promise<WorkspaceStatus> {
  return request<WorkspaceStatus>("/workspace/enable-examples", { method: "POST" });
}

export function disableWorkspaceExamples(): Promise<WorkspaceStatus> {
  return request<WorkspaceStatus>("/workspace/disable-examples", { method: "POST" });
}

export function applyEdukyTemplate(): Promise<WorkspaceStatus> {
  return request<WorkspaceStatus>("/workspace/apply-template/eduky", { method: "POST" });
}

export function applyWorkspaceTemplate(templateId: string): Promise<WorkspaceStatus> {
  return request<WorkspaceStatus>(
    `/workspace/apply-template/${encodeURIComponent(templateId)}`,
    { method: "POST" },
  );
}

export function configureWorkspaceOrganization(configuration: {
  organization_name: string;
  industry: string;
  workspace_name: string;
}): Promise<WorkspaceStatus> {
  return request<WorkspaceStatus>("/workspace/configure-organization", {
    method: "POST",
    body: JSON.stringify(configuration),
  });
}

export function getWorkspaceKnowledge(): Promise<KnowledgeDocument[]> {
  return request<KnowledgeDocument[]>("/workspace/knowledge");
}

export function saveWorkspaceKnowledge(
  fileName: string,
  content: string,
): Promise<KnowledgeDocument> {
  return request<KnowledgeDocument>("/workspace/knowledge", {
    method: "POST",
    body: JSON.stringify({ file_name: fileName, content }),
  });
}

export function getWorkspaceRoles(): Promise<WorkspaceRole[]> {
  return request<WorkspaceRole[]>("/workspace/roles");
}

export function saveWorkspaceRole(
  role: Omit<WorkspaceRole, "data_classification">,
): Promise<WorkspaceRole> {
  return request<WorkspaceRole>("/workspace/roles", {
    method: "POST",
    body: JSON.stringify(role),
  });
}

export function getWorkspaceSkills(): Promise<WorkspaceSkill[]> {
  return request<WorkspaceSkill[]>("/workspace/skills");
}

export function saveWorkspaceSkill(
  skill: Omit<WorkspaceSkill, "data_classification">,
): Promise<WorkspaceSkill> {
  return request<WorkspaceSkill>("/workspace/skills", {
    method: "POST",
    body: JSON.stringify(skill),
  });
}

export function getWorkspaceProfiles(): Promise<WorkspaceProfile[]> {
  return request<WorkspaceProfile[]>("/workspace/profiles");
}

export function saveWorkspaceProfile(
  profile: Omit<WorkspaceProfile, "data_classification">,
): Promise<WorkspaceProfile> {
  return request<WorkspaceProfile>("/workspace/profiles", {
    method: "POST",
    body: JSON.stringify(profile),
  });
}

export function saveWorkspaceScenario(
  scenario: Record<string, unknown>,
): Promise<Record<string, unknown>> {
  return request<Record<string, unknown>>("/workspace/scenarios", {
    method: "POST",
    body: JSON.stringify(scenario),
  });
}

export function validateWorkspaceScenario(
  scenario: Record<string, unknown>,
): Promise<ScenarioValidationResult> {
  return request<ScenarioValidationResult>("/scenarios/validate", {
    method: "POST",
    body: JSON.stringify(scenario),
  });
}

export function getWorkspaceTemplates(): Promise<WorkspaceTemplates> {
  return Promise.all([
    request<WorkspaceTemplates["workspace_templates"]>("/workspace/templates"),
    request<WorkspaceTemplates["scenario_templates"]>("/workspace/scenario-templates"),
  ]).then(([workspaceTemplates, scenarioTemplates]) => ({
    workspace_templates: workspaceTemplates,
    scenario_templates: scenarioTemplates,
  }));
}

export function getScenario(id: string): Promise<Record<string, unknown>> {
  return request<Record<string, unknown>>(`/scenarios/${encodeURIComponent(id)}`);
}

export function runCustomScenario(id: string, roleId: string): Promise<SimulationRun> {
  return request<SimulationRun>("/scenario/run-custom", {
    method: "POST",
    body: JSON.stringify({ scenario_id: id, role_id: roleId }),
  });
}

export function streamCustomScenarioUrl(id: string, roleId: string): string {
  const parameters = new URLSearchParams({ scenario_id: id, role_id: roleId });
  return `${API_BASE}/scenario/stream-custom?${parameters.toString()}`;
}

export function scenarioStreamUrl(roleId = "ROLE-SRE"): string {
  return `${API_BASE}/scenario/stream?role_id=${encodeURIComponent(roleId)}`;
}

export function apiAssetUrl(path: string): string {
  return new URL(path, `${API_BASE}/`).toString();
}

export function runTimeline(roleId = "ROLE-SRE"): Promise<TimelineResponse> {
  return request<TimelineResponse>(`/scenario/run/timeline?role_id=${encodeURIComponent(roleId)}`);
}

export function getLatestReport(): Promise<CompetenceReport> {
  return request<CompetenceReport>("/reports/latest");
}

export function getFragilityMap(): Promise<ManagerFragilityMap> {
  return request<ManagerFragilityMap>("/manager/fragility-map");
}

export function getReadinessSummary(): Promise<ReadinessSummary> {
  return request<ReadinessSummary>("/manager/readiness-summary");
}

export function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

export function getVoiceStatus(): Promise<VoiceStatusResponse> {
  return request<VoiceStatusResponse>("/voice/status");
}

export function getTelemetrySummary(): Promise<TelemetrySummary> {
  return request<TelemetrySummary>("/telemetry/summary");
}

export function getMcpTools(): Promise<McpToolsResponse> {
  return request<McpToolsResponse>("/mcp/tools");
}

export function runMcpDemo(): Promise<McpDemoResponse> {
  return request<McpDemoResponse>("/mcp/demo", { method: "POST" });
}

export function branchFromSession(
  sessionId: string,
  decisionNodeId: string,
  alternativeAction: string,
): Promise<ReplayBranchResult> {
  return request<ReplayBranchResult>("/replay/branch-from", {
    method: "POST",
    body: JSON.stringify({
      session_id: sessionId,
      decision_node_id: decisionNodeId,
      alternative_action: alternativeAction,
    }),
  });
}
