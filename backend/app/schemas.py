from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: str
    service: str
    phase: str


class OntologySummary(BaseModel):
    total_nodes: int
    total_edges: int
    counts_by_node_type: dict[str, int]


class RevenueAtRiskResponse(BaseModel):
    initial_systems: list[str]
    affected_systems: list[str]
    revenue_at_risk: float


class Citation(BaseModel):
    doc_id: str
    title: str
    file_name: str
    chunk_id: str
    quote: str


class GroundingTestResponse(BaseModel):
    query: str
    answer: str
    citations: list[Citation]
    mode: str


class ScenarioOption(BaseModel):
    id: str
    label: str
    description: str
    competencies: list[str]


class ScenarioSeed(BaseModel):
    id: str
    title: str
    role_id: str
    impacted_systems: list[str]
    initial_stakes: str
    options: list[ScenarioOption]
    expected_competencies: list[str]


class NPCReaction(BaseModel):
    persona: str
    tone: str
    message: str
    pressure_level: int


class ContractExposure(BaseModel):
    contract_id: str
    criticality: str
    systems: list[str]
    revenue_per_hour: float
    exposure: float


class ConsequenceDelta(BaseModel):
    branch_id: str
    severity_delta: int
    new_severity: int
    affected_systems: list[str]
    newly_affected_systems: list[str]
    recovered_systems: list[str]
    cascade_paths: list[list[str]]
    contract_exposure: list[ContractExposure]
    revenue_at_risk: float
    revenue_delta: float
    world_delta: str
    citations: list[Citation]


class TurnRecord(BaseModel):
    turn_number: int
    situation: str
    decision: dict
    npc_reactions: list[NPCReaction]
    consequence: ConsequenceDelta
    citations: list[Citation]


class ScoreDimension(BaseModel):
    score: float
    weight: float
    label: str | None = None
    description: str | None = None
    linked_skills: list[str] | None = None
    linked_certifications: list[str] | None = None


class EvidenceItem(BaseModel):
    evidence_id: str
    turn_number: int
    observation: str
    impact: str
    linked_dimension: str
    citations: list[Citation]


class FailureMode(BaseModel):
    mode_id: str
    description: str
    linked_dimensions: list[str]


class SkillGap(BaseModel):
    skill_id: str
    dimension_id: str
    severity: str
    recommended_practice_scenario: str
    rationale: str
    citations: list[Citation]


class CertificationAlignment(BaseModel):
    certification_id: str
    alignment_score: float
    risk: str
    note: str
    linked_dimensions: list[str] | None = None
    citations: list[Citation] | None = None


class NextBestAction(BaseModel):
    action_id: str
    title: str
    rationale: str
    estimated_minutes: int
    citations: list[Citation]


class ScoreReport(BaseModel):
    report_id: str | None = None
    score: float
    overall_score: float | None = None
    readiness_band: str | None = None
    executive_summary: str | None = None
    dimensions: dict[str, ScoreDimension]
    evidence_trail: list[EvidenceItem] | None = None
    failure_modes: list[FailureMode]
    skill_gaps: list[SkillGap] | None = None
    certification_alignment: list[CertificationAlignment] | None = None
    next_best_actions: list[NextBestAction] | None = None
    citations: list[Citation]


class CoachStep(BaseModel):
    step: int
    title: str
    activity: str
    estimated_minutes: int
    success_criteria: str


class CoachPlan(BaseModel):
    top_gap: str
    top_gap_dimension: str | None = None
    micro_plan: list[CoachStep]
    practice_scenario: str
    manager_note: str | None = None
    citations: list[Citation]


class CompetenceReport(BaseModel):
    report_id: str
    session_id: str
    overall_score: float
    readiness_band: str
    executive_summary: str
    dimensions: dict[str, ScoreDimension]
    evidence_trail: list[EvidenceItem]
    failure_modes: list[FailureMode]
    skill_gaps: list[SkillGap]
    certification_alignment: list[CertificationAlignment]
    next_best_actions: list[NextBestAction]
    citations: list[Citation]


class TimelineNode(BaseModel):
    node_id: str
    session_id: str
    parent_node_id: str | None
    turn_number: int
    decision_id: str | None
    decision_label: str | None
    severity: int
    affected_systems: list[str]
    revenue_at_risk: float
    revenue_delta: float
    world_delta: str
    branch_id: str
    created_at: str


class TimelineEdge(BaseModel):
    from_: str = Field(alias="from")
    to: str
    label: str

    model_config = ConfigDict(populate_by_name=True)


class TimelineSummary(BaseModel):
    total_nodes: int
    max_severity: int
    max_revenue_at_risk: float
    final_severity: int
    final_revenue_at_risk: float


class TimelineResponse(BaseModel):
    session_id: str
    root_node_id: str
    nodes: list[TimelineNode]
    edges: list[TimelineEdge]
    summary: TimelineSummary


class SavedSessionSummary(BaseModel):
    session_id: str
    scenario_id: str
    scenario_title: str
    turn_count: int
    final_score: float | None
    saved_at: str | None
    file_name: str


class RoleRisk(BaseModel):
    role_id: str
    sessions: int
    average_score: float
    risk_band: str
    weak_dimensions: list[str]
    recommended_manager_action: str


class SkillFragility(BaseModel):
    skill_id: str
    linked_dimension: str
    risk_score: float
    evidence_count: int
    recommended_intervention: str


class CertificationReadiness(BaseModel):
    certification_id: str
    alignment_score: float
    risk: str
    note: str


class TeamReadiness(BaseModel):
    average_score: float
    band_distribution: dict[str, int]
    highest_risk_dimension: str | None
    highest_risk_skill: str | None


class ManagerFragilityMap(BaseModel):
    generated_at: str
    session_count: int
    team_readiness: TeamReadiness
    role_risk: list[RoleRisk]
    skill_fragility: list[SkillFragility]
    certification_readiness: list[CertificationReadiness]
    privacy_note: str


class ManagerReadinessSummary(BaseModel):
    average_score: float
    highest_risk_dimension: str | None
    recommended_action: str
    session_count: int


class SimulationRunResponse(BaseModel):
    session_id: str
    scenario: dict
    turns: list[TurnRecord]
    timeline: TimelineResponse
    final_score: ScoreReport
    coach_plan: CoachPlan
    saved_at: str | None = None
