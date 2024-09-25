from domain.models.affiliation_calculations_model import Calculations


def parse_institutional_coauthorship_network(data: Calculations) -> dict:
    network = data.coauthorship_network
    nodes = sorted(network.nodes, key=lambda x: x.degree, reverse=True)[:50]
    nodes_ids = [node.id for node in nodes]
    edges = []
    nodes = [node.model_dump() for node in nodes]
    for edge in network.edges:
        if edge.source in nodes_ids and edge.target in nodes_ids:
            edges.append(edge.model_dump())
    return {"plot": {"nodes": nodes, "edges": edges}}
