"use client";

import { create } from "zustand";
import {
  apiAssetUrl,
  branchFromSession,
  getFragilityMap,
  getGroundingStatus,
  getHealth,
  getLatestReport,
  getMcpTools,
  getReadinessSummary,
  getScenarios,
  getTelemetrySummary,
  getVoiceStatus,
  getWorkspaceKnowledge,
  getWorkspaceProfiles,
  getWorkspaceRoles,
  getWorkspaceSkills,
  getWorkspaceStatus,
  getWorkspaceWalkthrough,
  getWorkspaceTemplates,
  initializeEmptyWorkspace,
  applyEdukyTemplate,
  applyWorkspaceTemplate,
  configureWorkspaceOrganization,
  enableWorkspaceExamples,
  disableWorkspaceExamples,
  saveWorkspaceKnowledge,
  saveWorkspaceProfile,
  saveWorkspaceRole,
  saveWorkspaceScenario,
  saveWorkspaceSkill,
  validateWorkspaceScenario,
  runMcpDemo as runMcpDemoRequest,
  runCustomScenario,
  streamCustomScenarioUrl,
} from "@/lib/api";
import { PlaybackDirector } from "@/lib/playback";
import type {
  Citation,
  CoachPlan,
  CompetenceReport,
  ConsequenceDelta,
  HealthResponse,
  GroundingStatus,
  DisplayMode,
  ManagerFragilityMap,
  McpDemoResponse,
  McpTool,
  NPCReaction,
  PlaybackSpeed,
  PlaybackStatus,
  ReadinessSummary,
  ReplayBranchResult,
  ScenarioSummary,
  SimulationRun,
  StreamEventEnvelope,
  StreamEventName,
  StreamStatus,
  TimelineResponse,
  TelemetrySummary,
  TurnRecord,
  VoiceStatusResponse,
  VoiceSynthesisResult,
  WorkspaceStatus,
  WorkspaceWalkthrough,
  KnowledgeDocument,
  WorkspaceProfile,
  WorkspaceRole,
  WorkspaceSkill,
  WorkspaceTemplates,
  AppSection,
  ScenarioValidationResult,
} from "@/lib/types";

