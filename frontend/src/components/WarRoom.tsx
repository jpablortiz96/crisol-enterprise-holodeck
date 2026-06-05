"use client";

import { useEffect } from "react";
import { motion } from "framer-motion";
import {
  Activity,
  CirclePause,
  Gauge,
  Play,
  Radio,
  RotateCcw,
  ShieldCheck,
  Volume2,
  VolumeX,
} from "lucide-react";
import { useWarRoomStore } from "@/store/warRoomStore";
import type { PlaybackSpeed } from "@/lib/types";
import { CompetenceGauge } from "@/components/CompetenceGauge";
import { CompetenceReport } from "@/components/CompetenceReport";
import { LiveEventRail } from "@/components/LiveEventRail";
import { ManagerFragilityMap } from "@/components/ManagerFragilityMap";
import { NpcStage } from "@/components/NpcStage";
import { RevenueTicker } from "@/components/RevenueTicker";
import { ScenarioFeed } from "@/components/ScenarioFeed";
import { SeverityMeter } from "@/components/SeverityMeter";
import { StatusPill } from "@/components/StatusPill";
import { TimelineGraph } from "@/components/TimelineGraph";

const PLAYBACK_SPEEDS: PlaybackSpeed[] = [0.75, 1, 1.25];

export function WarRoom() {
  const {
    health,
    session,
    latestReport,
    fragilityMap,
    readinessSummary,
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
    error,
    initialize,
    runSreSimulation,
    playLiveSimulation,
    pausePlayback,
    resumePlayback,
    replaySession,
    setPlaybackSpeed,
    toggleVoice,
  } = useWarRoomStore();

  useEffect(() => {
    void initialize();
  }, [initialize]);

  const currentTurn = session?.turns.at(-1);
  const reportReady = Boolean(session?.final_score.overall_score);
  const activeReport = reportReady ? session?.final_score ?? null : playbackStatus === "idle" ? latestReport : null;
  const maxSeverity = session?.timeline.summary.max_severity ?? 0;
  const currentSeverity = currentTurn?.consequence.new_severity ?? session?.timeline.summary.final_severity ?? 0;
  const revenue = currentTurn?.consequence.revenue_at_risk ?? session?.timeline.summary.final_revenue_at_risk ?? 0;
  const revenueDelta = currentTurn?.consequence.revenue_delta ?? 0;
  const activeScore = activeReport
    ? "score" in activeReport && typeof activeReport.score === "number"
      ? activeReport.score
      : activeReport.overall_score
    : 0;
  const playbackBusy = ["buffering", "playing", "paused"].includes(playbackStatus);
  const bufferedCount = Math.max(0, receivedEvents.length - liveEvents.length);
  const playbackProgress = receivedEvents.length
    ? Math.round((liveEvents.length / receivedEvents.length) * 100)
    : 0;
  const activeTurnNumber = activeEvent?.data.turn_number
    ? Number(activeEvent.data.turn_number)
    : currentTurn?.turn_number;

  return (
    <main className="war-room-shell">
      <header className="command-header">
        <div className="command-brand">
          <div className="brand-mark">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-semibold text-white md:text-3xl">CRISOL</h1>
              <span className="hidden text-[10px] uppercase text-slate-500 sm:inline">Enterprise Holodeck</span>
            </div>
            <p className="text-sm text-slate-400">Battle-test your team before the fire is real.</p>
          </div>
        </div>

        <div className="command-status">
          <StatusPill
            label={health?.status === "ok" ? "Backend online" : "Backend unavailable"}
            status={health?.status === "ok" ? "ok" : isLoading ? "loading" : "warn"}
          />
          <StatusPill
            label={
              voiceStatus.configured
                ? voiceEnabled
                  ? "Azure Speech active"
                  : "Voice muted"
                : "Text fallback active"
            }
            status={voiceStatus.configured && voiceEnabled ? "ok" : "warn"}
          />
          <StatusPill label={`Playback ${playbackStatus}`} status={playbackStatusTone(playbackStatus)} />
        </div>

        <div className="command-controls">
          <button
            onClick={() => void runSreSimulation()}
            disabled={isLoading || playbackBusy}
            className="control-button control-secondary"
          >
            <Play className="h-4 w-4" />
            {isLoading ? "Running" : "Run"}
          </button>
          <button
            onClick={playLiveSimulation}
            disabled={playbackBusy}
            className="control-button control-primary"
          >
            <Radio className="h-4 w-4" />
            Play Live Simulation
          </button>
          {playbackStatus === "paused" ? (
            <button onClick={resumePlayback} className="icon-control" title="Resume Playback">
              <Play className="h-4 w-4" />
              <span className="sr-only">Resume Playback</span>
            </button>
          ) : (
            <button
              onClick={pausePlayback}
              disabled={!["playing", "buffering"].includes(playbackStatus)}
              className="icon-control"
              title="Pause Playback"
            >
              <CirclePause className="h-4 w-4" />
              <span className="sr-only">Pause Playback</span>
            </button>
          )}
          <button
            onClick={replaySession}
            disabled={!receivedEvents.length || playbackStatus !== "completed"}
            className="icon-control"
            title="Replay Session"
          >
            <RotateCcw className="h-4 w-4" />
            <span className="sr-only">Replay Session</span>
          </button>
          <button
            onClick={toggleVoice}
            className="icon-control"
            title={voiceEnabled ? "Turn Voice Off" : "Turn Voice On"}
            aria-pressed={voiceEnabled}
          >
            {voiceEnabled ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
            <span className="sr-only">Voice: {voiceEnabled ? "On" : "Off"}</span>
          </button>
          <div className="speed-control" aria-label="Playback speed">
            {PLAYBACK_SPEEDS.map((speed) => (
              <button
                key={speed}
                onClick={() => setPlaybackSpeed(speed)}
                className={playbackSpeed === speed ? "speed-option speed-active" : "speed-option"}
              >
                {speed}x
              </button>
            ))}
          </div>
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <section className="war-room-grid">
        <aside className="left-rail">
          <SessionSummary
            title={session?.scenario.title}
            roleId={session?.scenario.role_id}
            sessionId={session?.session_id}
            streamStatus={streamStatus}
            playbackStatus={playbackStatus}
            bufferedCount={bufferedCount}
            progress={playbackProgress}
            readiness={readinessSummary?.average_score}
          />
          <LiveEventRail
            events={liveEvents}
            playbackStatus={playbackStatus}
            activeSequence={activeEvent?.sequence}
            bufferedCount={bufferedCount}
          />
        </aside>

        <motion.section
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.32 }}
          className="center-stage"
        >
          <NpcStage
            activeEvent={activeEvent}
            speakingPersona={speakingPersona}
            currentTurn={currentTurn}
            playbackStatus={playbackStatus}
            voiceStatus={voiceStatus}
            voiceEnabled={voiceEnabled}
          />
          <TimelineGraph timeline={session?.timeline ?? null} />
          <ScenarioFeed turns={session?.turns ?? []} activeTurnNumber={activeTurnNumber} />
        </motion.section>

        <aside className="right-rail">
          <div className="rail-heading">
            <Gauge className="h-4 w-4 text-cyan-300" />
            Operational stakes
          </div>
          <SeverityMeter severity={currentSeverity} maxSeverity={maxSeverity} />
          <RevenueTicker revenue={revenue} delta={revenueDelta} />
          <CompetenceGauge
            score={activeScore}
            band={activeReport?.readiness_band}
            topGap={session?.coach_plan.top_gap ?? activeReport?.skill_gaps?.[0]?.skill_id}
            evidenceCount={activeReport?.evidence_trail.length ?? 0}
            failureModes={activeReport?.failure_modes ?? []}
          />
        </aside>
      </section>

      <section className="bottom-intelligence">
        <CompetenceReport report={activeReport ?? null} />
        <ManagerFragilityMap map={fragilityMap} />
      </section>
    </main>
  );
}

