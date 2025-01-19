from flask import Blueprint, request, jsonify, render_template
from app.utils.gpx_generator import create_gpx
import traceback

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/generate-trace', methods=['POST'])
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
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
