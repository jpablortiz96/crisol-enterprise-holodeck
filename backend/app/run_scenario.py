import argparse
from typing import Any

from app.orchestration.turn_loop import run_simulation


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a local CRISOL scenario simulation.")
    parser.add_argument("--role", default="ROLE-SRE", help="Role ID to simulate.")
    parser.add_argument("--scenario", default=None, help="Optional scenario seed ID.")
    args = parser.parse_args()

    session = run_simulation(role_id=args.role, scenario_seed=args.scenario, auto_mode=True)
    _print_session(session)


def _print_session(session: dict[str, Any]) -> None:
    scenario = session["scenario"]
    print("CRISOL Terminal Simulation")
    print("=" * 26)
    print(f"Session: {session['session_id']}")
    print(f"Scenario: {scenario['title']}")
    print()
    print("Scenario Intro")
    print(scenario["intro"])
    _print_citations(scenario["citations"])

    for turn in session["turns"]:
        consequence = turn["consequence"]
        print()
        print(f"Turn {turn['turn_number']}")
        print("-" * 12)
        print(f"Situation: {turn['situation']}")
        print(f"Learner decision: {turn['decision']['label']}")
        print("NPC reactions:")
        for reaction in turn["npc_reactions"]:
            print(
                f"  - {reaction['persona']} ({reaction['tone']}, pressure {reaction['pressure_level']}): "
                f"{reaction['message']}"
            )
        print(
            "Consequence delta: "
            f"{consequence['world_delta']} "
            f"Severity {consequence['severity_delta']:+d} -> {consequence['new_severity']}; "
            f"revenue at risk {consequence['revenue_at_risk']} "
            f"({consequence['revenue_delta']:+.1f})"
        )
        print(f"Affected systems: {', '.join(consequence['affected_systems'])}")
        print(f"Newly affected: {', '.join(consequence['newly_affected_systems']) or 'none'}")
        print(f"Recovered: {', '.join(consequence['recovered_systems']) or 'none'}")
        print("Cascade paths:")
        for path in consequence["cascade_paths"][:3]:
            print(f"  - {' -> '.join(path)}")
        print("Contract exposure:")
        for exposure in consequence["contract_exposure"][:4]:
            print(
                f"  - {exposure['contract_id']} ({exposure['criticality']}): "
                f"{exposure['exposure']} across {', '.join(exposure['systems'])}"
            )
        _print_citations(turn["citations"])

    score = session["final_score"]
    print()
    print("Final Competence Score")
    print("-" * 24)
    print(f"Score: {score['score']}")
    print("Dimensions:")
    for name, dimension in score["dimensions"].items():
        print(f"  - {name}: {dimension['score']} (weight {dimension['weight']})")
    print("Failure modes:")
    for failure in score["failure_modes"]:
        print(f"  - {failure}")
    _print_citations(score["citations"])

    coach_plan = session["coach_plan"]
    print()
    print("Coach Debrief")
    print("-" * 13)
    print(f"Top gap: {coach_plan['top_gap']}")
    print("Micro-learning plan:")
    for item in coach_plan["micro_plan"]:
        print(f"  - {item}")
    print(f"Practice scenario: {coach_plan['practice_scenario']}")
    _print_citations(coach_plan["citations"])


def _print_citations(citations: list[dict[str, Any]]) -> None:
    print("Citations:")
    if not citations:
        print("  - none")
        return
    seen = set()
    for citation in citations:
        key = (citation["doc_id"], citation["chunk_id"])
        if key in seen:
            continue
        seen.add(key)
        print(f"  - {citation['doc_id']} | {citation['file_name']} | {citation['chunk_id']}")


if __name__ == "__main__":
    main()
