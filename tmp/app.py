from flask import Flask, request, jsonify, send_file, render_template
import os
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import gpxpy.gpx
import osmnx as ox
import networkx as nx
from shapely.geometry import Point, LineString
import uuid
import folium
import traceback

app = Flask(__name__)

# Cache pour les graphes routiers
graph_cache = {}


@app.route('/')
def index():
    return render_template('index.html')  # Assure-toi que "index.html" existe dans le dossier "templates"


@app.route('/generate-trace', methods=['POST'])
def generate_trace():
    data = request.json
    city = data.get("city")
    shape = data.get("shape")  # 'circle' ou 'square'
    distance = data.get("distance")  # Distance en mètres

    if not city or not shape or not distance:
        return jsonify({"error": "city, shape, and distance are required"}), 400

    try:
        # Convertir la distance en entier
        distance = int(distance)

        # Générer le fichier GPX
        gpx_file, map_file = create_gpx(city, shape, distance)
        return jsonify({
            "gpx_file": gpx_file,
            "map_file": map_file
        })

    except Exception as e:
        traceback.print_exc()  # Affiche l'erreur complète dans la console
        return jsonify({"error": str(e)}), 500


def create_gpx(city, shape, distance):
    # Télécharger ou utiliser le graphe en cache
    if city in graph_cache:
        graph = graph_cache[city]
    else:
        graph = ox.graph_from_place(city, network_type="walk")  # Réseau piéton
        graph_cache[city] = graph

    # Obtenir les coordonnées du centre de la ville
    geolocator = Nominatim(user_agent="gpx_art")
    location = geolocator.geocode(city)
    if location is None:
        raise ValueError(f"City '{city}' not found. Please check the spelling or try a nearby location.")

    center_point = (location.latitude, location.longitude)

    # Trouver le nœud le plus proche
    center_node = ox.distance.nearest_nodes(graph, location.longitude, location.latitude)

    # Générer la route selon la forme
    if shape == "circle":
        route = create_circular_route(graph, center_node, distance)
    elif shape == "square":
        route = create_square_route(graph, center_node, distance)
    else:
        raise ValueError("Shape not supported. Choose 'circle' or 'square'.")

    # Créer un fichier GPX
    gpx = gpxpy.gpx.GPX()
    track = gpxpy.gpx.GPXTrack(name=f"{city} {shape} route")
    gpx.tracks.append(track)
    segment = gpxpy.gpx.GPXTrackSegment()
    track.segments.append(segment)

    coords = []
    for node in route:
        if 'y' in graph.nodes[node] and 'x' in graph.nodes[node]:
            lat, lon = graph.nodes[node]['y'], graph.nodes[node]['x']  # latitude, longitude
            # Validation des coordonnées
            if lat is not None and lon is not None:
                segment.points.append(gpxpy.gpx.GPXTrackPoint(lat, lon))
                coords.append((lat, lon))
    
    if len(coords) < 2:
        raise ValueError("Route generation failed, insufficient coordinates for GPX file.")

    # Écriture du fichier GPX
    gpx_file = f"trace_{uuid.uuid4()}.gpx"
    with open(gpx_file, "w") as f:
        f.write(gpx.to_xml())
    
    # Créer une carte interactive avec Folium
    map_file = create_map(coords, center_point)

    return gpx_file, map_file



def create_circular_route(graph, center_node, distance):
    radius = distance / 2  # Rayon approximatif en mètres
    bbox = ox.utils_geo.bbox_from_point(
        (graph.nodes[center_node]['y'], graph.nodes[center_node]['x']), dist=radius
    )

    # Troncature du graphe pour limiter aux alentours
    subgraph = ox.truncate.truncate_graph_bbox(graph, *bbox)
    if len(subgraph.nodes) == 0:
        raise ValueError("No nodes found within the specified radius")

    # Trouver un nœud cible à distance équivalente
    nodes_within_radius = list(subgraph.nodes)
    target_node = nodes_within_radius[len(nodes_within_radius) // 2]

    # Chemin aller-retour
    route_to_target = nx.shortest_path(graph, source=center_node, target=target_node, weight='length')
    route_back = nx.shortest_path(graph, source=target_node, target=center_node, weight='length')

    return route_to_target + route_back


def create_square_route(graph, center_node, distance):
    center_lat = graph.nodes[center_node]['y']
    center_lon = graph.nodes[center_node]['x']
    half_side = distance / 2

    # Coins du carré (approximation)
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

    # Retour au point de départ
    segment = nx.shortest_path(graph, source=current_node, target=center_node, weight='length')
    route.extend(segment)

    return route


def create_map(coords, center_point):
    m = folium.Map(location=center_point, zoom_start=14)
    folium.PolyLine(coords, color="blue", weight=2.5, opacity=1).add_to(m)
    map_file = f"map_{uuid.uuid4()}.html"
    m.save(map_file)
    return map_file


if __name__ == "__main__":
    app.run(debug=True)
