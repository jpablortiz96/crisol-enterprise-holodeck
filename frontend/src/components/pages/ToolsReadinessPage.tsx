"use client";

import { Activity, Cloud, Database, Radio, Server, ShieldCheck } from "lucide-react";
import { McpToolsPanel } from "@/components/McpToolsPanel";
import { ProductReadinessPanel } from "@/components/ProductReadinessPanel";
import { useWarRoomStore } from "@/store/warRoomStore";

export function ToolsReadinessPage() {
  const { health, groundingStatus, voiceStatus, telemetrySummary, mcpTools } = useWarRoomStore();

  return (
    <section className="product-page">
      <header className="page-header">
        <p>Administrator workspace</p>
        <h2>Tools &amp; Readiness</h2>
        <span>Inspect service health, evaluation status, telemetry boundaries, voice readiness, and the reusable MCP tool surface.</span>
      </header>

      <div className="admin-status-grid">
        <AdminStatus icon={Server} label="Backend health" value={health?.status ?? "Unavailable"} ready={health?.status === "ok"} />
        <AdminStatus icon={Radio} label="Voice status" value={voiceStatus.configured ? "Azure Speech ready" : "Text fallback"} ready={voiceStatus.configured} />
        <AdminStatus icon={Activity} label="Evaluation status" value={telemetrySummary?.evaluation_status ?? "Pending"} ready={telemetrySummary?.evaluation_status === "pass"} />
        <AdminStatus icon={Database} label="Telemetry events" value={String(telemetrySummary?.event_count ?? 0)} ready={Boolean(telemetrySummary?.event_count)} />
        <AdminStatus icon={ShieldCheck} label="Release boundary" value="No production changes" ready />
        <AdminStatus icon={ShieldCheck} label="MCP tools" value={String(mcpTools.length)} ready={mcpTools.length >= 6} />
      </div>

      <div className="tools-readiness-grid">
        <ProductReadinessPanel />
        <McpToolsPanel />
      </div>

      <section className="war-panel grounding-status-panel">
        <div className="panel-header">
          <div><p className="panel-kicker">Knowledge retrieval</p><h2 className="panel-title">Grounding Status</h2></div>
          <Cloud className="h-5 w-5" />
        </div>
        <div className="telemetry-detail-grid">
          <GroundingMetric label="Mode" value={groundingStatus?.mode ?? "Unavailable"} />
          <GroundingMetric label="Foundry project" value={yesNo(groundingStatus?.foundry_project_configured)} />
          <GroundingMetric label="Model deployment" value={yesNo(groundingStatus?.model_deployment_configured)} />
          <GroundingMetric label="Azure Search" value={yesNo(groundingStatus?.azure_search_configured)} />
          <GroundingMetric label="Search index" value={groundingStatus?.search_index || "Not configured"} />
        </div>
        {groundingStatus?.warnings.length ? (
          <ul className="grounding-warning-list">
            {groundingStatus.warnings.map((warning) => <li key={warning}>{warning}</li>)}
          </ul>
        ) : null}
      </section>

      <section className="war-panel telemetry-detail-panel">
        <div className="panel-header">
          <div><p className="panel-kicker">Allowlisted telemetry</p><h2 className="panel-title">Telemetry Summary</h2></div>
        </div>
        <div className="telemetry-detail-grid">
          <div><span>Data mode</span><strong>{telemetrySummary?.data_mode ?? "sanitized-training"}</strong></div>
          <div><span>Production changes</span><strong>{telemetrySummary?.production_changes ? "Enabled" : "Disabled"}</strong></div>
          <div><span>Evaluation score</span><strong>{telemetrySummary?.evaluation_score ?? "Pending"}</strong></div>
          <div><span>Latest event</span><strong>{telemetrySummary?.latest_event?.event_type ?? "No events"}</strong></div>
        </div>
      </section>
    </section>
  );
}

function GroundingMetric({ label, value }: { label: string; value: string }) {
  return <div><span>{label}</span><strong>{value}</strong></div>;
}

function yesNo(value: boolean | undefined): string {
  if (value === undefined) return "Unavailable";
  return value ? "Yes" : "No";
}

function AdminStatus({ icon: Icon, label, value, ready }: { icon: typeof Server; label: string; value: string; ready: boolean }) {
  return (
    <div className={ready ? "admin-status-card admin-status-ready" : "admin-status-card"}>
      <Icon className="h-5 w-5" />
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
