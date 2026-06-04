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
