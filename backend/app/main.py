import os

from fastapi import Body, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from app.grounding.foundry_iq import grounded_answer
from app.grounding.learn_mcp import certification_context, search_learn_docs
from app.grounding.status import get_grounding_status
from app.eval.harness import run_eval_suite
from app.insights.manager import build_fragility_map
from app.mcp_server.tools import list_registered_tools, run_local_demo
from app.ontology.graph import affected_systems, load_ontology, revenue_at_risk, summarize_graph
from app.orchestration.turn_loop import run_simulation
from app.replay.time_travel import branch_from_session
from app.scenarios.library import (
    get_scenario,
    list_scenarios,
    list_workspace_scenarios,
    save_workspace_scenario,
)
from app.scenarios.validators import validate_no_sensitive_content, validate_scenario_pack
from app.scoring.competence_report import generate_competence_report
from app.schemas import (
    BranchFromRequest,
    CompetenceReport,
    CustomScenarioRunRequest,
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
from app.telemetry.events import list_recent_events, telemetry_summary
from app.telemetry.tracing import initialize_tracing
from app.voice.speech import (
    AUDIO_ROOT,
    configured_voices,
    is_speech_configured,
    synthesize_npc_line,
)
from app.workspace.config import (
    configure_organization,
    disable_examples,
    enable_examples,
    workspace_status,
)
from app.workspace.setup import (
    apply_creator_operations_template,
    apply_eduky_template,
    apply_workspace_template,
    setup_empty_workspace,
)
from app.workspace.storage import (
    list_knowledge_documents,
    list_profiles,
    list_roles,
    list_skills,
    save_knowledge_document,
    save_profile,
    save_role,
    save_skill,
)
from app.workspace.templates import scenario_template_catalog, workspace_template_catalog
from app.workspace.walkthrough import workspace_walkthrough


LOCAL_DEVELOPMENT_ORIGINS = (
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
)
AZURE_CONTAINER_APPS_ORIGIN_REGEX = r"https://.*\.azurecontainerapps\.io"


def normalize_origin(value: str | None) -> str:
    return (value or "").strip().rstrip("/")


def build_allowed_origins(
    frontend_url: str | None = None,
    allowed_origins: str | None = None,
) -> list[str]:
    candidates = [
        *LOCAL_DEVELOPMENT_ORIGINS,
        normalize_origin(frontend_url),
        *(
            normalize_origin(origin)
            for origin in (allowed_origins or "").split(",")
        ),
    ]
    return list(dict.fromkeys(origin for origin in candidates if origin))


FRONTEND_URL = normalize_origin(os.getenv("FRONTEND_URL"))
ALLOWED_ORIGINS = build_allowed_origins(
    FRONTEND_URL,
    os.getenv("ALLOWED_ORIGINS"),
)
APP_ENVIRONMENT = (
    os.getenv("ENVIRONMENT")
    or os.getenv("APP_ENV")
    or "development"
).strip() or "development"

app = FastAPI(title="CRISOL Backend", version="1.0.0-rc.2")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=AZURE_CONTAINER_APPS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
AUDIO_ROOT.mkdir(parents=True, exist_ok=True)
app.mount("/audio", StaticFiles(directory=AUDIO_ROOT), name="audio")
_GRAPH = load_ontology()
initialize_tracing()


@app.get("/health", response_model=HealthResponse)
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "crisol-backend",
        "phase": "10.3-workspace-packaging",
    }


@app.get("/debug/cors")
def debug_cors() -> dict[str, str | list[str]]:
    return {
        "frontend_url": FRONTEND_URL,
        "allowed_origins": ALLOWED_ORIGINS,
        "allow_origin_regex": AZURE_CONTAINER_APPS_ORIGIN_REGEX,
        "environment": APP_ENVIRONMENT,
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
        "grounding_mode": result["grounding_mode"],
    }


@app.get("/grounding/status")
def grounding_status() -> dict:
    return get_grounding_status()


@app.get("/grounding/learn/test")
def learn_grounding_test(q: str = Query(..., min_length=1)) -> dict:
    return search_learn_docs(q)


@app.get("/grounding/learn/certification/{certification_id}")
def learn_certification_context(certification_id: str) -> dict:
    return certification_context(certification_id)


@app.get("/mcp/tools")
def mcp_tools() -> dict:
    return {
        "mode": "fastmcp-and-local-registry",
        "tools": list_registered_tools(),
    }


@app.post("/mcp/demo")
def mcp_demo() -> dict:
    return run_local_demo()


@app.get("/workspace/status")
def workspace_status_endpoint() -> dict:
    return workspace_status()


@app.post("/workspace/initialize-empty")
def workspace_initialize_empty() -> dict:
    return setup_empty_workspace()


@app.post("/workspace/enable-examples")
def workspace_enable_examples() -> dict:
    return enable_examples()


@app.post("/workspace/disable-examples")
def workspace_disable_examples() -> dict:
    return disable_examples()


@app.post("/workspace/apply-template/eduky")
def workspace_apply_eduky_template() -> dict:
    return apply_eduky_template()


