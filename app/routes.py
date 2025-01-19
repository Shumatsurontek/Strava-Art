from app.utils.graph_cache import get_graph
from flask import request, jsonify, Blueprint, render_template
from app.utils.gpx_service import generate_gpx
from app.utils.map_utils import save_map
from app.utils.route_utils import get_center_node, create_circular_route, create_square_route
from dotenv import load_dotenv
import traceback

# Charger les variables d'environnement
load_dotenv()

bp = Blueprint('routes', __name__)

def validate_input(data):
    required_fields = ["city", "shape", "distance"]
    for field in required_fields:
        if field not in data or not data[field]:
            print(f"Erreur de validation : champ manquant ou vide : {field}")
            raise ValueError(f"Missing or empty field: {field}")
    if data["shape"] not in ["circle", "square"]:
        print(f"Erreur de validation : forme invalide : {data['shape']}")
        raise ValueError("Shape must be 'circle' or 'square'.")
    try:
        int(data["distance"])
    except ValueError:
        print(f"Erreur de validation : distance non entière : {data['distance']}")
        raise ValueError("Distance must be an integer.")


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/generate-trace', methods=['POST'])
def generate_trace():
    """
    Génère un trace GPX et une carte en fonction des données saisies.
    """
    data = request.json
    print("Données reçues :", data)  # Log des données reçues pour débogage
    try:
        # Validation des données d'entrée
        validate_input(data)

        city = data["city"]
        shape = data["shape"]
        distance = int(data["distance"])

        # Charger le graphe routier
        graph = get_graph(city)
        if not graph:
            raise ValueError(f"No graph data available for city: {city}")

        # Générer l'itinéraire basé sur la forme
        if shape == "circle":
            center_node, _ = get_center_node(graph, city)
            route = create_circular_route(graph, center_node, distance)
        elif shape == "square":
            center_node, _ = get_center_node(graph, city)
            route = create_square_route(graph, center_node, distance)
        else:
            raise ValueError(f"Unsupported shape: {shape}")

        # Convertir les nœuds en coordonnées géographiques
        coords = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in route]

        # Générer les fichiers GPX et la carte
        gpx_file, _ = generate_gpx(graph, route, city, shape)
        map_file = save_map(coords, coords[0])

        return jsonify({
            "gpx_file": gpx_file,
            "map_file": map_file
        })

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
