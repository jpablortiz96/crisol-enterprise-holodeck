"use client";

import { create } from "zustand";
import {
  apiAssetUrl,
  getFragilityMap,
  getHealth,
  getLatestReport,
  getReadinessSummary,
  getVoiceStatus,
  runScenario,
  scenarioStreamUrl,
} from "@/lib/api";
import type {
  Citation,
  CoachPlan,
  CompetenceReport,
  ConsequenceDelta,
  HealthResponse,
  ManagerFragilityMap,
  NPCReaction,
  ReadinessSummary,
  SimulationRun,
  StreamEventEnvelope,
  StreamEventName,
  StreamStatus,
  TimelineResponse,
  TurnRecord,
  VoiceStatusResponse,
  VoiceSynthesisResult,
} from "@/lib/types";

type WarRoomState = {
  health: HealthResponse | null;
  session: SimulationRun | null;
  latestReport: CompetenceReport | null;
  fragilityMap: ManagerFragilityMap | null;
  readinessSummary: ReadinessSummary | null;
  voiceStatus: VoiceStatusResponse;
  voiceEnabled: boolean;
  liveEvents: StreamEventEnvelope[];
  streamStatus: StreamStatus;
  isLoading: boolean;
  error: string | null;
  initialize: () => Promise<void>;
  runSreSimulation: () => Promise<void>;
  playLiveSimulation: () => void;
  toggleVoice: () => void;
};

const STREAM_EVENT_NAMES: StreamEventName[] = [
  "session_started",
  "scenario_intro",
  "turn_started",
  "decision_selected",
  "npc_reaction",
  "consequence_delta",
  "timeline_updated",
  "score_final",
  "coach_plan",
  "manager_snapshot",
  "session_completed",
];

let liveSource: EventSource | null = null;
let audioQueue: string[] = [];
let activeAudio: HTMLAudioElement | null = null;

const TEXT_ONLY_VOICE_STATUS: VoiceStatusResponse = {
  configured: false,
  provider: "text-only",
  region_configured: false,
  voices: {},
};

export const useWarRoomStore = create<WarRoomState>((set, get) => ({
  health: null,
  session: null,
  latestReport: null,
  fragilityMap: null,
  readinessSummary: null,
  voiceStatus: TEXT_ONLY_VOICE_STATUS,
  voiceEnabled: true,
  liveEvents: [],
  streamStatus: "idle",
  isLoading: false,
  error: null,
  initialize: async () => {
    set({ isLoading: true, error: null });
    try {
      const [health, latestReport, readinessSummary, fragilityMap, voiceStatus] = await Promise.allSettled([
        getHealth(),
        getLatestReport(),
        getReadinessSummary(),
        getFragilityMap(),
        getVoiceStatus(),
      ]);

      set({
        health: health.status === "fulfilled" ? health.value : null,
        latestReport: latestReport.status === "fulfilled" ? latestReport.value : null,
        readinessSummary: readinessSummary.status === "fulfilled" ? readinessSummary.value : null,
        fragilityMap: fragilityMap.status === "fulfilled" ? fragilityMap.value : null,
        voiceStatus: voiceStatus.status === "fulfilled" ? voiceStatus.value : TEXT_ONLY_VOICE_STATUS,
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false, error: error instanceof Error ? error.message : "Initialization failed" });
    }
  },
  runSreSimulation: async () => {
    liveSource?.close();
    liveSource = null;
    stopAudioPlayback();
    set({ isLoading: true, error: null, liveEvents: [], streamStatus: "idle" });
    try {
      const session = await runScenario("ROLE-SRE");
      const [fragilityMap, readinessSummary, latestReport] = await Promise.allSettled([
        getFragilityMap(),
        getReadinessSummary(),
        getLatestReport(),
      ]);

      set({
        session,
        latestReport: latestReport.status === "fulfilled" ? latestReport.value : session.final_score,
        fragilityMap: fragilityMap.status === "fulfilled" ? fragilityMap.value : null,
        readinessSummary: readinessSummary.status === "fulfilled" ? readinessSummary.value : null,
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false, error: error instanceof Error ? error.message : "Simulation failed" });
    }
  },
  playLiveSimulation: () => {
    if (typeof EventSource === "undefined") {
      set({ streamStatus: "error", error: "Live streaming is not supported by this browser." });
      return;
    }

    liveSource?.close();
    stopAudioPlayback();
    const source = new EventSource(scenarioStreamUrl("ROLE-SRE"));
    liveSource = source;

    set({
      session: null,
      liveEvents: [],
      streamStatus: "connecting",
      isLoading: false,
      error: null,
    });

    source.onopen = () => {
      set({ streamStatus: "live", error: null });
    };

    const handleEvent = (message: MessageEvent<string>) => {
      try {
        const payload = JSON.parse(message.data) as StreamEventEnvelope;
        set((state) => reduceStreamEvent(state, payload));
        const voice = voiceFromPayload(payload);
        if (payload.event === "npc_reaction" && voice?.audio_url && get().voiceEnabled) {
          enqueueAudio(voice.audio_url);
        }

        if (payload.event === "session_completed") {
          source.close();
          if (liveSource === source) {
            liveSource = null;
          }
          void getReadinessSummary()
            .then((readinessSummary) => set({ readinessSummary }))
            .catch(() => undefined);
        }
      } catch (error) {
        source.close();
        if (liveSource === source) {
          liveSource = null;
        }
        set({
          streamStatus: "error",
          error: error instanceof Error ? error.message : "Live stream parsing failed",
        });
      }
    };

    STREAM_EVENT_NAMES.forEach((name) => {
      source.addEventListener(name, handleEvent as EventListener);
    });

    source.onerror = () => {
      if (get().streamStatus === "completed") {
        return;
      }
      source.close();
      if (liveSource === source) {
        liveSource = null;
      }
      set({ streamStatus: "error", error: "Live stream connection failed." });
    };
  },
  toggleVoice: () => {
    const nextEnabled = !get().voiceEnabled;
    if (!nextEnabled) {
      stopAudioPlayback();
    }
    set({ voiceEnabled: nextEnabled });
  },
}));

