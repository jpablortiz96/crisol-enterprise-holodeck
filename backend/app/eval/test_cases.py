from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
REPOSITORY_ROOT = BACKEND_ROOT.parent
FRONTEND_SOURCE = REPOSITORY_ROOT / "frontend" / "src"
UI_BANNED_TERMS = (
    "hackathon",
    "contest",
    "judge",
    "submission",
    "agents league",
    "demo-only",
    "run mcp demo",
    "running demo",
    "mcp demo failed",
    "synthetic data only",
)
REQUIRED_CITATION_FIELDS = ("doc_id", "chunk_id", "quote")
REQUIRED_MCP_TOOLS = {
    "start_simulacrum",
    "get_situation",
    "make_decision",
    "branch_from",
    "get_competence_report",
    "get_manager_fragility_map",
}
