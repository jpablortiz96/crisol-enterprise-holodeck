"use client";

import { BookOpenCheck } from "lucide-react";
import { CompetenceReport } from "@/components/CompetenceReport";
import { ManagerFragilityMap } from "@/components/ManagerFragilityMap";
import { TimeTravelReplay } from "@/components/TimeTravelReplay";
import { useWarRoomStore } from "@/store/warRoomStore";

export function ResultsCenterPage() {
  const { session, latestSession, latestReport, fragilityMap } = useWarRoomStore();
  const resultSession = session ?? latestSession;
  const activeReport = resultSession?.final_score?.overall_score ? resultSession.final_score : latestReport;

  return (
    <section className="product-page results-page">
      <header className="page-header">
        <p>Evidence and coaching</p>
        <h2>Results Center</h2>
        <span>Review competence evidence, skill gaps, coaching actions, certification alignment, and alternative decision branches.</span>
      </header>

      <section className="results-session-bar">
        <BookOpenCheck className="h-5 w-5" />
        <div>
          <span>Latest session</span>
          <strong>{resultSession?.scenario.title ?? activeReport?.session_id ?? "No completed evaluation"}</strong>
        </div>
      </section>

      <CompetenceReport report={activeReport} />

      <section className="war-panel coach-plan-panel">
        <div className="panel-header">
          <div><p className="panel-kicker">Targeted development</p><h2 className="panel-title">Coach Plan</h2></div>
        </div>
        {!resultSession?.coach_plan.micro_plan.length ? (
          <div className="empty-state">Complete an evaluation to generate a coach plan.</div>
        ) : (
          <div className="coach-plan-grid">
            {resultSession.coach_plan.micro_plan.map((item) => (
              <article key={item.step}>
                <span>{item.step}</span>
                <div><strong>{item.title}</strong><p>{item.activity}</p><small>{item.success_criteria}</small></div>
              </article>
            ))}
          </div>
        )}
      </section>

      <div className="results-analysis-grid">
        <ManagerFragilityMap map={fragilityMap} />
        <TimeTravelReplay />
      </div>
    </section>
  );
}
