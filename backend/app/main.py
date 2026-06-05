import os

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from app.grounding.foundry_iq import grounded_answer
from app.insights.manager import build_fragility_map
from app.ontology.graph import affected_systems, load_ontology, revenue_at_risk, summarize_graph
from app.orchestration.turn_loop import run_simulation
from app.scoring.competence_report import generate_competence_report
from app.schemas import (
    CompetenceReport,
    GroundingTestResponse,
    HealthResponse,
    ManagerFragilityMap,
    ManagerReadinessSummary,
    OntologySummary,
    RevenueAtRiskResponse,
    SavedSessionSummary,
    SimulationRunResponse,
    TimelineResponse,
    VoiceStatusResponse,
    VoiceSynthesisResult,
)
from app.streaming.sse import scenario_event_stream
from app.storage.session_store import list_sessions, load_session
from app.voice.speech import (
    AUDIO_ROOT,
    configured_voices,
    is_speech_configured,
    synthesize_npc_line,
)


app = FastAPI(title="CRISOL Backend", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
AUDIO_ROOT.mkdir(parents=True, exist_ok=True)
app.mount("/audio", StaticFiles(directory=AUDIO_ROOT), name="audio")
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


@app.get("/scenario/stream")
def scenario_stream(role_id: str = Query(default="ROLE-SRE")) -> StreamingResponse:
    return StreamingResponse(
        scenario_event_stream(role_id=role_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@app.get("/voice/status", response_model=VoiceStatusResponse)
def voice_status() -> dict:
    configured = is_speech_configured()
    return {
        "configured": configured,
        "provider": "azure-speech" if configured else "text-only",
        "region_configured": bool(os.getenv("AZURE_SPEECH_REGION")),
        "voices": configured_voices(),
    }


@app.get("/voice/test", response_model=VoiceSynthesisResult)
def voice_test(
    text: str = Query(default="hello", min_length=1, max_length=450),
    persona: str = Query(default="VP Operations", min_length=1, max_length=80),
) -> dict:
    return synthesize_npc_line(
        text,
        persona,
        session_id="SES-VOICE-TEST",
        event_id="EVT-VOICE-TEST",
    )


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


@app.get("/reports/competence/{session_id}", response_model=CompetenceReport)
def competence_report(session_id: str) -> dict:
    try:
        return generate_competence_report(load_session(session_id))
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get("/reports/latest", response_model=CompetenceReport)
def latest_report() -> dict:
    sessions = list_sessions()
    if not sessions:
        raise HTTPException(status_code=404, detail="No saved sessions found. Run a scenario first.")
    return generate_competence_report(load_session(sessions[0]["session_id"]))


@app.get("/manager/fragility-map", response_model=ManagerFragilityMap)
def manager_fragility_map() -> dict:
    return build_fragility_map()


@app.get("/manager/readiness-summary", response_model=ManagerReadinessSummary)
def manager_readiness_summary() -> dict:
    fragility_map = build_fragility_map()
    team = fragility_map["team_readiness"]
    role_risk = fragility_map.get("role_risk", [])
    recommended_action = (
        role_risk[0]["recommended_manager_action"]
        if role_risk
        else "Run a scenario first to populate synthetic readiness insights."
    )
    return {
        "average_score": team["average_score"],
        "highest_risk_dimension": team["highest_risk_dimension"],
        "recommended_action": recommended_action,
        "session_count": fragility_map["session_count"],
    }