function reduceStreamEvent(state: WarRoomState, payload: StreamEventEnvelope): Partial<WarRoomState> {
  const duplicate = state.liveEvents.some(
    (event) => event.session_id === payload.session_id && event.sequence === payload.sequence,
  );
  if (duplicate) {
    return {};
  }

  const update: Partial<WarRoomState> = {
    liveEvents: [...state.liveEvents, payload].slice(-80),
    streamStatus: payload.event === "session_completed" ? "completed" : "live",
    isLoading: false,
    error: null,
  };

  let session = state.session ?? createEmptySession(payload.session_id, "ROLE-SRE");

  if (payload.event === "session_started") {
    session = createEmptySession(payload.session_id, String(payload.data.role_id ?? "ROLE-SRE"));
    update.session = session;
    return update;
  }

  if (payload.event === "scenario_intro") {
    session = {
      ...session,
      scenario: payload.data.scenario as SimulationRun["scenario"],
    };
    update.session = session;
    return update;
  }

  if (payload.event === "turn_started") {
    session = upsertTurn(session, Number(payload.data.turn_number), {
      situation: String(payload.data.situation ?? ""),
      citations: (payload.data.citations ?? []) as Citation[],
    });
    update.session = session;
    return update;
  }

  if (payload.event === "decision_selected") {
    session = upsertTurn(session, Number(payload.data.turn_number), {
      decision: payload.data.decision as TurnRecord["decision"],
    });
    update.session = session;
    return update;
  }

  if (payload.event === "npc_reaction") {
    const reaction = payload.data.reaction as NPCReaction;
    const voice = voiceFromPayload(payload);
    session = appendNpcReaction(
      session,
      Number(payload.data.turn_number),
      voice ? { ...reaction, voice } : reaction,
    );
    update.session = session;
    return update;
  }

  if (payload.event === "consequence_delta") {
    session = upsertTurn(session, Number(payload.data.turn_number), {
      consequence: payload.data.consequence as ConsequenceDelta,
    });
    update.session = session;
    return update;
  }

  if (payload.event === "timeline_updated") {
    session = {
      ...session,
      timeline: payload.data.timeline as TimelineResponse,
    };
    update.session = session;
    return update;
  }

  if (payload.event === "score_final") {
    const finalScore = payload.data.final_score as CompetenceReport & { score?: number };
    session = {
      ...session,
      final_score: finalScore,
    };
    update.session = session;
    update.latestReport = finalScore;
    return update;
  }

  if (payload.event === "coach_plan") {
    session = {
      ...session,
      coach_plan: payload.data.coach_plan as CoachPlan,
    };
    update.session = session;
    return update;
  }

  if (payload.event === "manager_snapshot") {
    update.fragilityMap = payload.data.manager_snapshot as ManagerFragilityMap;
    update.session = session;
    return update;
  }

  if (payload.event === "session_completed") {
    const completedSession = payload.data.session as SimulationRun;
    update.session = mergeReactionVoices(completedSession, session);
    update.latestReport = completedSession.final_score;
    update.streamStatus = "completed";
    return update;
  }

  update.session = session;
  return update;
}

function upsertTurn(session: SimulationRun, turnNumber: number, patch: Partial<TurnRecord>): SimulationRun {
  const turns = [...session.turns];
  const index = turns.findIndex((turn) => turn.turn_number === turnNumber);
  const current = index >= 0 ? turns[index] : createEmptyTurn(turnNumber);
  const nextTurn = { ...current, ...patch };

  if (index >= 0) {
    turns[index] = nextTurn;
  } else {
    turns.push(nextTurn);
  }

  turns.sort((first, second) => first.turn_number - second.turn_number);
  return { ...session, turns };
}

