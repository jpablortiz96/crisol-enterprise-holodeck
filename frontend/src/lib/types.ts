export type Citation = {
  doc_id: string;
  title: string;
  file_name: string;
  chunk_id: string;
  quote: string;
};

export type HealthResponse = {
  status: string;
  service: string;
  phase: string;
};

export type ScenarioSummary = {
  scenario_id: string;
  title: string;
  industry: string;
  role_id: string;
  difficulty: string;
  estimated_minutes: number;
  data_classification: "sanitized-training";
  tags: string[];
};

export type TelemetrySummary = {
  status: string;
  evaluation_status: string;
  evaluation_score: number | null;
  data_mode: string;
  production_changes: boolean;
  event_count: number;
  event_types: Record<string, number>;
  latest_event: {
    event_type: string;
    timestamp: string;
    payload: Record<string, unknown>;
  } | null;
  storage: string;
};

export type VoiceSynthesisResult = {
  enabled: boolean;
  provider: string;
  voice_name: string | null;
  audio_url: string | null;
  format: string | null;
  message: string;
};

export type VoiceStatusResponse = {
  configured: boolean;
  provider: "azure-speech" | "text-only";
  region_configured: boolean;
  voices: Record<string, string>;
};

export type NPCReaction = {
  persona: string;
  tone: string;
  message: string;
  pressure_level: number;
  voice?: VoiceSynthesisResult;
};

export type ContractExposure = {
  contract_id: string;
  criticality: string;
  systems: string[];
  revenue_per_hour: number;
  exposure: number;
};

export type ConsequenceDelta = {
  branch_id: string;
  severity_delta: number;
  new_severity: number;
  affected_systems: string[];
  newly_affected_systems: string[];
  recovered_systems: string[];
  cascade_paths: string[][];
  contract_exposure: ContractExposure[];
  revenue_at_risk: number;
  revenue_delta: number;
  world_delta: string;
  citations: Citation[];
};

export type TurnRecord = {
  turn_number: number;
  situation: string;
  decision: {
    id: string;
    label: string;
    description: string;
    action_type?: string;
  };
  npc_reactions: NPCReaction[];
  consequence: ConsequenceDelta;
  citations: Citation[];
};

export type TimelineNode = {
  node_id: string;
  session_id: string;
  parent_node_id: string | null;
  turn_number: number;
  decision_id: string | null;
  decision_label: string | null;
  severity: number;
  affected_systems: string[];
  revenue_at_risk: number;
  revenue_delta: number;
  world_delta: string;
  branch_id: string;
  created_at: string;
};

export type TimelineEdge = {
  from: string;
  to: string;
  label: string;
};

export type TimelineResponse = {
  session_id: string;
  root_node_id: string;
  nodes: TimelineNode[];
  edges: TimelineEdge[];
  summary: {
    total_nodes: number;
    max_severity: number;
    max_revenue_at_risk: number;
    final_severity: number;
    final_revenue_at_risk: number;
  };
};

export type ScoreDimension = {
  score: number;
  weight: number;
  label?: string;
  description?: string;
  linked_skills?: string[];
  linked_certifications?: string[];
  citations?: Citation[];
};

export type FailureMode = {
  mode_id: string;
  description: string;
  linked_dimensions: string[];
};

export type SkillGap = {
  skill_id: string;
  dimension_id: string;
  severity: string;
  recommended_practice_scenario: string;
  rationale: string;
  citations: Citation[];
};

export type CertificationAlignment = {
  certification_id: string;
  alignment_score: number;
  risk: string;
  note: string;
  source_mode: "learn-mcp" | "local-fallback";
  learn_context_available: boolean;
  linked_dimensions?: string[];
  citations?: Citation[];
};

export type NextBestAction = {
  action_id: string;
  title: string;
  rationale: string;
  estimated_minutes: number;
  citations: Citation[];
};

