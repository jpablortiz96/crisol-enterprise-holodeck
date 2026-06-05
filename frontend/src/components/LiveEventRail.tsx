"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Radio, VolumeX, Waves } from "lucide-react";
import type { StreamEventEnvelope, StreamStatus, VoiceSynthesisResult } from "@/lib/types";

type LiveEventRailProps = {
  events: StreamEventEnvelope[];
  status: StreamStatus;
};

const EVENT_LABELS: Record<string, string> = {
  session_started: "Session started",
  scenario_intro: "Scenario intro",
  turn_started: "Turn started",
  decision_selected: "Decision selected",
  npc_reaction: "NPC reaction",
  consequence_delta: "Consequence delta",
  timeline_updated: "Timeline updated",
  score_final: "Score final",
  coach_plan: "Coach plan",
  manager_snapshot: "Manager snapshot",
  session_completed: "Session completed",
};

export function LiveEventRail({ events, status }: LiveEventRailProps) {
  const textFallbackActive = events.some((event) => {
    const voice = voiceForEvent(event);
    return event.event === "npc_reaction" && voice?.enabled === false;
  });

  return (
    <section className="rounded-lg border border-line bg-panel/80 p-4 shadow-soft-border">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-400">Live agent orchestration</p>
          <h2 className="text-lg font-semibold text-white">Event Rail</h2>
        </div>
        <div className="flex items-center gap-2">
          {textFallbackActive && (
            <span className="inline-flex items-center gap-1 rounded-full border border-caution/40 bg-caution/10 px-2 py-1 text-[11px] font-medium text-amber-100">
              <VolumeX className="h-3.5 w-3.5" />
              Text fallback active
            </span>
          )}
          <span className="inline-flex items-center gap-1 rounded-full border border-slate-600 px-2 py-1 text-[11px] font-medium text-slate-200">
            <Radio className="h-3.5 w-3.5" />
            {status}
          </span>
        </div>
      </div>

      <div className="max-h-[340px] space-y-2 overflow-y-auto pr-1">
        <AnimatePresence initial={false}>
          {events.slice(-18).map((event) => (
            <motion.div
              key={`${event.session_id}-${event.sequence}`}
              layout
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 10 }}
              transition={{ duration: 0.18 }}
              className="rounded-md border border-line bg-ink/60 p-3"
            >
              <div className="flex items-center justify-between gap-3">
                <span className="inline-flex items-center gap-2 text-sm font-medium text-white">
                  <Waves className="h-3.5 w-3.5 text-signal" />
                  {EVENT_LABELS[event.event] ?? event.event}
                </span>
                <span className="text-[11px] text-slate-500">#{event.sequence}</span>
              </div>
              {event.event === "npc_reaction" && (
                <div className="mt-2 flex flex-wrap items-center gap-2">
                  <span className="rounded-full border border-caution/40 bg-caution/10 px-2 py-0.5 text-[11px] text-amber-100">
                    NPC pressure
                  </span>
                  <span className="text-[11px] text-slate-300">{npcPersona(event)}</span>
                  <span className="rounded-full border border-slate-600 px-2 py-0.5 text-[11px] text-slate-300">
                    {voiceProviderLabel(voiceForEvent(event))}
                  </span>
                </div>
              )}
              <p className="mt-1 line-clamp-2 text-xs leading-5 text-slate-400">{eventSummary(event)}</p>
            </motion.div>
          ))}
        </AnimatePresence>

        {!events.length && (
          <div className="rounded-lg border border-dashed border-slate-700 p-4 text-sm text-slate-400">
            Live events will appear here during playback.
          </div>
        )}
      </div>
    </section>
  );
}

function voiceForEvent(event: StreamEventEnvelope): VoiceSynthesisResult | undefined {
  return (event.data.voice ?? event.data.speech) as VoiceSynthesisResult | undefined;
}

function npcPersona(event: StreamEventEnvelope): string {
  const reaction = event.data.reaction as { persona?: string } | undefined;
  return reaction?.persona ?? "NPC";
}

function voiceProviderLabel(voice?: VoiceSynthesisResult): string {
  return voice?.provider === "azure-speech" ? "Azure Speech" : "Text fallback";
}

function eventSummary(event: StreamEventEnvelope): string {
  if (event.event === "turn_started") {
    return `Turn ${String(event.data.turn_number)} pressure entered the feed.`;
  }
  if (event.event === "decision_selected") {
    const decision = event.data.decision as { label?: string } | undefined;
    return decision?.label ?? "Decision selected.";
  }
  if (event.event === "npc_reaction") {
    const reaction = event.data.reaction as { persona?: string; message?: string } | undefined;
    return `${reaction?.persona ?? "NPC"}: ${reaction?.message ?? "Reaction received."}`;
  }
  if (event.event === "consequence_delta") {
    const consequence = event.data.consequence as { world_delta?: string } | undefined;
    return consequence?.world_delta ?? "Consequence received.";
  }
  if (event.event === "score_final") {
    const report = event.data.final_score as { overall_score?: number; score?: number } | undefined;
    const score = report?.overall_score ?? report?.score;
    return typeof score === "number" ? `Final score ${score.toFixed(1)}.` : "Final score received.";
  }
  if (event.event === "manager_snapshot") {
    return "Manager snapshot ready.";
  }
  if (event.event === "session_completed") {
    return "Session completed.";
  }
  return EVENT_LABELS[event.event] ?? event.event;
}
