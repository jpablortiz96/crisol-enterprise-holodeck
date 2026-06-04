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


class ScoreReport(BaseModel):
    score: float
    dimensions: dict[str, ScoreDimension]
    failure_modes: list[str]
    citations: list[Citation]


class CoachPlan(BaseModel):
    top_gap: str
    micro_plan: list[str]
    practice_scenario: str
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


class SimulationRunResponse(BaseModel):
    session_id: str
    scenario: dict
    turns: list[TurnRecord]
    timeline: TimelineResponse
    final_score: ScoreReport
    coach_plan: CoachPlan
    saved_at: str | None = None
