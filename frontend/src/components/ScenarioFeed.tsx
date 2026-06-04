import { MessageSquareWarning } from "lucide-react";
import type { TurnRecord } from "@/lib/types";
import { formatCurrency, formatDelta } from "@/lib/format";

type ScenarioFeedProps = {
  turns: TurnRecord[];
};

export function ScenarioFeed({ turns }: ScenarioFeedProps) {
  return (
    <section className="rounded-lg border border-line bg-panel/80 p-4 shadow-soft-border">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-400">Grounded simulation</p>
          <h2 className="text-lg font-semibold text-white">Scenario Feed</h2>
        </div>
        <MessageSquareWarning className="h-5 w-5 text-caution" />
      </div>
      <div className="max-h-[650px] space-y-3 overflow-y-auto pr-1">
        {turns.map((turn) => (
          <article key={turn.turn_number} className="rounded-lg border border-line bg-ink/60 p-3">
            <div className="flex items-center justify-between gap-3">
              <p className="text-sm font-semibold text-white">Turn {turn.turn_number}</p>
              <span className="rounded-full border border-slate-600 px-2 py-0.5 text-[11px] text-slate-300">
                Severity {turn.consequence.new_severity}
              </span>
            </div>
            <p className="mt-2 text-sm leading-6 text-slate-300">{turn.situation}</p>
            <div className="mt-3 rounded-md border border-caution/30 bg-caution/10 p-2">
              <p className="text-xs uppercase tracking-wide text-amber-200">Decision taken</p>
              <p className="mt-1 text-sm text-white">{turn.decision.label}</p>
            </div>
            <p className="mt-3 text-sm text-slate-200">{turn.consequence.world_delta}</p>
            <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
              <span className="rounded-md bg-slate-900/80 p-2 text-slate-300">
                Risk {formatCurrency(turn.consequence.revenue_at_risk)}
              </span>
              <span className="rounded-md bg-slate-900/80 p-2 text-slate-300">
                Delta {formatDelta(turn.consequence.revenue_delta)}
              </span>
            </div>
            <div className="mt-3 space-y-2">
              {turn.npc_reactions.slice(0, 3).map((reaction) => (
                <div key={`${turn.turn_number}-${reaction.persona}`} className="rounded-md bg-slate-950/60 p-2">
                  <p className="text-xs font-medium text-slate-100">{reaction.persona}</p>
                  <p className="mt-1 text-xs leading-5 text-slate-400">{reaction.message}</p>
                </div>
              ))}
            </div>
          </article>
        ))}
        {!turns.length && (
          <div className="rounded-lg border border-dashed border-slate-700 p-5 text-sm text-slate-400">
            Run a simulation to generate the first competence report.
          </div>
        )}
      </div>
    </section>
  );
}
