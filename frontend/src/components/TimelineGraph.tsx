"use client";

import ReactFlow, { Background, Controls, MarkerType, type Edge, type Node } from "reactflow";
import type { TimelineResponse } from "@/lib/types";
import { formatCurrency, formatDelta } from "@/lib/format";

type TimelineGraphProps = {
  timeline?: TimelineResponse | null;
};

export function TimelineGraph({ timeline }: TimelineGraphProps) {
  const nodes: Node[] =
    timeline?.nodes.map((node, index) => {
      const isBad = node.revenue_delta > 0 || node.severity >= 5;
      return {
        id: node.node_id,
        position: { x: index * 230, y: index % 2 === 0 ? 60 : 190 },
        data: {
          label: (
            <div className={`min-w-[180px] rounded-lg border p-3 ${isBad ? "border-danger/50 bg-danger/10" : "border-line bg-panel"}`}>
              <p className="text-[11px] uppercase tracking-wide text-slate-400">
                {node.turn_number === 0 ? "Root" : `Turn ${node.turn_number}`}
              </p>
              <p className="mt-1 text-sm font-semibold text-white">{node.decision_label || "Scenario start"}</p>
              <div className="mt-2 grid grid-cols-2 gap-2 text-[11px] text-slate-300">
                <span>Severity {node.severity}</span>
                <span>{formatDelta(node.revenue_delta)}</span>
              </div>
              <p className="mt-2 text-[11px] text-slate-400">{formatCurrency(node.revenue_at_risk)}</p>
            </div>
          ),
        },
        type: "default",
      };
    }) ?? [];

  const edges: Edge[] =
    timeline?.edges.map((edge) => ({
      id: `${edge.from}-${edge.to}`,
      source: edge.from,
      target: edge.to,
      label: edge.label,
      markerEnd: { type: MarkerType.ArrowClosed },
      style: { stroke: "#64748b" },
      labelStyle: { fill: "#cbd5e1", fontSize: 11 },
    })) ?? [];

  return (
    <section className="min-h-[420px] rounded-lg border border-line bg-panel/80 p-4 shadow-soft-border">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-400">Branching consequence timeline</p>
          <h2 className="text-lg font-semibold text-white">Decision Graph</h2>
        </div>
        <span className="rounded-full border border-slate-600 px-2 py-1 text-xs text-slate-300">
          {timeline?.summary.total_nodes ?? 0} nodes
        </span>
      </div>
      <div className="h-[460px] overflow-hidden rounded-lg border border-line bg-ink">
        {nodes.length ? (
          <ReactFlow nodes={nodes} edges={edges} fitView proOptions={{ hideAttribution: true }}>
            <Background color="#334155" gap={20} />
            <Controls />
          </ReactFlow>
        ) : (
          <div className="flex h-full items-center justify-center text-sm text-slate-500">
            Run a simulation to render the timeline.
          </div>
        )}
      </div>
    </section>
  );
}
