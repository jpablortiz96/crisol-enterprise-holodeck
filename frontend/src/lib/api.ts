import type {
  CompetenceReport,
  HealthResponse,
  ManagerFragilityMap,
  ReadinessSummary,
  SimulationRun,
  TimelineResponse,
} from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_CRISOL_API_URL || "http://127.0.0.1:8000";

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      Accept: "application/json",
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
