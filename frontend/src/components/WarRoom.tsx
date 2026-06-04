"use client";

import { useEffect } from "react";
import type { ReactNode } from "react";
import { motion } from "framer-motion";
import { Activity, Play, Radar, Shield } from "lucide-react";
import { useWarRoomStore } from "@/store/warRoomStore";
import { CompetenceGauge } from "@/components/CompetenceGauge";
import { CompetenceReport } from "@/components/CompetenceReport";
import { ManagerFragilityMap } from "@/components/ManagerFragilityMap";
import { RevenueTicker } from "@/components/RevenueTicker";
import { ScenarioFeed } from "@/components/ScenarioFeed";
import { SeverityMeter } from "@/components/SeverityMeter";
import { StatusPill } from "@/components/StatusPill";
import { TimelineGraph } from "@/components/TimelineGraph";

export function WarRoom() {
  const {
    health,
    session,
    latestReport,
    fragilityMap,
    readinessSummary,
    isLoading,
    error,
    initialize,
    runSreSimulation,
  } = useWarRoomStore();

  useEffect(() => {
    void initialize();
  }, [initialize]);

  const activeReport = session?.final_score ?? latestReport;
  const latestTurn = session?.turns.at(-1);
  const maxSeverity = session?.timeline.summary.max_severity ?? 0;
  const currentSeverity = latestTurn?.consequence.new_severity ?? session?.timeline.summary.final_severity ?? 0;
  const revenue = latestTurn?.consequence.revenue_at_risk ?? session?.timeline.summary.final_revenue_at_risk ?? 0;
  const revenueDelta = latestTurn?.consequence.revenue_delta ?? 0;
  const activeScore = activeReport
    ? "score" in activeReport && typeof activeReport.score === "number"
      ? activeReport.score
      : activeReport.overall_score
    : 0;

  return (
    <main className="min-h-screen bg-ink px-4 py-5 text-slate-100 md:px-6 xl:px-8">
      <section className="mb-5 rounded-lg border border-line bg-panel/80 p-5 shadow-soft-border">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="mb-3 flex flex-wrap items-center gap-2">
              <StatusPill label={health?.status === "ok" ? "Backend online" : "Backend unavailable"} status={health?.status === "ok" ? "ok" : isLoading ? "loading" : "warn"} />
              <StatusPill label="Synthetic data only" status="ok" />
              <StatusPill label="Grounded simulation" status="ok" />
            </div>
            <p className="text-xs uppercase tracking-[0.28em] text-slate-500">The Enterprise Holodeck</p>
            <h1 className="mt-1 text-4xl font-semibold tracking-normal text-white md:text-5xl">CRISOL</h1>
            <p className="mt-3 max-w-2xl text-base text-slate-300">Battle-test your team before the fire is real.</p>
          </div>

          <div className="flex flex-col gap-3 sm:flex-row">
            <button
              onClick={() => void runSreSimulation()}
              disabled={isLoading}
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-signal px-4 py-3 text-sm font-semibold text-ink transition hover:bg-emerald-300 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <Play className="h-4 w-4" />
              {isLoading ? "Running..." : "Run SRE Simulation"}
            </button>
            <div className="rounded-lg border border-line bg-ink/70 px-4 py-3 text-sm text-slate-300">
              <p className="text-xs uppercase tracking-wide text-slate-500">Readiness summary</p>
              <p className="mt-1">{readinessSummary ? `${readinessSummary.average_score.toFixed(1)} avg / ${readinessSummary.session_count} sessions` : "Awaiting first run"}</p>
            </div>
          </div>
        </div>
        {error && <p className="mt-4 rounded-md border border-danger/40 bg-danger/10 p-3 text-sm text-rose-200">{error}</p>}
      </section>

      <motion.section
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="grid gap-5 xl:grid-cols-[380px_minmax(0,1fr)_340px]"
      >
        <ScenarioFeed turns={session?.turns ?? []} />

        <div className="space-y-5">
          <TimelineGraph timeline={session?.timeline ?? null} />
          <section className="grid gap-5 md:grid-cols-3">
            <MiniSignal icon={<Radar className="h-5 w-5" />} label="Scenario" value={session?.scenario.title ?? "No active run"} />
            <MiniSignal icon={<Activity className="h-5 w-5" />} label="Timeline" value={`${session?.timeline.summary.total_nodes ?? 0} branch nodes`} />
            <MiniSignal icon={<Shield className="h-5 w-5" />} label="Report" value={activeReport ? activeReport.readiness_band : "Pending"} />
          </section>
        </div>

        <div className="space-y-5">
          <SeverityMeter severity={currentSeverity} maxSeverity={maxSeverity} />
          <RevenueTicker revenue={revenue} delta={revenueDelta} />
          <CompetenceGauge
            score={activeScore}
            band={activeReport?.readiness_band}
            topGap={session?.coach_plan.top_gap ?? activeReport?.skill_gaps?.[0]?.skill_id}
            failureModes={activeReport?.failure_modes ?? []}
          />
        </div>
      </motion.section>

      <section className="mt-5 grid gap-5 2xl:grid-cols-[minmax(0,1.15fr)_minmax(460px,0.85fr)]">
        <CompetenceReport report={activeReport ?? null} />
        <ManagerFragilityMap map={fragilityMap} />
      </section>
    </main>
  );
}

function MiniSignal({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <div className="rounded-lg border border-line bg-panel/80 p-4 shadow-soft-border">
      <div className="mb-3 text-slate-400">{icon}</div>
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 line-clamp-2 text-sm font-medium text-white">{value}</p>
    </div>
  );
}
