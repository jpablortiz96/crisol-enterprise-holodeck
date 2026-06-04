from pydantic import BaseModel


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


class ConsequenceDelta(BaseModel):
    branch_id: str
    severity_delta: int
    new_severity: int
    affected_systems: list[str]
    revenue_at_risk: float
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


class SimulationRunResponse(BaseModel):
    session_id: str
    scenario: dict
    turns: list[TurnRecord]
    final_score: ScoreReport
    coach_plan: CoachPlan
