"use client";

import { motion } from "framer-motion";
import { ShieldAlert, TriangleAlert } from "lucide-react";

type SeverityMeterProps = {
  severity?: number;
  maxSeverity?: number;
};

export function SeverityMeter({ severity = 0, maxSeverity = 0 }: SeverityMeterProps) {
  return (
    <section className="war-panel metric-panel">
      <div className="flex items-center justify-between">
        <div>
          <p className="panel-kicker">Incident severity</p>
          <motion.p
            key={severity}
            initial={{ opacity: 0.6, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-1 text-4xl font-semibold text-white"
          >
            {severity || "-"}
            <span className="text-lg text-slate-600">/5</span>
          </motion.p>
        </div>
        <div className={`metric-icon ${severity >= 4 ? "metric-icon-danger" : ""}`}>
          <ShieldAlert className="h-5 w-5" />
        </div>
      </div>
      <div className="mt-5 grid grid-cols-5 gap-1.5">
        {[1, 2, 3, 4, 5].map((level) => (
          <motion.span
            key={level}
            animate={{ opacity: level <= severity ? 1 : 0.18 }}
            className={`h-2 rounded-sm ${
              level >= 4 ? "bg-rose-400" : level === 3 ? "bg-amber-300" : "bg-cyan-300"
            }`}
          />
        ))}
      </div>
      <div className="mt-4 flex items-center justify-between text-xs">
        <span className="flex items-center gap-1.5 text-slate-500">
          <TriangleAlert className="h-3.5 w-3.5" />
          Peak observed
        </span>
        <span className="font-semibold text-slate-200">S{maxSeverity || "-"}</span>
      </div>
    </section>
  );
}
