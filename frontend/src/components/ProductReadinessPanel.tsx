"use client";

import { Activity, Database, ShieldCheck } from "lucide-react";
import type { ReactNode } from "react";
import { useWarRoomStore } from "@/store/warRoomStore";


export function ProductReadinessPanel() {
  const { scenarios, telemetrySummary } = useWarRoomStore();

  return (
    <section className="war-panel product-readiness-panel">
      <div className="panel-header">
        <div>
          <p className="panel-kicker">Operational assurance</p>
          <h2 className="panel-title">Product Readiness</h2>
        </div>
        <ShieldCheck className="h-5 w-5 text-emerald-300" />
      </div>

      <div className="readiness-metric-grid">
        <ReadinessMetric
          icon={<Activity className="h-4 w-4" />}
          label="Evaluation"
          value={
            telemetrySummary?.evaluation_score !== null
              && telemetrySummary?.evaluation_score !== undefined
              ? `${telemetrySummary.evaluation_status} / ${telemetrySummary.evaluation_score}`
              : telemetrySummary?.evaluation_status ?? "Pending"
          }
        />
        <ReadinessMetric
          icon={<Database className="h-4 w-4" />}
          label="Scenarios"
          value={String(scenarios.length)}
        />
        <ReadinessMetric
          icon={<Activity className="h-4 w-4" />}
          label="Recent events"
          value={String(telemetrySummary?.event_count ?? 0)}
        />
        <ReadinessMetric
          icon={<ShieldCheck className="h-4 w-4" />}
          label="Data mode"
          value="Sanitized training"
        />
      </div>

      <div className="production-boundary">
        <ShieldCheck className="h-4 w-4" />
        <span>No production changes</span>
      </div>
    </section>
  );
}


function ReadinessMetric({
  icon,
  label,
  value,
}: {
  icon: ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="readiness-metric">
      <span>{icon}</span>
      <div>
        <p>{label}</p>
        <strong>{value}</strong>
      </div>
    </div>
  );
}
