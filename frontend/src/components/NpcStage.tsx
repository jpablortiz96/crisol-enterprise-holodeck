"use client";

import { AudioWaveform, RadioTower, UsersRound } from "lucide-react";
import type {
  NPCReaction,
  PersonaMetadata,
  PlaybackStatus,
  StreamEventEnvelope,
  TurnRecord,
  VoiceStatusResponse,
} from "@/lib/types";
import { NpcCard } from "@/components/NpcCard";

type NpcStageProps = {
  personas: PersonaMetadata[];
  activeEvent?: StreamEventEnvelope | null;
  speakingPersona?: string | null;
  currentTurn?: TurnRecord;
  playbackStatus: PlaybackStatus;
  voiceStatus: VoiceStatusResponse;
  voiceEnabled: boolean;
};

export function NpcStage({
  personas,
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
          <p className="panel-kicker">Scenario-driven presence</p>
          <h2 className="panel-title">NPC Command Stage</h2>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <RadioTower className={`h-4 w-4 ${playbackStatus === "playing" ? "animate-pulse text-cyan-300" : ""}`} />
          {activePersona ? `${activePersona} active` : personas.length ? "Standby" : "No roster"}
        </div>
      </div>

      <div className="stage-grid">
        <div className="stage-focus">
          <div className="stage-horizon" />
          <div className="relative z-10">
            <div className="mb-4 flex items-center gap-2 text-xs uppercase text-slate-400">
              {activePersona ? <AudioWaveform className="h-4 w-4 text-cyan-300" /> : <UsersRound className="h-4 w-4" />}
              {activePersona ? "Live NPC pressure" : personas.length ? "Scenario personas ready" : "No personas loaded"}
            </div>
            <p className="stage-message max-w-3xl text-xl font-medium leading-8 text-white">
              {activeReaction?.message ??
                currentTurn?.situation ??
                (personas.length
                  ? "Start synchronized live playback to activate the configured scenario personas."
                  : "Select or create a scenario to populate the incident room.")}
            </p>
            <div className="mt-5 flex flex-wrap items-center gap-2">
              <span className="stage-chip">
                {activePersona ?? `${personas.length} persona${personas.length === 1 ? "" : "s"} configured`}
              </span>
              <span className="stage-chip">
                {voiceEnabled && voiceStatus.configured ? "Azure Speech active" : "Text fallback"}
              </span>
              {currentTurn && <span className="stage-chip">Turn {currentTurn.turn_number}</span>}
            </div>
          </div>
        </div>

        {personas.length > 0 && (
          <div className="npc-roster-grid">
            {personas.map((persona) => {
              const reaction = findLatestReaction(currentTurn, persona.persona);
              return (
                <NpcCard
                  key={persona.persona}
                  persona={persona.persona}
                  role={persona.role}
                  communicationStyle={persona.communication_style}
                  avatarStyle={persona.avatar_style}
                  pressure={reaction?.pressure_level ?? pressureBaseline(persona.pressure_profile)}
                  status={reaction ? reaction.tone : persona.pressure_profile}
                  active={activePersona === persona.persona}
                  compact
                />
              );
            })}
          </div>
        )}
      </div>
    </section>
  );
}

function findLatestReaction(turn: TurnRecord | undefined, persona: string): NPCReaction | undefined {
  return turn?.npc_reactions.find((reaction) => reaction.persona === persona);
}

function pressureBaseline(profile: string): number {
  return { low: 1, medium: 2, high: 3, critical: 4 }[profile] ?? 2;
}
