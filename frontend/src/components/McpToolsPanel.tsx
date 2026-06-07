"use client";

import { Braces, LoaderCircle, Play } from "lucide-react";
import { formatCurrency } from "@/lib/format";
import { useWarRoomStore } from "@/store/warRoomStore";


export function McpToolsPanel() {
  const { mcpTools, mcpDemo, isMcpLoading, runMcpDemo } = useWarRoomStore();

  return (
    <section className="war-panel mcp-panel">
      <div className="panel-header">
        <div>
          <p className="panel-kicker">Reusable tool surface</p>
          <h2 className="panel-title">CRISOL MCP Server</h2>
        </div>
        <Braces className="h-5 w-5 text-cyan-300" />
      </div>

      <div className="mcp-tool-list">
        {mcpTools.map((tool) => (
          <div key={tool.name} className="mcp-tool-row">
            <code>{tool.name}</code>
            <span>{tool.description}</span>
          </div>
        ))}
        {!mcpTools.length && <div className="empty-state">Tool registry unavailable.</div>}
      </div>

      <button
        onClick={() => void runMcpDemo()}
        disabled={isMcpLoading}
        className="control-button control-secondary mcp-demo-button"
      >
        {isMcpLoading ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
        {isMcpLoading ? "Running Preview" : "Run Tool Preview"}
      </button>

      {mcpDemo && (
        <div className="mcp-demo-output">
          <div>
            <span>Scenario</span>
            <strong>{mcpDemo.started.scenario_id}</strong>
          </div>
          <div>
            <span>Tool count</span>
            <strong>{mcpDemo.tools.length}</strong>
          </div>
          <div>
            <span>Decision</span>
            <strong>{mcpDemo.decision.decision}</strong>
          </div>
          <div>
            <span>Revenue at risk</span>
            <strong>{formatCurrency(mcpDemo.situation.revenue_at_risk)}</strong>
          </div>
          <div>
            <span>Projected score</span>
            <strong>{mcpDemo.competence_report.overall_score.toFixed(1)}</strong>
          </div>
          <p>{mcpDemo.decision.world_delta}</p>
        </div>
      )}
    </section>
  );
}
