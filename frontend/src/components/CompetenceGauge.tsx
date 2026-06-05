"use client";

import { motion } from "framer-motion";
import { Gauge } from "lucide-react";
import { bandLabel } from "@/lib/format";

type CompetenceGaugeProps = {
  score?: number;
  band?: string;
  topGap?: string;
  evidenceCount?: number;
  failureModes?: Array<{ mode_id: string; description: string }>;
};

export function CompetenceGauge({
  score = 0,
  band,
  topGap,
  evidenceCount = 0,
  failureModes = [],
}: CompetenceGaugeProps) {
  const stroke = Math.min(100, Math.max(0, score));

  return (
    <section className="war-panel metric-panel">
      <div className="flex items-center justify-between">
        <div>
          <p className="panel-kicker">Competence Score</p>
          <motion.p
            key={score}
            initial={{ opacity: 0.6, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mt-1 text-4xl font-semibold text-white"
          >
            {score ? score.toFixed(1) : "--"}
          </motion.p>
        </div>
        <div className="metric-icon metric-icon-ok">
          <Gauge className="h-5 w-5" />
        </div>
      </div>
      <div className="mt-5 h-1.5 rounded-full bg-white/5">
        <motion.div
          className="h-full rounded-full bg-emerald-300"
          animate={{ width: `${stroke}%` }}
          transition={{ duration: 0.35 }}
        />
      </div>
      <div className="mt-5 grid grid-cols-3 gap-3 border-t border-white/5 pt-4">
        <GaugeDetail label="Readiness band" value={bandLabel(band)} />
        <GaugeDetail label="Top gap" value={topGap || "No run yet"} />
        <GaugeDetail label="Cited evidence" value={String(evidenceCount)} />
      </div>
      <div className="mt-5">
        <p className="text-[9px] uppercase text-slate-600">Failure modes</p>
        <ul className="mt-2 space-y-2 text-[11px] leading-4 text-slate-400">
          {failureModes.slice(0, 3).map((mode) => (
            <li key={mode.mode_id} className="border-l-2 border-rose-400/50 bg-rose-400/[0.03] p-2">
              {mode.description}
            </li>
          ))}
          {!failureModes.length && <li className="text-slate-600">Assessment pending.</li>}
        </ul>
      </div>
    </section>
  );
}

function GaugeDetail({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0">
      <p className="text-[9px] uppercase text-slate-600">{label}</p>
      <p className="mt-1 line-clamp-2 text-xs font-medium text-slate-100">{value}</p>
    </div>
  );
}
