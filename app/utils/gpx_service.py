import os
import uuid
import gpxpy.gpx
import folium
import dotenv
import networkx as nx

dotenv.load_dotenv()

# Définir les dossiers pour les fichiers GPX et les cartes
GPX_FOLDER = "gpx_files"
MAP_FOLDER = "map_files"

# Assurez-vous que les dossiers existent
os.makedirs(GPX_FOLDER, exist_ok=True)
os.makedirs(MAP_FOLDER, exist_ok=True)

def generate_gpx(route, graph, city=None, shape=None):
    """
    Génère un fichier GPX à partir d'une route et d'un graphe.

    Args:
        route (list): Liste des nœuds représentant la route.
        graph (networkx.Graph): Graphe contenant les coordonnées des nœuds.
        city (str, optional): Nom de la ville. Par défaut None.
        shape (str, optional): Forme de la route (par exemple, 'circle', 'square'). Par défaut None.

    Returns:
        tuple: Chemin du fichier GPX généré et liste des coordonnées.
    """
    if not isinstance(graph, nx.Graph) and not isinstance(graph, nx.DiGraph):
        raise TypeError("Le graphe fourni n'est pas un objet valide NetworkX.")

    gpx = gpxpy.gpx.GPX()

    # Ajouter des métadonnées si city et shape sont fournis
    if city and shape:
        gpx.name = f"{city.capitalize()} {shape.capitalize()} Route"
    else:
        gpx.name = "Generated Route"

    track = gpxpy.gpx.GPXTrack(name=gpx.name)
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

    # Générer un nom de fichier unique avec city et shape si disponibles
    if city and shape:
        gpx_file = os.path.join(GPX_FOLDER, f"trace_{city}_{shape}_{uuid.uuid4()}.gpx")
    else:
        gpx_file = os.path.join(GPX_FOLDER, f"trace_{uuid.uuid4()}.gpx")

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
    map_file = os.path.join(MAP_FOLDER, f"map_{uuid.uuid4()}.html")
    m.save(map_file)
    return map_file