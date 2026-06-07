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
    throw new Error(`Request failed: ${response.status} ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}

export function runScenario(roleId = "ROLE-SRE"): Promise<SimulationRun> {
  return request<SimulationRun>(`/scenario/run?role_id=${encodeURIComponent(roleId)}`);
}

export function getScenarios(): Promise<ScenarioSummary[]> {
  return request<ScenarioSummary[]>("/scenarios");
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
