"use client";

import { useMemo, type ReactNode } from "react";
import dagre from "@dagrejs/dagre";
import {
  Background,
  Controls,
  MarkerType,
  Position,
  ReactFlow,
  type Edge,
  type Node,
} from "@xyflow/react";
import { AlertTriangle, CheckCircle2, CircleDot, Flag } from "lucide-react";
import type { TimelineNode, TimelineResponse } from "@/lib/types";
import { formatCurrency } from "@/lib/format";

type TimelineGraphProps = {
  timeline?: TimelineResponse | null;
};

type TimelineNodeState = "root" | "risk" | "recovery" | "steady";

type TimelineNodeData = {
  label: ReactNode;
};

type TimelineFlowNode = Node<TimelineNodeData>;

const NODE_WIDTH = 178;
const NODE_HEIGHT = 112;

function TimelineNodeContent({
  node,
  state,
}: {
  node: TimelineNode;
  state: TimelineNodeState;
}) {
  const Icon =
    state === "root"
      ? Flag
      : state === "risk"
        ? AlertTriangle
        : state === "recovery"
          ? CheckCircle2
          : CircleDot;

  return (
    <>
      <div className="flex items-center justify-between gap-3">
        <span className="flex min-w-0 items-center gap-1.5 text-[9px] uppercase text-slate-500">
          <Icon className="h-3 w-3 shrink-0" />
          <span className="truncate">
            {node.turn_number === 0 ? "Root state" : `Turn ${node.turn_number}`}
          </span>
        </span>
        <span className="timeline-severity">S{node.severity}</span>
      </div>
      <p className="mt-2 line-clamp-2 text-xs font-semibold leading-4 text-white">
        {node.decision_label || "Scenario initialized"}
      </p>
      <div className="mt-3 border-t border-white/5 pt-2">
        <p className="text-[9px] uppercase text-slate-600">Revenue at risk</p>
        <p className="mt-0.5 truncate text-[11px] font-medium text-slate-300">
          {formatCurrency(node.revenue_at_risk)}
        </p>
      </div>
      {state === "risk" && <span className="timeline-state-label">Cascade</span>}
      {state === "recovery" && <span className="timeline-state-label">Stabilizing</span>}
    </>
  );
}

export function TimelineGraph({ timeline }: TimelineGraphProps) {
  const layout = useMemo(() => layoutTimeline(timeline), [timeline]);
  const layoutKey = useMemo(
    () => `${timeline?.session_id ?? "empty"}:${layout.nodes.map((node) => node.id).join("|")}`,
    [layout.nodes, timeline?.session_id],
  );

  return (
    <section className="war-panel timeline-panel">
      <div className="panel-header">
        <div>
          <p className="panel-kicker">Branching consequence timeline</p>
          <h2 className="panel-title">Decision Graph</h2>
        </div>
        <div className="timeline-summary">
          <span>
            <strong>{timeline?.summary.total_nodes ?? 0}</strong> nodes
          </span>
          <span>Left-to-right flow</span>
        </div>
      </div>

      <div className="timeline-canvas">
        {layout.nodes.length ? (
          <TimelineFlow
            nodes={layout.nodes}
            edges={layout.edges}
            layoutKey={layoutKey}
          />
        ) : (
          <div className="empty-state h-full">
            The branching consequence timeline will animate as decisions land.
          </div>
        )}
      </div>
    </section>
  );
}

function TimelineFlow({
  nodes,
  edges,
  layoutKey,
}: {
  nodes: TimelineFlowNode[];
  edges: Edge[];
  layoutKey: string;
}) {
  return (
    <ReactFlow<TimelineFlowNode, Edge>
      key={layoutKey}
      nodes={nodes}
      edges={edges}
      fitView
      fitViewOptions={{ padding: 0.2, minZoom: 0.45, maxZoom: 1 }}
      minZoom={0.4}
      maxZoom={1.15}
      nodesDraggable={false}
      nodesConnectable={false}
      elementsSelectable={false}
      panOnDrag
      zoomOnDoubleClick={false}
      proOptions={{ hideAttribution: true }}
    >
      <Background color="#253844" gap={24} size={1} />
      <Controls
        showInteractive={false}
        position="bottom-left"
        orientation="horizontal"
      />
    </ReactFlow>
  );
}

