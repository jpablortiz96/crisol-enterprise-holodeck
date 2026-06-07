import argparse
import json
from typing import Any

from app.mcp_server.tools import (
    branch_from as branch_from_tool,
    get_competence_report as get_competence_report_tool,
    get_manager_fragility_map as get_manager_fragility_map_tool,
    get_situation as get_situation_tool,
    list_registered_tools,
    make_decision as make_decision_tool,
    run_local_demo,
    start_simulacrum as start_simulacrum_tool,
)

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    FastMCP = None


def build_mcp_server() -> Any | None:
    if FastMCP is None:
        return None

    server = FastMCP(
        "CRISOL",
        instructions=(
            "CRISOL runs sanitized role-readiness simulacrums, deterministic replay "
            "projections, cited competence reports, and aggregate manager insights."
        ),
        log_level="WARNING",
    )

    @server.tool(description="Start a sanitized CRISOL role-readiness incident simulacrum.")
    def start_simulacrum(
        role: str = "ROLE-SRE",
        difficulty: str = "standard",
        scenario_seed: str | None = None,
    ) -> dict[str, Any]:
        return start_simulacrum_tool(role, difficulty, scenario_seed)

    @server.tool(description="Get the current situation, stakes, options, and citations.")
    def get_situation(session_id: str) -> dict[str, Any]:
        return get_situation_tool(session_id)

    @server.tool(description="Apply one decision and return its modeled consequences.")
    def make_decision(session_id: str, action: str) -> dict[str, Any]:
        return make_decision_tool(session_id, action)

    @server.tool(description="Create a deterministic replay projection from a saved decision.")
    def branch_from(
        session_id: str,
        decision_node_id: str,
        alternative_action: str,
    ) -> dict[str, Any]:
        return branch_from_tool(session_id, decision_node_id, alternative_action)

    @server.tool(description="Generate a cited competence report for a sanitized training session.")
    def get_competence_report(session_id: str) -> dict[str, Any]:
        return get_competence_report_tool(session_id)

    @server.tool(description="Return the aggregate no-PII manager fragility map.")
    def get_manager_fragility_map() -> dict[str, Any]:
        return get_manager_fragility_map_tool()

    return server


MCP_SERVER = build_mcp_server()


def main() -> None:
    parser = argparse.ArgumentParser(description="CRISOL MCP server and local validation CLI.")
    parser.add_argument("--list-tools", action="store_true", help="List registered CRISOL tools.")
    parser.add_argument("--demo", action="store_true", help="Run the local CRISOL MCP demo.")
    parser.add_argument("--serve", action="store_true", help="Serve CRISOL through MCP.")
    parser.add_argument(
        "--transport",
        choices=("stdio", "sse", "streamable-http"),
        default="stdio",
        help="MCP transport used with --serve.",
    )
    arguments = parser.parse_args()

    if arguments.list_tools:
        print(json.dumps(list_registered_tools(), indent=2))
        return
    if arguments.demo:
        print(json.dumps(run_local_demo(), indent=2))
        return
    if arguments.serve:
        if MCP_SERVER is None:
            raise SystemExit("The mcp package is unavailable; use the local registry CLI.")
        MCP_SERVER.run(transport=arguments.transport)
        return
    parser.print_help()


if __name__ == "__main__":
    main()
