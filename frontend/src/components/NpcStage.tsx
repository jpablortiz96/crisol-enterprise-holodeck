"use client";

import { AnimatePresence, motion } from "framer-motion";
import { AudioWaveform, RadioTower, UsersRound } from "lucide-react";
import type {
  NPCReaction,
  PlaybackStatus,
  StreamEventEnvelope,
  TurnRecord,
  VoiceStatusResponse,
} from "@/lib/types";
import { NpcCard } from "@/components/NpcCard";

type NpcStageProps = {
  activeEvent?: StreamEventEnvelope | null;
  speakingPersona?: string | null;
  currentTurn?: TurnRecord;
  playbackStatus: PlaybackStatus;
  voiceStatus: VoiceStatusResponse;
  voiceEnabled: boolean;
};

const NPCS = [
  { persona: "VP Operations", role: "Executive command" },
  { persona: "Product Manager", role: "Customer impact" },
  { persona: "Database Lead", role: "Data recovery" },
  { persona: "Support Lead", role: "Response communications" },
];

export function NpcStage({
  activeEvent,
  speakingPersona,
  currentTurn,
  playbackStatus,
  voiceStatus,
  voiceEnabled,
}: NpcStageProps) {
  const activeReaction =
    activeEvent?.event === "npc_reaction"
      ? (activeEvent.data.reaction as NPCReaction | undefined)
      : currentTurn?.npc_reactions.at(-1);
  const activePersona =
    speakingPersona ??
    (activeEvent?.event === "npc_reaction" ? activeReaction?.persona ?? null : null);

  return (
    <section className="war-panel npc-stage-panel">
      <div className="panel-header">
        <div>
          <p className="panel-kicker">Incident room presence</p>
          <h2 className="panel-title">NPC Command Stage</h2>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <RadioTower className={`h-4 w-4 ${playbackStatus === "playing" ? "animate-pulse text-cyan-300" : ""}`} />
          {activePersona ? `${activePersona} active` : "Standby"}
        </div>
      </div>

      <div className="stage-grid">
        <div className="stage-focus">
          <div className="stage-horizon" />
          <AnimatePresence mode="wait">
            <motion.div
              key={activePersona ?? "standby"}
              initial={{ opacity: 0, y: 12, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.28 }}
              className="relative z-10"
            >
              <div className="mb-4 flex items-center gap-2 text-xs uppercase text-slate-400">
                {activePersona ? <AudioWaveform className="h-4 w-4 text-cyan-300" /> : <UsersRound className="h-4 w-4" />}
                {activePersona ? "Live NPC pressure" : "Incident room awaiting signal"}
              </div>
              <p className="stage-message max-w-3xl text-xl font-medium leading-8 text-white">
                {activeReaction?.message ??
                  currentTurn?.situation ??
                  "Start synchronized live playback to activate the incident room."}
              </p>
              <div className="mt-5 flex flex-wrap items-center gap-2">
                <span className="stage-chip">{activePersona ?? "Four personas online"}</span>
                <span className="stage-chip">
                  {voiceEnabled && voiceStatus.configured ? "Azure Speech active" : "Text fallback"}
                </span>
                {currentTurn && <span className="stage-chip">Turn {currentTurn.turn_number}</span>}
              </div>
            </motion.div>
          </AnimatePresence>
        </div>

        <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
          {NPCS.map((npc) => {
            const reaction = findLatestReaction(currentTurn, npc.persona);
            return (
              <NpcCard
                key={npc.persona}
                persona={npc.persona}
                role={npc.role}
                pressure={reaction?.pressure_level ?? 1}
                status={reaction ? reaction.tone : "ready"}
                active={activePersona === npc.persona}
                compact
              />
            );
          })}
        </div>
      </div>
    </section>
  );
}

function findLatestReaction(turn: TurnRecord | undefined, persona: string): NPCReaction | undefined {
  return turn?.npc_reactions.find((reaction) => reaction.persona === persona);
}
