import os
import uuid
import gpxpy.gpx
import folium

GPX_DIR = "generated_gpx"
MAP_DIR = "generated_maps"

os.makedirs(GPX_DIR, exist_ok=True)
os.makedirs(MAP_DIR, exist_ok=True)


def generate_gpx(route, graph):
    """
    Génère un fichier GPX à partir d'une route et d'un graphe.

    Args:
        route (list): Liste des nœuds représentant la route.
        graph (networkx.Graph): Graphe contenant les coordonnées des nœuds.

    Returns:
        tuple: Chemin du fichier GPX généré et liste des coordonnées.
    """
    gpx = gpxpy.gpx.GPX()
    track = gpxpy.gpx.GPXTrack(name="Generated Route")
    gpx.tracks.append(track)
    segment = gpxpy.gpx.GPXTrackSegment()
    track.segments.append(segment)

    coords = []
    for node in route:
        lat, lon = graph.nodes[node].get('y'), graph.nodes[node].get('x')
        if lat is not None and lon is not None:
            segment.points.append(gpxpy.gpx.GPXTrackPoint(lat, lon))
            coords.append((lat, lon))
        else:
            raise ValueError(f"Node {node} has invalid coordinates.")

    if len(coords) < 2:
        raise ValueError("Insufficient coordinates for GPX generation")

    gpx_file = os.path.join(GPX_DIR, f"trace_{uuid.uuid4()}.gpx")
    with open(gpx_file, "w") as f:
        f.write(gpx.to_xml())

    return gpx_file, coords


def generate_map(coords, center_point):
    """
    Génère une carte HTML avec une polyline.

    Args:
        coords (list of tuples): Liste des coordonnées (latitude, longitude).
        center_point (tuple): Point central (latitude, longitude) pour centrer la carte.

    Returns:
        str: Chemin du fichier HTML généré.
    """
    m = folium.Map(location=center_point, zoom_start=14)
    folium.PolyLine(coords, color="blue", weight=2.5, opacity=1).add_to(m)
    map_file = os.path.join(MAP_DIR, f"map_{uuid.uuid4()}.html")
    m.save(map_file)
    return map_file
