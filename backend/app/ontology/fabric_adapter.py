import networkx as nx

from app.ontology.graph import summarize_graph


def to_fabric_seed_payload(graph: nx.DiGraph) -> dict:
    summary = summarize_graph(graph)
    return {
        "source": "local-phase-1",
        "summary": summary,
        "nodes": [
            {"id": node_id, **attributes}
            for node_id, attributes in graph.nodes(data=True)
        ],
        "edges": [
            {"source": source, "target": target, **attributes}
            for source, target, attributes in graph.edges(data=True)
        ],
    }
