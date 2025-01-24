import networkx as nx
import osmnx as ox
from geopy.geocoders import Nominatim
import math

def get_center_node(graph, city):
    """Trouve le nœud central basé sur la localisation de la ville."""
    geolocator = Nominatim(user_agent="gpx_art")
    location = geolocator.geocode(city)

    if location is None:
        raise ValueError(f"City '{city}' not found.")

    print(f"Location for '{city}': lat={location.latitude}, lon={location.longitude}")

    try:
        center_node = ox.distance.nearest_nodes(graph, location.longitude, location.latitude)
        return center_node, (location.latitude, location.longitude)
    except Exception as e:
        raise ValueError(f"Error finding nearest node for '{city}': {e}")

def create_circular_route(graph, center_node, distance):
    """Crée une route circulaire autour d'un nœud central."""
    radius = distance / 2
    center_lat = graph.nodes[center_node]['y']
    center_lon = graph.nodes[center_node]['x']

    north = center_lat + (radius / 111111)  # 111,111 m = 1° de latitude
    south = center_lat - (radius / 111111)
    east = center_lon + (radius / (111111 * abs(math.cos(math.radians(center_lat)))))
    west = center_lon - (radius / (111111 * abs(math.cos(math.radians(center_lat)))))

    bbox = (north, south, east, west)

    print("Arguments pour truncate_graph_bbox :")
    print(f"Graphe : {graph}")
    print(f"Bbox : (north={north}, south={south}, east={east}, west={west})")

    subgraph = ox.truncate.truncate_graph_bbox(graph, bbox)  # Version >= 1.0.0

    if len(subgraph.nodes) == 0:
        raise ValueError("No nodes found within the specified radius")

    nodes_within_radius = list(subgraph.nodes)
    target_node = nodes_within_radius[len(nodes_within_radius) // 2]
    route_to_target = nx.shortest_path(graph, source=center_node, target=target_node, weight='length')
    route_back = nx.shortest_path(graph, source=target_node, target=center_node, weight='length')

    return route_to_target + route_back

def create_square_route(graph, center_node, distance):
    """Crée une route carrée autour d'un nœud central."""
    try:
        center_lat = graph.nodes[center_node]['y']
        center_lon = graph.nodes[center_node]['x']
    except KeyError as e:
        raise ValueError(f"Error accessing node data: {e}")

    half_side = distance / 2

    corners = [
        (center_lat + 0.0001 * half_side, center_lon - 0.0001 * half_side),
        (center_lat + 0.0001 * half_side, center_lon + 0.0001 * half_side),
        (center_lat - 0.0001 * half_side, center_lon + 0.0001 * half_side),
        (center_lat - 0.0001 * half_side, center_lon - 0.0001 * half_side),
    ]

    corner_nodes = []
    for lat, lon in corners:
        try:
            corner_node = ox.distance.nearest_nodes(graph, lon, lat)
            corner_nodes.append(corner_node)
        except Exception as e:
            raise ValueError(f"Error finding nearest node for corner ({lat}, {lon}): {e}")

    route = []
    current_node = center_node
    for corner_node in corner_nodes:
        try:
            segment = nx.shortest_path(graph, source=current_node, target=corner_node, weight='length')
            route.extend(segment[:-1])
            current_node = corner_node
        except nx.NetworkXNoPath:
            raise ValueError(f"No path between {current_node} and {corner_node}")

    segment = nx.shortest_path(graph, source=current_node, target=center_node, weight='length')
    route.extend(segment)

    return route