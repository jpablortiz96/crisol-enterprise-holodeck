import { TrendingDown, TrendingUp } from "lucide-react";
import { formatCurrency, formatDelta } from "@/lib/format";

type RevenueTickerProps = {
  revenue?: number;
  delta?: number;
};

export function RevenueTicker({ revenue = 0, delta = 0 }: RevenueTickerProps) {
  const positive = delta > 0;

  return (
    <section className="rounded-lg border border-line bg-panel/80 p-4 shadow-soft-border">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-400">Revenue at risk</p>
          <p className="mt-1 text-2xl font-semibold text-white">{formatCurrency(revenue)}</p>
        </div>
        {positive ? <TrendingUp className="h-7 w-7 text-danger" /> : <TrendingDown className="h-7 w-7 text-signal" />}
      </div>
      <p className={`mt-3 text-sm ${positive ? "text-rose-200" : "text-emerald-200"}`}>
        {formatDelta(delta)} from previous branch
      </p>
    </section>
  );
}
