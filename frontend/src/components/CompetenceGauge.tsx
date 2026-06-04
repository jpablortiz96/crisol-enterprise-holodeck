import { Gauge } from "lucide-react";
import { bandLabel } from "@/lib/format";

type CompetenceGaugeProps = {
  score?: number;
  band?: string;
  topGap?: string;
  failureModes?: Array<{ mode_id: string; description: string }>;
};

export function CompetenceGauge({ score = 0, band, topGap, failureModes = [] }: CompetenceGaugeProps) {
  const stroke = Math.min(100, Math.max(0, score));

  return (
    <section className="rounded-lg border border-line bg-panel/80 p-4 shadow-soft-border">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-400">Competence Score</p>
          <p className="mt-1 text-3xl font-semibold text-white">{score ? score.toFixed(1) : "--"}</p>
        </div>
        <Gauge className="h-7 w-7 text-signal" />
      </div>
      <div className="mt-4 h-2 rounded-full bg-slate-800">
        <div className="h-2 rounded-full bg-signal" style={{ width: `${stroke}%` }} />
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500">Band</p>
          <p className="font-medium text-slate-100">{bandLabel(band)}</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500">Top gap</p>
          <p className="font-medium text-slate-100">{topGap || "No run yet"}</p>
        </div>
      </div>
      <div className="mt-4">
        <p className="text-xs uppercase tracking-wide text-slate-500">Latest failure modes</p>
        <ul className="mt-2 space-y-2 text-xs text-slate-300">
          {failureModes.slice(0, 3).map((mode) => (
            <li key={mode.mode_id} className="rounded-md border border-line bg-ink/60 p-2">
              {mode.description}
            </li>
          ))}
          {!failureModes.length && <li className="text-slate-500">Run a simulation to populate evidence.</li>}
        </ul>
      </div>
    </section>
  );
}
