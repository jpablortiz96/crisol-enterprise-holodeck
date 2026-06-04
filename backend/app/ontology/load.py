from app.ontology.graph import (
    affected_systems,
    load_ontology,
    revenue_at_risk,
    role_readiness,
    summarize_graph,
)


def main() -> None:
    graph = load_ontology()
    summary = summarize_graph(graph)
    checkout_affected = affected_systems(graph, ["SVC-checkout"])
    checkout_revenue = revenue_at_risk(graph, checkout_affected)
    sre_readiness = role_readiness(graph, "L-1001", "ROLE-SRE")

    print(f"total nodes: {summary['total_nodes']}")
    print(f"total edges: {summary['total_edges']}")
    print("counts by node type:")
    for node_type, count in summary["counts_by_node_type"].items():
        print(f"  {node_type}: {count}")
    print(f"sample affected systems for SVC-checkout: {', '.join(checkout_affected)}")
    print(f"sample revenue at risk: {checkout_revenue}")
    print("sample readiness for learner L-1001 and ROLE-SRE:")
    print(f"  readiness_score: {sre_readiness['readiness_score']}")
    print(f"  missing_skills: {', '.join(sre_readiness['missing_skills']) or 'none'}")
    print(f"  missing_certifications: {', '.join(sre_readiness['missing_certifications']) or 'none'}")


if __name__ == "__main__":
    main()