export type CompetenceReport = {
  report_id: string;
  session_id: string;
  overall_score: number;
  readiness_band: string;
  executive_summary: string;
  dimensions: Record<string, ScoreDimension>;
  evidence_trail: Array<{
    evidence_id: string;
    turn_number: number;
    observation: string;
    impact: string;
    linked_dimension: string;
    citations: Citation[];
  }>;
  failure_modes: FailureMode[];
  skill_gaps: SkillGap[];
  certification_alignment: CertificationAlignment[];
  next_best_actions: NextBestAction[];
  citations: Citation[];
};

export type CoachPlan = {
  top_gap: string;
  top_gap_dimension?: string;
  micro_plan: Array<{
    step: number;
    title: string;
    activity: string;
    estimated_minutes: number;
    success_criteria: string;
  }>;
  practice_scenario: string;
  manager_note?: string;
  citations: Citation[];
};

export type SimulationRun = {
  session_id: string;
  scenario: {
    id: string;
    title: string;
    role_id: string;
    initial_stakes: string;
    industry?: string;
    difficulty?: string;
    estimated_minutes?: number;
    data_classification?: string;
    intro?: string;
    citations?: Citation[];
  };
  turns: TurnRecord[];
  timeline: TimelineResponse;
  final_score: CompetenceReport & { score?: number };
  coach_plan: CoachPlan;
  saved_at?: string;
};

export type StreamEventName =
  | "session_started"
  | "scenario_intro"
  | "turn_started"
  | "decision_selected"
  | "npc_reaction"
  | "consequence_delta"
  | "timeline_updated"
  | "score_final"
  | "coach_plan"
  | "manager_snapshot"
  | "session_completed";

export type StreamEventEnvelope = {
  event: StreamEventName;
  session_id: string;
  sequence: number;
  data: Record<string, unknown>;
};

export type StreamStatus = "idle" | "connecting" | "live" | "completed" | "error";
export type PlaybackStatus = "idle" | "buffering" | "playing" | "paused" | "completed" | "error";
export type PlaybackSpeed = 0.75 | 1 | 1.25;

export type ManagerFragilityMap = {
  generated_at: string;
  session_count: number;
  team_readiness: {
    average_score: number;
    band_distribution: Record<string, number>;
    highest_risk_dimension: string | null;
    highest_risk_skill: string | null;
  };
  role_risk: Array<{
    role_id: string;
    sessions: number;
    average_score: number;
    risk_band: string;
    weak_dimensions: string[];
    recommended_manager_action: string;
  }>;
  skill_fragility: Array<{
    skill_id: string;
    linked_dimension: string;
    risk_score: number;
    evidence_count: number;
    recommended_intervention: string;
  }>;
  certification_readiness: Array<{
    certification_id: string;
    alignment_score: number;
    risk: string;
    note: string;
  }>;
  privacy_note: string;
};

export type ReadinessSummary = {
  average_score: number;
  highest_risk_dimension: string | null;
  recommended_action: string;
  session_count: number;
};

export type McpTool = {
  name: string;
  description: string;
  input_schema: Record<string, string>;
};

export type McpToolsResponse = {
  mode: string;
  tools: McpTool[];
};

export type McpDemoResponse = {
  tools: string[];
  started: {
    session_id: string;
    scenario_id: string;
    current_situation: string;
  };
  situation: {
    current_turn: number;
    revenue_at_risk: number;
    citation_count: number;
  };
  decision: {
    decision: string;
    new_severity: number;
    world_delta: string;
  };
  competence_report: {
    session_id: string;
    overall_score: number;
    readiness_band: string;
    evidence_count: number;
  };
};

export type BranchComparison = {
  original_final_score: number;
  alternative_projected_score: number;
  score_delta: number;
  original_max_revenue_at_risk: number;
  alternative_revenue_at_risk: number;
  alternative_max_revenue_at_risk: number;
  revenue_at_risk_delta: number;
  original_final_severity: number;
  alternative_final_severity: number;
  severity_delta: number;
  reasoning_summary: string;
};

export type ReplayBranchResult = {
  source_session_id: string;
  new_session_id: string;
  branched_from_node_id: string;
  alternative_decision: TurnRecord["decision"];
  original_path_summary: Record<string, unknown>;
  alternative_path_summary: Record<string, unknown>;
  timeline: TimelineResponse;
  comparison: BranchComparison;
  citations: Citation[];
};
