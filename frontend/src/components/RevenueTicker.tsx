"use client";

import { motion } from "framer-motion";
import { TrendingDown, TrendingUp } from "lucide-react";
import { formatCurrency, formatDelta } from "@/lib/format";

type RevenueTickerProps = {
  revenue?: number;
  delta?: number;
};

export function RevenueTicker({ revenue = 0, delta = 0 }: RevenueTickerProps) {
  const increased = delta > 0;

  return (
    <section className="war-panel metric-panel">
      <div className="flex items-center justify-between gap-3">
        <div className="min-w-0">
          <p className="panel-kicker">Revenue at risk</p>
          <motion.p
            key={revenue}
            initial={{ opacity: 0.6, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-1 truncate text-3xl font-semibold text-white"
          >
            {formatCurrency(revenue)}
          </motion.p>
        </div>
        <div className={`metric-icon ${increased ? "metric-icon-danger" : "metric-icon-ok"}`}>
          {increased ? <TrendingUp className="h-5 w-5" /> : <TrendingDown className="h-5 w-5" />}
        </div>
      </div>
      <motion.div
        key={delta}
        initial={{ opacity: 0.6, y: 4 }}
        animate={{ opacity: 1, y: 0 }}
        className={`mt-5 border-l-2 pl-3 ${
          increased ? "border-rose-400 text-rose-200" : "border-emerald-400 text-emerald-200"
        }`}
      >
        <p className="text-[9px] uppercase text-slate-600">Revenue delta</p>
        <p className="mt-1 text-sm font-semibold">{formatDelta(delta)}</p>
      </motion.div>
    </section>
  );
}
