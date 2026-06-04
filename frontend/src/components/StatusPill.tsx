import { CheckCircle2, CircleAlert, Loader2 } from "lucide-react";

type StatusPillProps = {
  label: string;
  status?: "ok" | "warn" | "loading";
};

export function StatusPill({ label, status = "ok" }: StatusPillProps) {
  const styles = {
    ok: "border-signal/40 bg-signal/10 text-emerald-200",
    warn: "border-caution/40 bg-caution/10 text-amber-200",
    loading: "border-slate-500/40 bg-slate-500/10 text-slate-200",
  };
  const Icon = status === "ok" ? CheckCircle2 : status === "loading" ? Loader2 : CircleAlert;

  return (
    <span className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium ${styles[status]}`}>
      <Icon className={`h-3.5 w-3.5 ${status === "loading" ? "animate-spin" : ""}`} />
      {label}
    </span>
  );
}
