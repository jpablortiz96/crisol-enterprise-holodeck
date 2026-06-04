from fastapi import FastAPI, HTTPException, Query

from app.grounding.foundry_iq import grounded_answer
from app.ontology.graph import affected_systems, load_ontology, revenue_at_risk, summarize_graph
from app.orchestration.turn_loop import run_simulation
from app.schemas import (
    GroundingTestResponse,
    HealthResponse,
    OntologySummary,
    RevenueAtRiskResponse,
    SavedSessionSummary,
    SimulationRunResponse,
    TimelineResponse,
)
from app.storage.session_store import list_sessions, load_session


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


@app.get("/grounding/test", response_model=GroundingTestResponse)
def grounding_test(q: str = Query(..., min_length=1)) -> dict:
    result = grounded_answer(q)
    return {
        "query": q,
        "answer": result["answer"],
        "citations": result["citations"],
        "mode": result["mode"],
    }


@app.get("/scenario/run", response_model=SimulationRunResponse)
def scenario_run(role_id: str = Query(default="ROLE-SRE")) -> dict:
    return run_simulation(role_id=role_id, auto_mode=True)


@app.get("/scenario/run/timeline", response_model=TimelineResponse)
def scenario_run_timeline(role_id: str = Query(default="ROLE-SRE")) -> dict:
    return run_simulation(role_id=role_id, auto_mode=True)["timeline"]


@app.get("/scenario/sessions", response_model=list[SavedSessionSummary])
def scenario_sessions() -> list[dict]:
    return list_sessions()


@app.get("/scenario/{session_id}/timeline", response_model=TimelineResponse)
def scenario_session_timeline(session_id: str) -> dict:
    try:
        return load_session(session_id)["timeline"]
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get("/scenario/{session_id}", response_model=SimulationRunResponse)
def scenario_session(session_id: str) -> dict:
    try:
        return load_session(session_id)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