@app.post("/workspace/apply-template/creator-operations")
def workspace_apply_creator_operations_template() -> dict:
    return apply_creator_operations_template()


@app.post("/workspace/apply-template/{template_id}")
def workspace_apply_template(template_id: str) -> dict:
    try:
        return apply_workspace_template(template_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get("/workspace/walkthrough")
def workspace_walkthrough_endpoint() -> dict:
    return workspace_walkthrough()


@app.post("/workspace/configure-organization")
def workspace_configure_organization(organization: dict = Body(...)) -> dict:
    try:
        return configure_organization(organization)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/workspace/knowledge")
def workspace_knowledge() -> list[dict]:
    return list_knowledge_documents()


@app.post("/workspace/knowledge")
def workspace_save_knowledge(document: dict = Body(...)) -> dict:
    try:
        return save_knowledge_document(
            str(document.get("file_name", "")),
            str(document.get("content", "")),
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/workspace/roles")
def workspace_roles() -> list[dict]:
    return list_roles()


@app.post("/workspace/roles")
def workspace_save_role(role: dict = Body(...)) -> dict:
    try:
        return save_role(role)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/workspace/skills")
def workspace_skills() -> list[dict]:
    return list_skills()


@app.post("/workspace/skills")
def workspace_save_skill(skill: dict = Body(...)) -> dict:
    try:
        return save_skill(skill)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/workspace/profiles")
def workspace_profiles() -> list[dict]:
    return list_profiles()


@app.post("/workspace/profiles")
def workspace_save_profile(profile: dict = Body(...)) -> dict:
    try:
        return save_profile(profile)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/workspace/scenarios")
def workspace_scenarios() -> list[dict]:
    return list_workspace_scenarios()


@app.post("/workspace/scenarios")
def workspace_save_scenario(pack: dict = Body(...)) -> dict:
    try:
        return save_workspace_scenario(pack)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/workspace/templates")
def workspace_templates() -> list[dict]:
    return workspace_template_catalog()


@app.get("/workspace/scenario-templates")
def workspace_scenario_templates() -> list[dict]:
    return scenario_template_catalog()


@app.get("/scenarios")
def scenarios() -> list[dict]:
    return list_scenarios()


@app.post("/scenarios/validate")
def scenarios_validate(pack: dict = Body(...)) -> dict:
    structural_errors = validate_scenario_pack(pack)
    safety_errors = validate_no_sensitive_content(pack)
    errors = [*structural_errors, *safety_errors]
    return {
        "valid": not errors,
        "scenario_id": pack.get("scenario_id"),
        "errors": errors,
        "structural_errors": structural_errors,
        "safety_errors": safety_errors,
    }


@app.get("/scenarios/{scenario_id}")
def scenario_pack(scenario_id: str) -> dict:
    try:
        return get_scenario(scenario_id)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.post("/scenario/run-custom", response_model=SimulationRunResponse)
def scenario_run_custom(request: CustomScenarioRunRequest) -> dict:
    try:
        pack = get_scenario(request.scenario_id)
        role_id = request.role_id or pack["role_id"]
        return run_simulation(
            role_id=role_id,
            scenario_seed=request.scenario_id,
            auto_mode=True,
        )
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/scenario/stream-custom")
def scenario_stream_custom(
    scenario_id: str = Query(..., min_length=1),
    role_id: str | None = Query(default=None),
) -> StreamingResponse:
    try:
        pack = get_scenario(scenario_id)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    selected_role = role_id or pack["role_id"]
    if selected_role != pack["role_id"]:
        raise HTTPException(
            status_code=400,
            detail=f"Scenario {scenario_id} is assigned to {pack['role_id']}, not {selected_role}.",
        )
    return StreamingResponse(
        scenario_event_stream(role_id=selected_role, scenario_id=scenario_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@app.get("/eval/report")
def evaluation_report() -> dict:
    return run_eval_suite()


@app.get("/telemetry/summary")
def telemetry_summary_endpoint() -> dict:
    return telemetry_summary()


@app.get("/telemetry/events")
def telemetry_events(limit: int = Query(default=50, ge=1, le=500)) -> list[dict]:
    return list_recent_events(limit=limit)


@app.post("/replay/branch-from")
def replay_branch_from(request: BranchFromRequest) -> dict:
    try:
        return branch_from_session(
            request.session_id,
            request.decision_node_id,
            request.alternative_action,
        )
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/scenario/run", response_model=SimulationRunResponse)
def scenario_run(role_id: str = Query(default="ROLE-SRE")) -> dict:
    try:
        return run_simulation(role_id=role_id, auto_mode=True)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


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
    persona: str = Query(default="Operations Lead", min_length=1, max_length=80),
) -> dict:
    return synthesize_npc_line(
        text,
        persona,
        session_id="SES-VOICE-TEST",
        event_id="EVT-VOICE-TEST",
    )


@app.get("/scenario/run/timeline", response_model=TimelineResponse)
def scenario_run_timeline(role_id: str = Query(default="ROLE-SRE")) -> dict:
    try:
        return run_simulation(role_id=role_id, auto_mode=True)["timeline"]
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


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
