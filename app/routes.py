from flask import request, jsonify, Blueprint, render_template
from app.utils.graph_cache import get_graph
from app.utils.gpx_service import generate_gpx
from app.utils.map_utils import save_map
from app.utils.route_utils import get_center_node, create_circular_route, create_square_route
from dotenv import load_dotenv
import traceback

load_dotenv()

bp = Blueprint('routes', __name__)


def validate_input(data):
    """
    Valide les données de la requête.
    """
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
    """
    Point d'entrée pour la page d'accueil.
    """
    return render_template('index.html')


@bp.route('/generate-trace', methods=['POST'])
def generate_trace():
    """
    Génère un trace GPX et une carte en fonction des données saisies.
    """
    data = request.json
    print("Données reçues :", data)
    try:
        # Valider les données d'entrée
        validate_input(data)

        # Récupérer les informations de la requête
        city = data["city"]
        shape = data["shape"]
        distance = int(data["distance"])

        # Charger le graphe pour la ville donnée
        graph = get_graph(city)
        if not graph:
            print(f"Erreur : aucun graphe trouvé pour la ville : {city}")
            raise ValueError(f"No graph data available for city: {city}")

        print(f"Graph chargé pour {city}. Nombre de nœuds : {len(graph.nodes())}")

        # Récupérer le nœud central
        center_node, _ = get_center_node(graph, city)
        if center_node is None:
            print("Erreur : impossible de déterminer le nœud central.")
            raise ValueError("Could not determine the center node for the graph.")

        # Créer l'itinéraire en fonction de la forme
        if shape == "circle":
            route = create_circular_route(graph, center_node, distance)
        elif shape == "square":
            route = create_square_route(graph, center_node, distance)
        else:
            raise ValueError(f"Unsupported shape: {shape}")

        # Vérifier si la route a été générée
        if not route or len(route) == 0:
            print("Erreur : l'itinéraire généré est vide.")
            raise ValueError("The generated route is empty. Please check your input data.")

        # Extraire les coordonnées pour la carte
        coords = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in route]

        # Générer le fichier GPX et la carte
        gpx_file, gpx_path = generate_gpx(route, graph, city, shape)
        map_file = save_map(coords, coords[0])

        # Vérification des fichiers générés
        if not gpx_file or not map_file:
            print("Erreur : échec de la génération des fichiers GPX ou de la carte.")
            raise ValueError("Failed to generate GPX file or map.")

        print(f"Fichiers générés avec succès : {gpx_file}, {map_file}")

        return jsonify({
            "gpx_file": gpx_file,
            "map_file": map_file
        })

    except ValueError as ve:
        print(f"Erreur de validation : {ve}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print("Erreur inattendue :", traceback.format_exc())
        return jsonify({"error": str(e)}), 500