type WarRoomState = {
  activeSection: AppSection;
  health: HealthResponse | null;
  groundingStatus: GroundingStatus | null;
  session: SimulationRun | null;
  latestSession: SimulationRun | null;
  latestReport: CompetenceReport | null;
  fragilityMap: ManagerFragilityMap | null;
  readinessSummary: ReadinessSummary | null;
  scenarios: ScenarioSummary[];
  selectedScenarioId: string | null;
  selectedProfileId: string | null;
  telemetrySummary: TelemetrySummary | null;
  workspaceStatus: WorkspaceStatus | null;
  workspaceWalkthrough: WorkspaceWalkthrough | null;
  workspaceKnowledge: KnowledgeDocument[];
  workspaceRoles: WorkspaceRole[];
  workspaceSkills: WorkspaceSkill[];
  workspaceProfiles: WorkspaceProfile[];
  workspaceTemplates: WorkspaceTemplates | null;
  workspaceEditing: boolean;
  mcpTools: McpTool[];
  mcpDemo: McpDemoResponse | null;
  replayBranch: ReplayBranchResult | null;
  selectedDecisionNodeId: string | null;
  voiceStatus: VoiceStatusResponse;
  voiceEnabled: boolean;
  displayMode: DisplayMode;
  receivedEvents: StreamEventEnvelope[];
  liveEvents: StreamEventEnvelope[];
  activeEvent: StreamEventEnvelope | null;
  speakingPersona: string | null;
  streamStatus: StreamStatus;
  playbackStatus: PlaybackStatus;
  playbackSpeed: PlaybackSpeed;
  isLoading: boolean;
  isMcpLoading: boolean;
  isBranching: boolean;
  isWorkspaceSaving: boolean;
  error: string | null;
  initialize: () => Promise<void>;
  runSreSimulation: () => Promise<void>;
  playLiveSimulation: () => void;
  pausePlayback: () => void;
  resumePlayback: () => void;
  replaySession: () => void;
  setPlaybackSpeed: (speed: PlaybackSpeed) => void;
  toggleVoice: () => void;
  toggleRecordingMode: () => void;
  refreshWorkspace: () => Promise<void>;
  startEmptyWorkspace: () => Promise<void>;
  applyEdukyWorkspace: () => Promise<void>;
  applyTemplate: (templateId: string) => Promise<void>;
  configureOrganization: (configuration: {
    organization_name: string;
    industry: string;
    workspace_name: string;
  }) => Promise<void>;
  setExamplesEnabled: (enabled: boolean) => Promise<void>;
  saveKnowledge: (fileName: string, content: string) => Promise<void>;
  saveRole: (role: Omit<WorkspaceRole, "data_classification">) => Promise<void>;
  saveSkill: (skill: Omit<WorkspaceSkill, "data_classification">) => Promise<void>;
  saveProfile: (profile: Omit<WorkspaceProfile, "data_classification">) => Promise<void>;
  saveScenario: (scenario: Record<string, unknown>) => Promise<void>;
  validateScenario: (scenario: Record<string, unknown>) => Promise<ScenarioValidationResult>;
  selectScenario: (scenarioId: string) => void;
  selectProfile: (profileId: string) => void;
  setActiveSection: (section: AppSection) => void;
  goToEvaluation: () => void;
  goToResults: () => void;
  goToSetup: () => void;
  goToScenarioStudio: () => void;
  setSelectedDecisionNode: (nodeId: string) => void;
  branchFromDecision: (alternativeAction: string) => Promise<void>;
  runMcpDemo: () => Promise<void>;
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

const TEXT_ONLY_VOICE_STATUS: VoiceStatusResponse = {
  configured: false,
  provider: "text-only",
  region_configured: false,
  voices: {},
};

let liveSource: EventSource | null = null;
let activeAudio: HTMLAudioElement | null = null;
let activeAudioResolve: (() => void) | null = null;
let activeAudioTimeout: number | null = null;

export const useWarRoomStore = create<WarRoomState>((set, get) => {
  const director = new PlaybackDirector({
    onEvent: (event) => {
      set((state) => reducePlaybackEvent(state, event));
    },
    onStatus: (playbackStatus) => {
      set({ playbackStatus });
    },
    onSpeaker: (speakingPersona) => {
      set({ speakingPersona });
    },
    playVoice: (voice, speed) => playVoice(voice, speed),
    shouldPlayVoice: () => get().voiceEnabled,
  });

  return {
    activeSection: "command-center",
    health: null,
    groundingStatus: null,
    session: null,
    latestSession: null,
    latestReport: null,
    fragilityMap: null,
    readinessSummary: null,
    scenarios: [],
    selectedScenarioId: null,
    selectedProfileId: null,
    telemetrySummary: null,
    workspaceStatus: null,
    workspaceWalkthrough: null,
    workspaceKnowledge: [],
    workspaceRoles: [],
    workspaceSkills: [],
    workspaceProfiles: [],
    workspaceTemplates: null,
    workspaceEditing: false,
    mcpTools: [],
    mcpDemo: null,
    replayBranch: null,
    selectedDecisionNodeId: null,
    voiceStatus: TEXT_ONLY_VOICE_STATUS,
    voiceEnabled: true,
    displayMode: "standard",
    receivedEvents: [],
    liveEvents: [],
    activeEvent: null,
    speakingPersona: null,
    streamStatus: "idle",
    playbackStatus: "idle",
    playbackSpeed: 1,
    isLoading: false,
    isMcpLoading: false,
    isBranching: false,
    isWorkspaceSaving: false,
    error: null,
    initialize: async () => {
      set({ isLoading: true, error: null });
      try {
        const [
          health,
          groundingStatus,
          latestReport,
          readinessSummary,
          fragilityMap,
          voiceStatus,
          mcpTools,
          scenarios,
          telemetrySummary,
          workspaceStatus,
          workspaceWalkthrough,
          workspaceKnowledge,
          workspaceRoles,
          workspaceSkills,
          workspaceProfiles,
          workspaceTemplates,
        ] = await Promise.allSettled([
          getHealth(),
          getGroundingStatus(),
          getLatestReport(),
          getReadinessSummary(),
          getFragilityMap(),
          getVoiceStatus(),
          getMcpTools(),
          getScenarios(),
          getTelemetrySummary(),
          getWorkspaceStatus(),
          getWorkspaceWalkthrough(),
          getWorkspaceKnowledge(),
          getWorkspaceRoles(),
          getWorkspaceSkills(),
          getWorkspaceProfiles(),
          getWorkspaceTemplates(),
        ]);
        const availableScenarios = scenarios.status === "fulfilled" ? scenarios.value : [];

        set({
          health: health.status === "fulfilled" ? health.value : null,
          groundingStatus:
            groundingStatus.status === "fulfilled"
              ? groundingStatus.value
              : null,
          latestReport: latestReport.status === "fulfilled" ? latestReport.value : null,
          readinessSummary: readinessSummary.status === "fulfilled" ? readinessSummary.value : null,
          fragilityMap: fragilityMap.status === "fulfilled" ? fragilityMap.value : null,
          voiceStatus: voiceStatus.status === "fulfilled" ? voiceStatus.value : TEXT_ONLY_VOICE_STATUS,
          mcpTools: mcpTools.status === "fulfilled" ? mcpTools.value.tools : [],
          scenarios: availableScenarios,
          selectedScenarioId:
            get().selectedScenarioId
            ?? availableScenarios.find((scenario) => scenario.scenario_id === "SCN-SRE-001")?.scenario_id
            ?? availableScenarios[0]?.scenario_id
            ?? null,
          selectedProfileId:
            get().selectedProfileId
            ?? (workspaceProfiles.status === "fulfilled"
              ? workspaceProfiles.value[0]?.profile_id ?? null
              : null),
          telemetrySummary: telemetrySummary.status === "fulfilled" ? telemetrySummary.value : null,
          workspaceStatus: workspaceStatus.status === "fulfilled" ? workspaceStatus.value : null,
          workspaceWalkthrough:
            workspaceWalkthrough.status === "fulfilled" ? workspaceWalkthrough.value : null,
          workspaceKnowledge: workspaceKnowledge.status === "fulfilled" ? workspaceKnowledge.value : [],
          workspaceRoles: workspaceRoles.status === "fulfilled" ? workspaceRoles.value : [],
          workspaceSkills: workspaceSkills.status === "fulfilled" ? workspaceSkills.value : [],
          workspaceProfiles: workspaceProfiles.status === "fulfilled" ? workspaceProfiles.value : [],
          workspaceTemplates: workspaceTemplates.status === "fulfilled" ? workspaceTemplates.value : null,
          isLoading: false,
        });
      } catch (error) {
        set({ isLoading: false, error: error instanceof Error ? error.message : "Initialization failed" });
      }
    },
    runSreSimulation: async () => {
      closeLiveSource();
      director.reset();
      stopAudioPlayback();
      set({
        isLoading: true,
        error: null,
        receivedEvents: [],
        liveEvents: [],
        activeEvent: null,
        speakingPersona: null,
        streamStatus: "idle",
      });
      try {
        const selectedScenario = get().scenarios.find(
          (scenario) => scenario.scenario_id === get().selectedScenarioId,
        );
        if (!selectedScenario) {
          throw new Error("Create or select a scenario before starting a run.");
        }
        const session = await runCustomScenario(
          selectedScenario.scenario_id,
          selectedScenario.role_id,
        );
        const [
          fragilityMap,
          readinessSummary,
          latestReport,
          telemetrySummary,
          workspaceWalkthrough,
        ] = await Promise.allSettled([
          getFragilityMap(),
          getReadinessSummary(),
          getLatestReport(),
          getTelemetrySummary(),
          getWorkspaceWalkthrough(),
        ]);

        set({
          session,
          latestSession: session,
          latestReport: latestReport.status === "fulfilled" ? latestReport.value : session.final_score,
          fragilityMap: fragilityMap.status === "fulfilled" ? fragilityMap.value : null,
          readinessSummary: readinessSummary.status === "fulfilled" ? readinessSummary.value : null,
          telemetrySummary: telemetrySummary.status === "fulfilled" ? telemetrySummary.value : get().telemetrySummary,
          workspaceWalkthrough:
            workspaceWalkthrough.status === "fulfilled"
              ? workspaceWalkthrough.value
              : get().workspaceWalkthrough,
          selectedDecisionNodeId: firstDecisionNodeId(session.timeline),
          replayBranch: null,
          isLoading: false,
        });
      } catch (error) {
        set({ isLoading: false, error: error instanceof Error ? error.message : "Simulation failed" });
      }
    },
    playLiveSimulation: () => {
      if (typeof EventSource === "undefined") {
        set({
          streamStatus: "error",
          playbackStatus: "error",
          error: "Live streaming is not supported by this browser.",
        });
        return;
      }

      closeLiveSource();
      director.reset();
      director.setSpeed(get().playbackSpeed);
      stopAudioPlayback();

      const selectedScenario = get().scenarios.find(
        (scenario) => scenario.scenario_id === get().selectedScenarioId,
      );
      if (!selectedScenario) {
        set({
          streamStatus: "idle",
          playbackStatus: "idle",
          error: "Create or select a scenario before starting live simulation.",
        });
        return;
      }
      const source = new EventSource(
        streamCustomScenarioUrl(selectedScenario.scenario_id, selectedScenario.role_id),
      );
      liveSource = source;
      set({
        session: null,
        fragilityMap: null,
        replayBranch: null,
        selectedDecisionNodeId: null,
        receivedEvents: [],
        liveEvents: [],
        activeEvent: null,
        speakingPersona: null,
        streamStatus: "connecting",
        playbackStatus: "buffering",
        isLoading: false,
        error: null,
      });

      source.onopen = () => {
        set({ streamStatus: "live", error: null });
      };

      const handleEvent = (message: MessageEvent<string>) => {
        try {
          const payload = JSON.parse(message.data) as StreamEventEnvelope;
          set((state) => ({
            receivedEvents: appendUniqueEvent(state.receivedEvents, payload),
            streamStatus: payload.event === "session_completed" ? "completed" : "live",
          }));
          director.enqueue(payload);

          if (payload.event === "session_completed") {
            closeLiveSource();
            void getReadinessSummary()
              .then((readinessSummary) => set({ readinessSummary }))
              .catch(() => undefined);
            void getTelemetrySummary()
              .then((telemetrySummary) => set({ telemetrySummary }))
              .catch(() => undefined);
            void getWorkspaceWalkthrough()
              .then((workspaceWalkthrough) => set({ workspaceWalkthrough }))
              .catch(() => undefined);
          }
        } catch (error) {
          closeLiveSource();
          set({
            streamStatus: "error",
            playbackStatus: "error",
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
        closeLiveSource();
        set({
          streamStatus: "error",
          playbackStatus: "error",
          error: "Live stream connection failed.",
        });
      };
    },
    pausePlayback: () => {
      director.pause();
      activeAudio?.pause();
    },
    resumePlayback: () => {
      director.resume();
      if (activeAudio?.src) {
        void activeAudio.play().catch(() => finishActiveAudio());
      }
    },
    replaySession: () => {
      if (!director.getArchive().length) {
        return;
      }
      stopAudioPlayback();
      set({
        session: null,
        fragilityMap: null,
        liveEvents: [],
        activeEvent: null,
        speakingPersona: null,
        playbackStatus: "buffering",
        error: null,
      });
      director.replay();
    },
    setPlaybackSpeed: (playbackSpeed) => {
      director.setSpeed(playbackSpeed);
      if (activeAudio) {
        activeAudio.playbackRate = playbackSpeed;
      }
      set({ playbackSpeed });
    },
    toggleVoice: () => {
      const nextEnabled = !get().voiceEnabled;
      if (!nextEnabled) {
        stopAudioPlayback();
      }
      set({ voiceEnabled: nextEnabled });
    },
    toggleRecordingMode: () => {
      set({
        displayMode: get().displayMode === "recording" ? "standard" : "recording",
      });
    },
    refreshWorkspace: async () => {
      const [
        workspaceStatus,
        workspaceWalkthrough,
        scenarios,
        knowledge,
        roles,
        skills,
        profiles,
        templates,
      ] = await Promise.all([
        getWorkspaceStatus(),
        getWorkspaceWalkthrough(),
        getScenarios(),
        getWorkspaceKnowledge(),
        getWorkspaceRoles(),
        getWorkspaceSkills(),
        getWorkspaceProfiles(),
        getWorkspaceTemplates(),
      ]);
      const selectedScenarioId = scenarios.some(
        (scenario) => scenario.scenario_id === get().selectedScenarioId,
      )
        ? get().selectedScenarioId
        : scenarios[0]?.scenario_id ?? null;
      set({
        workspaceStatus,
        workspaceWalkthrough,
        scenarios,
        selectedScenarioId,
        workspaceKnowledge: knowledge,
        workspaceRoles: roles,
        workspaceSkills: skills,
        workspaceProfiles: profiles,
        selectedProfileId: profiles.some(
          (profile) => profile.profile_id === get().selectedProfileId,
        )
          ? get().selectedProfileId
          : profiles[0]?.profile_id ?? null,
        workspaceTemplates: templates,
      });
    },
    startEmptyWorkspace: async () => {
      set({ isWorkspaceSaving: true, error: null });
      try {
        await initializeEmptyWorkspace();
        set({ workspaceEditing: true });
        await get().refreshWorkspace();
        set({ isWorkspaceSaving: false });
      } catch (error) {
        set({
          isWorkspaceSaving: false,
          error: error instanceof Error ? error.message : "Workspace initialization failed",
        });
        throw error;
      }
    },
    applyEdukyWorkspace: async () => {
      set({ isWorkspaceSaving: true, error: null });
      try {
        await applyEdukyTemplate();
        set({ workspaceEditing: true });
        await get().refreshWorkspace();
        set({ isWorkspaceSaving: false });
      } catch (error) {
        set({
          isWorkspaceSaving: false,
          error: error instanceof Error ? error.message : "Workspace template failed",
        });
        throw error;
      }
    },
    applyTemplate: async (templateId) => {
      await workspaceMutation(set, get, () => applyWorkspaceTemplate(templateId));
    },
    configureOrganization: async (configuration) => {
      await workspaceMutation(
        set,
        get,
        () => configureWorkspaceOrganization(configuration),
      );
    },
    setExamplesEnabled: async (enabled) => {
      set({ isWorkspaceSaving: true, error: null });
      try {
        if (enabled) {
          await enableWorkspaceExamples();
        } else {
          await disableWorkspaceExamples();
        }
        set({ workspaceEditing: true });
        await get().refreshWorkspace();
        set({ isWorkspaceSaving: false });
      } catch (error) {
        set({
          isWorkspaceSaving: false,
          error: error instanceof Error ? error.message : "Example mode update failed",
        });
        throw error;
      }
    },
    saveKnowledge: async (fileName, content) => {
      await workspaceMutation(set, get, () => saveWorkspaceKnowledge(fileName, content));
    },
    saveRole: async (role) => {
      await workspaceMutation(set, get, () => saveWorkspaceRole(role));
    },
    saveSkill: async (skill) => {
      await workspaceMutation(set, get, () => saveWorkspaceSkill(skill));
    },
    saveProfile: async (profile) => {
      await workspaceMutation(set, get, () => saveWorkspaceProfile(profile));
    },
    saveScenario: async (scenario) => {
      await workspaceMutation(set, get, () => saveWorkspaceScenario(scenario));
    },
    validateScenario: async (scenario) => validateWorkspaceScenario(scenario),
    selectScenario: (selectedScenarioId) => {
      if (get().streamStatus === "live") {
        return;
      }
      set({
        selectedScenarioId,
        session: null,
        replayBranch: null,
        selectedDecisionNodeId: null,
        error: null,
      });
    },
    selectProfile: (selectedProfileId) => {
      set({ selectedProfileId, error: null });
    },
    setActiveSection: (activeSection) => {
      set({ activeSection });
    },
    goToEvaluation: () => {
      set({ activeSection: "evaluation-room" });
    },
    goToResults: () => {
      set({ activeSection: "results-center" });
    },
    goToSetup: () => {
      set({ activeSection: "workspace-setup" });
    },
    goToScenarioStudio: () => {
      set({ activeSection: "scenario-studio" });
    },
    setSelectedDecisionNode: (selectedDecisionNodeId) => {
      set({ selectedDecisionNodeId, replayBranch: null });
    },
    branchFromDecision: async (alternativeAction) => {
      const { session, selectedDecisionNodeId } = get();
      if (!session || !selectedDecisionNodeId) {
        set({ error: "Select a completed decision before branching." });
        return;
      }
      set({ isBranching: true, replayBranch: null, error: null });
      try {
        const replayBranch = await branchFromSession(
          session.session_id,
          selectedDecisionNodeId,
          alternativeAction,
        );
        set({ replayBranch, isBranching: false });
      } catch (error) {
        set({
          isBranching: false,
          error: error instanceof Error ? error.message : "Replay branch failed",
        });
      }
    },
    runMcpDemo: async () => {
      set({ isMcpLoading: true, mcpDemo: null, error: null });
      try {
        const mcpDemo = await runMcpDemoRequest();
        set({ mcpDemo, isMcpLoading: false });
      } catch (error) {
        set({
          isMcpLoading: false,
          error: error instanceof Error ? error.message : "Tool preview failed",
        });
      }
    },
  };
});

async function workspaceMutation(
  set: (partial: Partial<WarRoomState>) => void,
  get: () => WarRoomState,
  mutation: () => Promise<unknown>,
): Promise<void> {
  set({ isWorkspaceSaving: true, error: null });
  try {
    await mutation();
    set({ workspaceEditing: true });
    await get().refreshWorkspace();
    set({ isWorkspaceSaving: false });
  } catch (error) {
    set({
      isWorkspaceSaving: false,
      error: error instanceof Error ? error.message : "Workspace update failed",
    });
    throw error;
  }
}

function reducePlaybackEvent(state: WarRoomState, payload: StreamEventEnvelope): Partial<WarRoomState> {
  const update: Partial<WarRoomState> = {
    liveEvents: appendUniqueEvent(state.liveEvents, payload).slice(-80),
    activeEvent: payload,
    error: null,
  };

  let session = state.session ?? createEmptySession(payload.session_id, "ROLE-SRE");

  if (payload.event === "session_started") {
    update.session = createEmptySession(payload.session_id, String(payload.data.role_id ?? "ROLE-SRE"));
    return update;
  }

  if (payload.event === "scenario_intro") {
    update.session = {
      ...session,
      scenario: payload.data.scenario as SimulationRun["scenario"],
    };
    return update;
  }

  if (payload.event === "turn_started") {
    update.session = upsertTurn(session, Number(payload.data.turn_number), {
      situation: String(payload.data.situation ?? ""),
      citations: (payload.data.citations ?? []) as Citation[],
    });
    return update;
  }

  if (payload.event === "decision_selected") {
    update.session = upsertTurn(session, Number(payload.data.turn_number), {
      decision: payload.data.decision as TurnRecord["decision"],
    });
    return update;
  }

  if (payload.event === "npc_reaction") {
    const reaction = payload.data.reaction as NPCReaction;
    const voice = voiceFromPayload(payload);
    update.session = appendNpcReaction(
      session,
      Number(payload.data.turn_number),
      voice ? { ...reaction, voice } : reaction,
    );
    return update;
  }

  if (payload.event === "consequence_delta") {
    update.session = upsertTurn(session, Number(payload.data.turn_number), {
      consequence: payload.data.consequence as ConsequenceDelta,
    });
    return update;
  }

  if (payload.event === "timeline_updated") {
    const timeline = payload.data.timeline as TimelineResponse;
    update.session = {
      ...session,
      timeline,
    };
    update.selectedDecisionNodeId =
      state.selectedDecisionNodeId ?? firstDecisionNodeId(timeline);
    return update;
  }

  if (payload.event === "score_final") {
    const finalScore = payload.data.final_score as CompetenceReport & { score?: number };
    update.session = { ...session, final_score: finalScore };
    update.latestReport = finalScore;
    return update;
  }

  if (payload.event === "coach_plan") {
    update.session = {
      ...session,
      coach_plan: payload.data.coach_plan as CoachPlan,
    };
    return update;
  }

  if (payload.event === "manager_snapshot") {
    update.fragilityMap = payload.data.manager_snapshot as ManagerFragilityMap;
    update.session = session;
    return update;
  }

  if (payload.event === "session_completed") {
    const completedSession = payload.data.session as SimulationRun;
    const mergedSession = mergeReactionVoices(completedSession, session);
    update.session = mergedSession;
    update.latestSession = mergedSession;
    update.latestReport = mergedSession.final_score;
    update.selectedDecisionNodeId =
      state.selectedDecisionNodeId ?? firstDecisionNodeId(mergedSession.timeline);
    return update;
  }

  update.session = session;
  return update;
}

function appendUniqueEvent(
  events: StreamEventEnvelope[],
  payload: StreamEventEnvelope,
): StreamEventEnvelope[] {
  if (events.some((event) => event.session_id === payload.session_id && event.sequence === payload.sequence)) {
    return events;
  }
  return [...events, payload];
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
  return upsertTurn(session, turnNumber, {
    npc_reactions: [...currentTurn.npc_reactions, reaction],
  });
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

function playVoice(voice: VoiceSynthesisResult, speed: PlaybackSpeed): Promise<void> {
  if (typeof Audio === "undefined" || !voice.audio_url) {
    return Promise.resolve();
  }

  stopAudioPlayback();
  const audio = new Audio(apiAssetUrl(voice.audio_url));
  audio.playbackRate = speed;
  activeAudio = audio;

  return new Promise<void>((resolve) => {
    activeAudioResolve = resolve;
    const complete = () => finishActiveAudio();
    audio.addEventListener("ended", complete, { once: true });
    audio.addEventListener("error", complete, { once: true });
    activeAudioTimeout = window.setTimeout(complete, 22000 / speed);
    void audio.play().catch(complete);
  });
}

function finishActiveAudio(): void {
  if (activeAudioTimeout !== null) {
    window.clearTimeout(activeAudioTimeout);
    activeAudioTimeout = null;
  }
  const resolve = activeAudioResolve;
  activeAudioResolve = null;
  activeAudio = null;
  resolve?.();
}

function stopAudioPlayback(): void {
  if (activeAudio) {
    activeAudio.pause();
    activeAudio.src = "";
  }
  finishActiveAudio();
}

function closeLiveSource(): void {
  liveSource?.close();
  liveSource = null;
}

function createEmptySession(sessionId: string, roleId: string): SimulationRun {
  return {
    session_id: sessionId,
    scenario: {
      id: "live-pending",
      title: "Live simulation",
      role_id: roleId,
      initial_stakes: "Connecting to synchronized scenario playback.",
      personas: [],
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
    situation: "Awaiting synchronized situation update.",
    decision: {
      id: "pending",
      label: "Decision pending",
      description: "Awaiting synchronized decision.",
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
    executive_summary: "Synchronized simulation in progress.",
    dimensions: {},
    evidence_trail: [],
    failure_modes: [],
    skill_gaps: [],
    certification_alignment: [],
    next_best_actions: [],
    citations: [],
  };
}

function firstDecisionNodeId(timeline: TimelineResponse): string | null {
  return timeline.nodes.find((node) => node.turn_number > 0)?.node_id ?? null;
}