function appendNpcReaction(session: SimulationRun, turnNumber: number, reaction: NPCReaction): SimulationRun {
  const currentTurn = session.turns.find((turn) => turn.turn_number === turnNumber) ?? createEmptyTurn(turnNumber);
  const nextReactions = [...currentTurn.npc_reactions, reaction];
  return upsertTurn(session, turnNumber, { npc_reactions: nextReactions });
}

function voiceFromPayload(payload: StreamEventEnvelope): VoiceSynthesisResult | undefined {
  return (payload.data.voice ?? payload.data.speech) as VoiceSynthesisResult | undefined;
}

function mergeReactionVoices(completedSession: SimulationRun, streamedSession: SimulationRun): SimulationRun {
  return {
    ...completedSession,
    turns: completedSession.turns.map((turn) => {
      const streamedTurn = streamedSession.turns.find((candidate) => candidate.turn_number === turn.turn_number);
      if (!streamedTurn) {
        return turn;
      }
      return {
        ...turn,
        npc_reactions: turn.npc_reactions.map((reaction) => {
          const streamedReaction = streamedTurn.npc_reactions.find(
            (candidate) => candidate.persona === reaction.persona && candidate.message === reaction.message,
          );
          return streamedReaction?.voice ? { ...reaction, voice: streamedReaction.voice } : reaction;
        }),
      };
    }),
  };
}

function enqueueAudio(audioUrl: string): void {
  if (typeof Audio === "undefined") {
    return;
  }
  audioQueue.push(apiAssetUrl(audioUrl));
  void playNextAudio();
}

async function playNextAudio(): Promise<void> {
  if (activeAudio || !audioQueue.length || typeof Audio === "undefined") {
    return;
  }

  const audio = new Audio(audioQueue.shift());
  activeAudio = audio;

  const complete = () => {
    if (activeAudio !== audio) {
      return;
    }
    activeAudio = null;
    void playNextAudio();
  };

  audio.addEventListener("ended", complete, { once: true });
  audio.addEventListener("error", complete, { once: true });

  try {
    await audio.play();
  } catch {
    complete();
  }
}

function stopAudioPlayback(): void {
  audioQueue = [];
  if (activeAudio) {
    activeAudio.pause();
    activeAudio.src = "";
    activeAudio = null;
  }
}

function createEmptySession(sessionId: string, roleId: string): SimulationRun {
  return {
    session_id: sessionId,
    scenario: {
      id: "live-pending",
      title: "Live simulation",
      role_id: roleId,
      initial_stakes: "Connecting to live scenario playback.",
    },
    turns: [],
    timeline: createEmptyTimeline(sessionId),
    final_score: createEmptyReport(sessionId),
    coach_plan: {
      top_gap: "Pending",
      micro_plan: [],
      practice_scenario: "Pending",
      citations: [],
    },
  };
}

function createEmptyTimeline(sessionId: string): TimelineResponse {
  return {
    session_id: sessionId,
    root_node_id: "NODE-ROOT",
    nodes: [],
    edges: [],
    summary: {
      total_nodes: 0,
      max_severity: 0,
      max_revenue_at_risk: 0,
      final_severity: 0,
      final_revenue_at_risk: 0,
    },
  };
}

function createEmptyTurn(turnNumber: number): TurnRecord {
  return {
    turn_number: turnNumber,
    situation: "Awaiting streamed situation.",
    decision: {
      id: "pending",
      label: "Pending decision",
      description: "Awaiting streamed decision.",
    },
    npc_reactions: [],
    consequence: createEmptyConsequence(),
    citations: [],
  };
}

function createEmptyConsequence(): ConsequenceDelta {
  return {
    branch_id: "BR-PENDING",
    severity_delta: 0,
    new_severity: 0,
    affected_systems: [],
    newly_affected_systems: [],
    recovered_systems: [],
    cascade_paths: [],
    contract_exposure: [],
    revenue_at_risk: 0,
    revenue_delta: 0,
    world_delta: "Awaiting consequence update.",
    citations: [],
  };
}

function createEmptyReport(sessionId: string): CompetenceReport & { score?: number } {
  return {
    report_id: `RPT-${sessionId}`,
    session_id: sessionId,
    overall_score: 0,
    score: 0,
    readiness_band: "pending",
    executive_summary: "Live simulation in progress.",
    dimensions: {},
    evidence_trail: [],
    failure_modes: [],
    skill_gaps: [],
    certification_alignment: [],
    next_best_actions: [],
    citations: [],
  };
}
