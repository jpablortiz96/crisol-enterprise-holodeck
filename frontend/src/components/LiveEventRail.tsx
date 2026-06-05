"use client";

import { AnimatePresence, motion } from "framer-motion";
import {
  AlertTriangle,
  Bot,
  BookOpenCheck,
  CircleDollarSign,
  GitBranch,
  Radio,
  VolumeX,
} from "lucide-react";
import type { ReactNode } from "react";
import type {
  PlaybackStatus,
  StreamEventEnvelope,
  VoiceSynthesisResult,
} from "@/lib/types";

type LiveEventRailProps = {
  events: StreamEventEnvelope[];
  playbackStatus: PlaybackStatus;
  activeSequence?: number;
  bufferedCount: number;
};

export function LiveEventRail({
  events,
  playbackStatus,
  activeSequence,
  bufferedCount,
}: LiveEventRailProps) {
  const groups = groupEvents(events);
  const fallbackActive = events.some((event) => voiceForEvent(event)?.enabled === false);

  return (
    <section className="war-panel live-event-panel p-4">
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <p className="panel-kicker">Live agent orchestration</p>
          <h2 className="panel-title">Synchronized Event Rail</h2>
        </div>
        <div className="text-right">
          <div className="flex items-center justify-end gap-1.5 text-[11px] capitalize text-cyan-200">
            <Radio className={playbackStatus === "playing" ? "h-3.5 w-3.5 animate-pulse" : "h-3.5 w-3.5"} />
            {playbackStatus}
          </div>
          <p className="mt-1 text-[10px] uppercase text-slate-600">{bufferedCount} buffered</p>
        </div>
      </div>

      {fallbackActive && (
        <div className="mb-3 flex items-center gap-2 border-l-2 border-amber-300 bg-amber-300/5 px-3 py-2 text-[11px] text-amber-100">
          <VolumeX className="h-3.5 w-3.5" />
          Text fallback active for one or more NPC lines
        </div>
      )}

      <div className="event-rail-scroll">
        <AnimatePresence initial={false}>
          {groups.map((group) => (
            <motion.div
              key={group.key}
              layout
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="event-group"
            >
              <div className="event-group-label">
                <span>{group.label}</span>
                <span>{group.events.length} signals</span>
              </div>
              <div className="space-y-1">
                {group.events.map((event) => (
                  <EventItem
                    key={`${event.session_id}-${event.sequence}`}
                    event={event}
                    active={event.sequence === activeSequence}
                  />
                ))}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {!events.length && (
          <div className="empty-state">
            Live events will advance here in sync with the simulation stage.
          </div>
        )}
      </div>
    </section>
  );
}

function EventItem({ event, active }: { event: StreamEventEnvelope; active: boolean }) {
  const metadata = eventMetadata(event);
  const isFirstBadDecision =
    Number(event.data.turn_number) === 1 &&
    (event.event === "decision_selected" || event.event === "consequence_delta");

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.2 }}
      className={`event-item ${active ? "event-active" : ""} ${isFirstBadDecision ? "event-danger" : ""}`}
    >
      <div className="event-icon">{metadata.icon}</div>
      <div className="min-w-0 flex-1">
        <div className="flex items-center justify-between gap-2">
          <p className="truncate text-xs font-medium text-slate-100">{metadata.label}</p>
          <span className="font-mono text-[9px] text-slate-600">#{event.sequence}</span>
        </div>
        <p className="mt-1 line-clamp-2 text-[11px] leading-4 text-slate-500">{eventSummary(event)}</p>
        {metadata.badges.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {metadata.badges.map((badge) => (
              <span key={badge} className="event-badge">
                {badge}
              </span>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}

function eventMetadata(event: StreamEventEnvelope): {
  label: string;
  icon: ReactNode;
  badges: string[];
} {
  if (event.event === "npc_reaction") {
    return {
      label: `${npcPersona(event)} pressure`,
      icon: <Bot className="h-3.5 w-3.5" />,
      badges: ["NPC pressure", voiceProviderLabel(voiceForEvent(event))],
    };
  }
  if (event.event === "consequence_delta") {
    return {
      label: Number(event.data.turn_number) === 1 ? "Cascade detected" : "Consequence recalculated",
      icon: <AlertTriangle className="h-3.5 w-3.5" />,
      badges: ["Cascade detected", "Revenue delta"],
    };
  }
  if (event.event === "timeline_updated") {
    return {
      label: "Branching timeline updated",
      icon: <GitBranch className="h-3.5 w-3.5" />,
      badges: [],
    };
  }
  if (event.event === "turn_started") {
    const citations = (event.data.citations as unknown[] | undefined)?.length ?? 0;
    return {
      label: `Turn ${String(event.data.turn_number)} opened`,
      icon: <BookOpenCheck className="h-3.5 w-3.5" />,
      badges: citations ? [`Cited evidence ${citations}`] : [],
    };
  }
  if (event.event === "decision_selected") {
    return {
      label: Number(event.data.turn_number) === 1 ? "High-risk decision selected" : "Decision selected",
      icon: <CircleDollarSign className="h-3.5 w-3.5" />,
      badges: Number(event.data.turn_number) === 1 ? ["First bad decision"] : [],
    };
  }
  return {
    label: event.event.replaceAll("_", " "),
    icon: <Radio className="h-3.5 w-3.5" />,
    badges: [],
  };
}

function groupEvents(events: StreamEventEnvelope[]) {
  const groups = new Map<string, { key: string; label: string; events: StreamEventEnvelope[] }>();
  events.forEach((event) => {
    const turn = Number(event.data.turn_number);
    const key = Number.isFinite(turn) && turn > 0
      ? `turn-${turn}`
      : ["score_final", "coach_plan", "manager_snapshot", "session_completed"].includes(event.event)
        ? "outcome"
        : "briefing";
    const label = key.startsWith("turn-")
      ? `Turn ${turn}`
      : key === "outcome"
        ? "Assessment"
        : "Briefing";
    const group = groups.get(key) ?? { key, label, events: [] };
    group.events.push(event);
    groups.set(key, group);
  });
  return [...groups.values()];
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
  if (event.event === "scenario_intro") {
    const scenario = event.data.scenario as { title?: string } | undefined;
    return scenario?.title ?? "Scenario briefing received.";
  }
  if (event.event === "turn_started") {
    return String(event.data.situation ?? `Turn ${String(event.data.turn_number)} started.`);
  }
  if (event.event === "decision_selected") {
    const decision = event.data.decision as { label?: string } | undefined;
    return decision?.label ?? "Decision selected.";
  }
  if (event.event === "npc_reaction") {
    const reaction = event.data.reaction as { message?: string } | undefined;
    return reaction?.message ?? "NPC reaction received.";
  }
  if (event.event === "consequence_delta") {
    const consequence = event.data.consequence as { world_delta?: string } | undefined;
    return consequence?.world_delta ?? "Business consequence recalculated.";
  }
  if (event.event === "score_final") {
    const report = event.data.final_score as { overall_score?: number; score?: number } | undefined;
    const score = report?.overall_score ?? report?.score;
    return typeof score === "number" ? `Final competence score ${score.toFixed(1)}.` : "Final score received.";
  }
  if (event.event === "coach_plan") {
    return "Targeted coach plan generated.";
  }
  if (event.event === "manager_snapshot") {
    return "Manager fragility snapshot ready.";
  }
  if (event.event === "session_completed") {
    return "Synchronized session completed.";
  }
  return "Signal received.";
}
