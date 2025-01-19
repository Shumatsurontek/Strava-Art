import folium
import uuid

def save_map(coords, start_point):
    """
    Sauvegarde une carte avec l'itinéraire tracé.

    Args:
        coords (list): Liste de tuples (lat, lon) des coordonnées de l'itinéraire.
        start_point (tuple): Point de départ de l'itinéraire.

    Returns:
        str: Nom du fichier HTML de la carte.
    """
    try:
        # Créer une carte centrée sur le point de départ
        m = folium.Map(location=start_point, zoom_start=14)

        # Ajouter une ligne représentant l'itinéraire
        folium.PolyLine(coords, color="blue", weight=2.5).add_to(m)

        # Sauvegarder la carte avec un nom de fichier unique
        map_file = f"route_map_{uuid.uuid4()}.html"
        m.save(map_file)
        return map_file
    except Exception as e:
        raise RuntimeError(f"Error saving map: {str(e)}")
