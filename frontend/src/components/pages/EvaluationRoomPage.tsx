"use client";

import {
  CirclePause,
  Gauge,
  Play,
  Radio,
  RotateCcw,
  Volume2,
  VolumeX,
} from "lucide-react";
import { CompetenceGauge } from "@/components/CompetenceGauge";
import { LiveEventRail } from "@/components/LiveEventRail";
import { NpcStage } from "@/components/NpcStage";
import { RevenueTicker } from "@/components/RevenueTicker";
import { ScenarioFeed } from "@/components/ScenarioFeed";
import { ScenarioLibrary } from "@/components/ScenarioLibrary";
import { SeverityMeter } from "@/components/SeverityMeter";
import { TimelineGraph } from "@/components/TimelineGraph";
import { useWarRoomStore } from "@/store/warRoomStore";
import type { PlaybackSpeed } from "@/lib/types";

const PLAYBACK_SPEEDS: PlaybackSpeed[] = [0.75, 1, 1.25];

export function EvaluationRoomPage() {
  const {
    session,
    latestReport,
    scenarios,
    selectedScenarioId,
    selectedProfileId,
    workspaceProfiles,
    voiceStatus,
    voiceEnabled,
    receivedEvents,
    liveEvents,
    activeEvent,
    speakingPersona,
    streamStatus,
    playbackStatus,
    playbackSpeed,
    isLoading,
    runSreSimulation,
    playLiveSimulation,
    pausePlayback,
    resumePlayback,
    replaySession,
    setPlaybackSpeed,
    toggleVoice,
    selectProfile,
    goToResults,
  } = useWarRoomStore();
  const selectedScenario = scenarios.find((item) => item.scenario_id === selectedScenarioId);
  const currentTurn = session?.turns.at(-1);
  const report = session?.final_score?.overall_score ? session.final_score : latestReport;
  const activeScore = report?.overall_score ?? 0;
  const activeTurnNumber = activeEvent?.data.turn_number
    ? Number(activeEvent.data.turn_number)
    : currentTurn?.turn_number;
  const bufferedCount = Math.max(0, receivedEvents.length - liveEvents.length);
  const currentSeverity = currentTurn?.consequence.new_severity ?? session?.timeline.summary.final_severity ?? 0;
  const maxSeverity = session?.timeline.summary.max_severity ?? 0;
  const revenue = currentTurn?.consequence.revenue_at_risk ?? session?.timeline.summary.final_revenue_at_risk ?? 0;
  const playbackBusy = ["buffering", "playing", "paused"].includes(playbackStatus);

  return (
    <section className="product-page evaluation-page">
      <header className="page-header">
        <p>Candidate evaluation</p>
        <h2>Incident room</h2>
        <span>Run the selected scenario with scenario-driven personas, synchronized consequences, and optional Azure Speech.</span>
      </header>

      <section className="evaluation-control-bar">
        <label>
          Scenario
          <strong>{selectedScenario?.title ?? "Create or select a scenario"}</strong>
        </label>
        <label className="technical-field evaluation-profile-select">
          Evaluated profile
          <select value={selectedProfileId ?? ""} onChange={(event) => selectProfile(event.target.value)}>
            <option value="">Select profile</option>
            {workspaceProfiles.map((profile) => <option key={profile.profile_id} value={profile.profile_id}>{profile.display_name}</option>)}
          </select>
        </label>
        <div className="evaluation-actions">
          <button className="control-button control-secondary" disabled={!selectedScenario || isLoading || playbackBusy} onClick={() => void runSreSimulation()}>
            <Play className="h-4 w-4" /> {isLoading ? "Running" : "Run Evaluation"}
          </button>
          <button className="control-button control-primary" disabled={!selectedScenario || playbackBusy} onClick={playLiveSimulation}>
            <Radio className="h-4 w-4" /> Play Live Simulation
          </button>
          {playbackStatus === "paused"
            ? <button className="icon-control" onClick={resumePlayback} title="Resume"><Play className="h-4 w-4" /></button>
            : <button className="icon-control" disabled={!["playing", "buffering"].includes(playbackStatus)} onClick={pausePlayback} title="Pause"><CirclePause className="h-4 w-4" /></button>}
          <button className="icon-control" disabled={!receivedEvents.length || playbackStatus !== "completed"} onClick={replaySession} title="Replay"><RotateCcw className="h-4 w-4" /></button>
          <button className="icon-control" onClick={toggleVoice} title={voiceEnabled ? "Voice off" : "Voice on"}>
            {voiceEnabled ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
          </button>
          <div className="speed-control">
            {PLAYBACK_SPEEDS.map((speed) => (
              <button key={speed} className={playbackSpeed === speed ? "speed-option speed-active" : "speed-option"} onClick={() => setPlaybackSpeed(speed)}>{speed}x</button>
            ))}
          </div>
        </div>
      </section>

      {!selectedScenario && <div className="scenario-required-banner">Create or select a scenario before starting an evaluation.</div>}
      <ScenarioLibrary />

      <div className="evaluation-grid">
        <aside className="evaluation-left">
          <LiveEventRail events={liveEvents} playbackStatus={playbackStatus} activeSequence={activeEvent?.sequence} bufferedCount={bufferedCount} />
        </aside>
        <div className="evaluation-center">
          <NpcStage
            personas={session?.scenario.personas ?? selectedScenario?.personas ?? []}
            activeEvent={activeEvent}
            speakingPersona={speakingPersona}
            currentTurn={currentTurn}
            playbackStatus={playbackStatus}
            voiceStatus={voiceStatus}
            voiceEnabled={voiceEnabled}
          />
          <TimelineGraph timeline={session?.timeline ?? null} />
          <ScenarioFeed turns={session?.turns ?? []} activeTurnNumber={activeTurnNumber} />
        </div>
        <aside className="evaluation-right">
          <div className="rail-heading"><Gauge className="h-4 w-4 text-cyan-300" /> Operational stakes</div>
          <SeverityMeter severity={currentSeverity} maxSeverity={maxSeverity} />
          <RevenueTicker revenue={revenue} delta={currentTurn?.consequence.revenue_delta ?? 0} />
          <CompetenceGauge
            score={activeScore}
            band={report?.readiness_band}
            topGap={session?.coach_plan.top_gap ?? report?.skill_gaps?.[0]?.skill_id}
            evidenceCount={report?.evidence_trail.length ?? 0}
            failureModes={report?.failure_modes ?? []}
          />
          {session && report && activeScore > 0 && (
            <button className="control-button control-primary evaluation-results-button" onClick={goToResults}>
              View Full Results
            </button>
          )}
          <div className="evaluation-status-card">
            <span>Stream</span><strong>{streamStatus}</strong>
            <span>Playback</span><strong>{playbackStatus}</strong>
          </div>
        </aside>
      </div>
    </section>
  );
}
