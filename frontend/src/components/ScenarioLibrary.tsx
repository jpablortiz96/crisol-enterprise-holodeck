"use client";

import { BookOpenCheck, Check, Clock3, ShieldCheck } from "lucide-react";
import { useWarRoomStore } from "@/store/warRoomStore";


export function ScenarioLibrary() {
  const {
    scenarios,
    selectedScenarioId,
    streamStatus,
    selectScenario,
  } = useWarRoomStore();

  return (
    <section className="war-panel scenario-library-panel">
      <div className="panel-header">
        <div>
          <p className="panel-kicker">Sanitized training data</p>
          <h2 className="panel-title">Scenario Library</h2>
        </div>
        <BookOpenCheck className="h-5 w-5 text-cyan-300" />
      </div>

      <div className="scenario-library-list">
        {scenarios.map((scenario) => {
          const selected = selectedScenarioId === scenario.scenario_id;
          return (
            <button
              key={scenario.scenario_id}
              onClick={() => selectScenario(scenario.scenario_id)}
              disabled={streamStatus === "live"}
              className={selected ? "scenario-library-item scenario-library-selected" : "scenario-library-item"}
              aria-pressed={selected}
            >
              <span className="scenario-select-icon">
                {selected ? <Check className="h-3.5 w-3.5" /> : <ShieldCheck className="h-3.5 w-3.5" />}
              </span>
              <span className="min-w-0 flex-1">
                <strong>{scenario.title}</strong>
                <span>{scenario.industry} · {scenario.role_id}</span>
              </span>
              <span className="scenario-library-meta">
                <span>{scenario.difficulty}</span>
                <span><Clock3 className="h-3 w-3" /> {scenario.estimated_minutes} min</span>
              </span>
            </button>
          );
        })}
        {!scenarios.length && (
          <div className="empty-state">Scenario Library is unavailable.</div>
        )}
      </div>
    </section>
  );
}
