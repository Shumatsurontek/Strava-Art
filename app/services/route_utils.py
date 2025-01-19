import networkx as nx
import osmnx as ox


def create_circular_route(graph, center_node, distance):
    radius = distance / 2  # Rayon approximatif en mètres
    bbox = ox.utils_geo.bbox_from_point(
        (graph.nodes[center_node]['y'], graph.nodes[center_node]['x']), dist=radius
    )

    subgraph = ox.truncate.truncate_graph_bbox(graph, *bbox)
    if len(subgraph.nodes) == 0:
        raise ValueError("No nodes found within the specified radius")

    nodes_within_radius = list(subgraph.nodes)
    target_node = nodes_within_radius[len(nodes_within_radius) // 2]

    route_to_target = nx.shortest_path(graph, source=center_node, target=target_node, weight='length')
    route_back = nx.shortest_path(graph, source=target_node, target=center_node, weight='length')

    return route_to_target + route_back


def create_square_route(graph, center_node, distance):
    center_lat = graph.nodes[center_node]['y']
    center_lon = graph.nodes[center_node]['x']
    half_side = distance / 2

    corners = [
        (center_lat + 0.0001 * half_side, center_lon - 0.0001 * half_side),
        (center_lat + 0.0001 * half_side, center_lon + 0.0001 * half_side),
        (center_lat - 0.0001 * half_side, center_lon + 0.0001 * half_side),
        (center_lat - 0.0001 * half_side, center_lon - 0.0001 * half_side),
    ]

    corner_nodes = [ox.distance.nearest_nodes(graph, lon, lat) for lat, lon in corners]

    route = []
    current_node = center_node
    for corner_node in corner_nodes:
        segment = nx.shortest_path(graph, source=current_node, target=corner_node, weight='length')
        route.extend(segment[:-1])
        current_node = corner_node

    segment = nx.shortest_path(graph, source=current_node, target=center_node, weight='length')
    route.extend(segment)

    return route