type SessionSummaryProps = {
  title?: string;
  roleId?: string;
  sessionId?: string;
  streamStatus: string;
  playbackStatus: string;
  bufferedCount: number;
  progress: number;
  readiness?: number;
};

function SessionSummary({
  title,
  roleId,
  sessionId,
  streamStatus,
  playbackStatus,
  bufferedCount,
  progress,
  readiness,
}: SessionSummaryProps) {
  return (
    <section className="war-panel session-summary-panel p-4">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="panel-kicker">Session summary</p>
          <h2 className="line-clamp-2 break-words text-base font-semibold leading-5 text-white">
            {title ?? "No active incident"}
          </h2>
        </div>
        <Activity className={`h-5 w-5 ${playbackStatus === "playing" ? "animate-pulse text-cyan-300" : "text-slate-500"}`} />
      </div>
      <dl className="space-y-3 text-xs">
        <SummaryRow label="Role" value={roleId ?? "ROLE-SRE"} />
        <SummaryRow label="Stream intake" value={streamStatus} />
        <SummaryRow label="Playback" value={playbackStatus} />
        <SummaryRow label="Buffered events" value={String(bufferedCount)} />
        <SummaryRow label="Team readiness" value={readiness ? readiness.toFixed(1) : "Pending"} />
      </dl>
      <div className="mt-4">
        <div className="mb-2 flex items-center justify-between text-[10px] uppercase text-slate-500">
          <span>Synchronized progress</span>
          <span>{progress}%</span>
        </div>
        <div className="h-1.5 overflow-hidden rounded-full bg-white/5">
          <motion.div
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.25 }}
            className="h-full rounded-full bg-cyan-300"
          />
        </div>
      </div>
      {sessionId && <p className="mt-4 truncate font-mono text-[10px] text-slate-600">{sessionId}</p>}
    </section>
  );
}

function SummaryRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="summary-row">
      <dt className="summary-label">{label}</dt>
      <dd className="summary-value" title={value}>{value}</dd>
    </div>
  );
}

function playbackStatusTone(status: string): "ok" | "warn" | "loading" | "neutral" {
  if (status === "error") {
    return "warn";
  }
  if (status === "playing" || status === "buffering") {
    return "loading";
  }
  if (status === "completed") {
    return "ok";
  }
  return "neutral";
}
