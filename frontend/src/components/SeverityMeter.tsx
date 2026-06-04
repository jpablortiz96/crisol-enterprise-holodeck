import { ShieldAlert } from "lucide-react";

type SeverityMeterProps = {
  severity?: number;
  maxSeverity?: number;
};

export function SeverityMeter({ severity = 0, maxSeverity = 0 }: SeverityMeterProps) {
  const percentage = Math.min(100, Math.max(0, severity * 20));

  return (
    <section className="rounded-lg border border-line bg-panel/80 p-4 shadow-soft-border">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-400">Severity</p>
          <p className="mt-1 text-2xl font-semibold text-white">{severity || "-"}/5</p>
        </div>
        <ShieldAlert className="h-7 w-7 text-caution" />
      </div>
      <div className="mt-4 h-2 rounded-full bg-slate-800">
        <div className="h-2 rounded-full bg-caution" style={{ width: `${percentage}%` }} />
      </div>
      <p className="mt-3 text-xs text-slate-400">Peak severity: {maxSeverity || "-"}</p>
    </section>
  );
}
