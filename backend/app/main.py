from fastapi import FastAPI, Query

from app.ontology.graph import affected_systems, load_ontology, revenue_at_risk, summarize_graph
from app.schemas import HealthResponse, OntologySummary, RevenueAtRiskResponse


app = FastAPI(title="CRISOL Backend", version="0.1.0")
_GRAPH = load_ontology()


@app.get("/health", response_model=HealthResponse)
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "crisol-backend",
        "phase": "1-scaffold",
    }


@app.get("/ontology/summary", response_model=OntologySummary)
def ontology_summary() -> dict:
    return summarize_graph(_GRAPH)


@app.get("/ontology/revenue-at-risk", response_model=RevenueAtRiskResponse)
def ontology_revenue_at_risk(
    systems: str = Query(default="SVC-checkout", description="Comma-separated system IDs"),
) -> dict:
    initial_systems = [system.strip() for system in systems.split(",") if system.strip()]
    impacted = affected_systems(_GRAPH, initial_systems)
    return {
        "initial_systems": initial_systems,
        "affected_systems": impacted,
        "revenue_at_risk": revenue_at_risk(_GRAPH, impacted),
    }
