"use client";

import { useEffect, useState } from "react";
import { GitBranch, LoaderCircle } from "lucide-react";
import { formatCurrency } from "@/lib/format";
import { useWarRoomStore } from "@/store/warRoomStore";


const QUICK_ACTIONS = [
  "Freeze writes and identify primary database writer",
  "Fail over database immediately",
  "Restart checkout service",
  "Escalate to database lead and incident command",
  "Correlate traces across checkout, orders, and database",
];


export function TimeTravelReplay() {
  const {
    session,
    replayBranch,
    selectedDecisionNodeId,
    isBranching,
    setSelectedDecisionNode,
    branchFromDecision,
  } = useWarRoomStore();
  const [alternativeAction, setAlternativeAction] = useState(QUICK_ACTIONS[0]);
  const decisionNodes = session?.timeline.nodes.filter((node) => node.turn_number > 0) ?? [];

  useEffect(() => {
    if (!selectedDecisionNodeId && decisionNodes[0]) {
      setSelectedDecisionNode(decisionNodes[0].node_id);
    }
  }, [decisionNodes, selectedDecisionNodeId, setSelectedDecisionNode]);

  return (
    <section className="war-panel replay-panel">
      <div className="panel-header">
        <div>
          <p className="panel-kicker">Deterministic replay projection</p>
          <h2 className="panel-title">Time-Travel Replay</h2>
        </div>
        <GitBranch className="h-5 w-5 text-cyan-300" />
      </div>

      <div className="replay-controls">
        <label className="technical-field">
          <span>Selected decision node</span>
          <select
            value={selectedDecisionNodeId ?? ""}
            onChange={(event) => setSelectedDecisionNode(event.target.value)}
            disabled={!decisionNodes.length || isBranching}
          >
            {!decisionNodes.length && <option value="">Run a simulation first</option>}
            {decisionNodes.map((node) => (
              <option key={node.node_id} value={node.node_id}>
                Turn {node.turn_number}: {node.decision_label}
              </option>
            ))}
          </select>
        </label>

        <label className="technical-field">
          <span>Alternative action</span>
          <input
            value={alternativeAction}
            onChange={(event) => setAlternativeAction(event.target.value)}
            disabled={isBranching}
          />
        </label>

        <div className="replay-quick-actions">
          {QUICK_ACTIONS.map((action) => (
            <button
              key={action}
              onClick={() => setAlternativeAction(action)}
              className={alternativeAction === action ? "quick-action quick-action-active" : "quick-action"}
            >
              {action}
            </button>
          ))}
        </div>

        <button
          onClick={() => void branchFromDecision(alternativeAction)}
          disabled={!session || !selectedDecisionNodeId || !alternativeAction.trim() || isBranching}
          className="control-button control-primary replay-submit"
        >
          {isBranching ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <GitBranch className="h-4 w-4" />}
          {isBranching ? "Projecting Branch" : "Branch From This Decision"}
        </button>
      </div>

      {replayBranch ? (
        <div className="replay-result">
          <div className="comparison-grid">
            <ComparisonCard
              label="Competence score"
              original={replayBranch.comparison.original_final_score.toFixed(1)}
              alternative={replayBranch.comparison.alternative_projected_score.toFixed(1)}
            />
            <ComparisonCard
              label="Max revenue at risk"
              original={formatCurrency(replayBranch.comparison.original_max_revenue_at_risk)}
              alternative={formatCurrency(replayBranch.comparison.alternative_revenue_at_risk)}
            />
            <ComparisonCard
              label="Final severity"
              original={`S${replayBranch.comparison.original_final_severity}`}
              alternative={`S${replayBranch.comparison.alternative_final_severity}`}
            />
          </div>
          <div className="replay-reasoning">
            <p>{replayBranch.comparison.reasoning_summary}</p>
            <span>{replayBranch.citations.length} cited evidence items</span>
          </div>
        </div>
      ) : (
        <div className="empty-state replay-empty">
          Select a saved decision and project an alternative path.
        </div>
      )}
    </section>
  );
}


function ComparisonCard({
  label,
  original,
  alternative,
}: {
  label: string;
  original: string;
  alternative: string;
}) {
  return (
    <div className="comparison-card">
      <p>{label}</p>
      <div>
        <span>Original</span>
        <strong>{original}</strong>
      </div>
      <div>
        <span>Alternative</span>
        <strong className="text-emerald-300">{alternative}</strong>
      </div>
    </div>
  );
}
