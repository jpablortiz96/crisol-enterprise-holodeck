"use client";

import { AnimatePresence, motion } from "framer-motion";
import {
  AlertOctagon,
  BookOpenCheck,
  ChevronRight,
  MessageSquareWarning,
} from "lucide-react";
import type { TurnRecord } from "@/lib/types";
import { formatCurrency, formatDelta } from "@/lib/format";

type ScenarioFeedProps = {
  turns: TurnRecord[];
  activeTurnNumber?: number;
};

export function ScenarioFeed({ turns, activeTurnNumber }: ScenarioFeedProps) {
  return (
    <section className="war-panel scenario-feed-panel p-4">
      <div className="panel-header">
        <div>
          <p className="panel-kicker">Grounded simulation</p>
          <h2 className="panel-title">Turn-by-Turn Incident Log</h2>
        </div>
        <MessageSquareWarning className="h-5 w-5 text-amber-300" />
      </div>

      <div className="scenario-feed-scroll">
        <AnimatePresence initial={false}>
          {turns.map((turn) => {
            const active = activeTurnNumber === turn.turn_number;
            const cascadeDetected =
              turn.consequence.newly_affected_systems.length > 0 ||
              turn.consequence.cascade_paths.length > 0;

            return (
              <motion.article
                key={turn.turn_number}
                layout
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.24 }}
                className={`turn-record ${active ? "turn-active" : ""} ${
                  turn.turn_number === 1 && cascadeDetected ? "turn-critical" : ""
                }`}
              >
                <div className="turn-index">
                  <span>{String(turn.turn_number).padStart(2, "0")}</span>
                  <div className="turn-line" />
                </div>

                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div>
                      <p className="text-[10px] uppercase text-slate-500">Operational turn</p>
                      <h3 className="line-clamp-2 break-words text-sm font-semibold text-white">
                        {turn.decision.id === "pending" ? "Awaiting decision" : turn.decision.label}
                      </h3>
                    </div>
                    <div className="flex items-center gap-2">
                      {active && <span className="live-chip">Live</span>}
                      <span className="severity-chip">S{turn.consequence.new_severity || "-"}</span>
                    </div>
                  </div>

                  <p className="mt-3 line-clamp-3 break-words text-sm leading-6 text-slate-300">
                    {turn.situation}
                  </p>

                  <div className="decision-strip">
                    <ChevronRight className="h-4 w-4 shrink-0 text-cyan-300" />
                    <span>{turn.decision.description}</span>
                  </div>

                  {turn.consequence.world_delta !== "Awaiting consequence update." && (
                    <div className="mt-3 flex gap-3 border-l-2 border-amber-300/70 bg-amber-300/[0.04] p-3">
                      <AlertOctagon className="mt-0.5 h-4 w-4 shrink-0 text-amber-300" />
                      <p className="text-xs leading-5 text-slate-300">{turn.consequence.world_delta}</p>
                    </div>
                  )}

                  <div className="mt-3 grid gap-2 sm:grid-cols-3">
                    <TurnMetric label="Revenue at risk" value={formatCurrency(turn.consequence.revenue_at_risk)} />
                    <TurnMetric label="Revenue delta" value={formatDelta(turn.consequence.revenue_delta)} danger={turn.consequence.revenue_delta > 0} />
                    <TurnMetric label="Cited evidence" value={String(turn.citations.length)} />
                  </div>

                  <div className="mt-3 flex flex-wrap gap-1.5">
                    {cascadeDetected && <SignalBadge label="Cascade detected" danger />}
                    {turn.consequence.newly_affected_systems.slice(0, 3).map((system) => (
                      <SignalBadge key={system} label={system} />
                    ))}
                    {turn.citations.length > 0 && (
                      <span className="inline-flex items-center gap-1 text-[10px] text-slate-500">
                        <BookOpenCheck className="h-3 w-3" />
                        grounded
                      </span>
                    )}
                  </div>

                  {turn.npc_reactions.length > 0 && (
                    <div className="mt-4 grid gap-2 lg:grid-cols-2">
                      {turn.npc_reactions.map((reaction) => (
                        <div key={`${turn.turn_number}-${reaction.persona}`} className="npc-reaction-line">
                          <div className="flex items-center justify-between gap-2">
                            <div className="min-w-0">
                              <p className="text-[11px] font-semibold text-white">{reaction.persona}</p>
                              <p className="truncate text-[9px] text-slate-600">
                                {reaction.role} / {reaction.communication_style}
                              </p>
                            </div>
                            <span className="text-[9px] uppercase text-slate-600">
                              {reaction.voice?.provider === "azure-speech" ? "Azure Speech" : "Text fallback"}
                            </span>
                          </div>
                          <p className="mt-1 line-clamp-2 text-[11px] leading-4 text-slate-400">
                            {reaction.message}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </motion.article>
            );
          })}
        </AnimatePresence>

        {!turns.length && (
          <div className="empty-state">
            Run or stream a simulation to create the operational incident log.
          </div>
        )}
      </div>
    </section>
  );
}

function TurnMetric({ label, value, danger = false }: { label: string; value: string; danger?: boolean }) {
  return (
    <div className="turn-metric">
      <p className="text-[9px] uppercase text-slate-600">{label}</p>
      <p className={`mt-1 text-xs font-semibold ${danger ? "text-rose-300" : "text-slate-200"}`}>{value}</p>
    </div>
  );
}

function SignalBadge({ label, danger = false }: { label: string; danger?: boolean }) {
  return <span className={danger ? "signal-badge signal-danger" : "signal-badge"}>{label}</span>;
}