function layoutTimeline(timeline?: TimelineResponse | null): {
  nodes: TimelineFlowNode[];
  edges: Edge[];
} {
  if (!timeline?.nodes.length) {
    return { nodes: [], edges: [] };
  }

  const orderedNodes = [...timeline.nodes].sort(
    (first, second) =>
      first.turn_number - second.turn_number ||
      first.created_at.localeCompare(second.created_at),
  );
  const nodeById = new Map(orderedNodes.map((node) => [node.node_id, node]));
  const graph = new dagre.graphlib.Graph({ multigraph: true });
  graph.setDefaultEdgeLabel(() => ({}));
  graph.setGraph({
    rankdir: "LR",
    align: "UL",
    ranker: "tight-tree",
    ranksep: 44,
    nodesep: 30,
    edgesep: 18,
    marginx: 24,
    marginy: 24,
  });

  orderedNodes.forEach((node) => {
    graph.setNode(node.node_id, { width: NODE_WIDTH, height: NODE_HEIGHT });
  });
  timeline.edges.forEach((edge, index) => {
    graph.setEdge(edge.from, edge.to, {}, `${edge.from}-${edge.to}-${index}`);
  });
  dagre.layout(graph);

  const nodes = orderedNodes.map<TimelineFlowNode>((node) => {
    const position = graph.node(node.node_id) as { x: number; y: number };
    const state = timelineNodeState(
      node,
      nodeById.get(node.parent_node_id ?? ""),
    );
    return {
      id: node.node_id,
      position: {
        x: position.x - NODE_WIDTH / 2,
        y: position.y - NODE_HEIGHT / 2,
      },
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
      data: {
        label: <TimelineNodeContent node={node} state={state} />,
      },
      className: `timeline-node timeline-${state}`,
      style: {
        width: NODE_WIDTH,
        height: NODE_HEIGHT,
      },
    };
  });

  const edges = timeline.edges.map<Edge>((edge, index) => ({
    id: `${edge.from}-${edge.to}-${index}`,
    source: edge.from,
    target: edge.to,
    type: "smoothstep",
    label: compactEdgeLabel(nodeById.get(edge.to)?.turn_number),
    ariaLabel: edge.label,
    animated: index === timeline.edges.length - 1,
    interactionWidth: 14,
    markerEnd: {
      type: MarkerType.ArrowClosed,
      color: index === timeline.edges.length - 1 ? "#67e8f9" : "#4b6474",
      width: 14,
      height: 14,
    },
    style: {
      stroke: index === timeline.edges.length - 1 ? "#67e8f9" : "#4b6474",
      strokeWidth: index === timeline.edges.length - 1 ? 1.8 : 1.35,
    },
    labelStyle: {
      fill: "#8da0aa",
      fontSize: 8,
      fontWeight: 600,
    },
    labelBgStyle: {
      fill: "#071016",
      fillOpacity: 0.94,
    },
    labelBgPadding: [5, 3],
    labelBgBorderRadius: 4,
  }));

  return { nodes, edges };
}

function timelineNodeState(
  node: TimelineNode,
  parent?: TimelineNode,
): TimelineNodeState {
  if (node.turn_number === 0) {
    return "root";
  }
  if (node.revenue_delta > 0 || node.severity >= 5) {
    return "risk";
  }
  if (
    node.revenue_delta < 0 ||
    (parent && node.severity < parent.severity)
  ) {
    return "recovery";
  }
  return "steady";
}

function compactEdgeLabel(turnNumber?: number): string | undefined {
  return turnNumber && turnNumber > 0 ? `T${turnNumber}` : undefined;
}
