import folium

def visualize_square(coords, center):
    m = folium.Map(location=[center.latitude, center.longitude], zoom_start=13)
    folium.PolyLine([(c.latitude, c.longitude) for c in coords], color="blue").add_to(m)
    return m

# Exemple d'utilisation :
square_coords = get_square_coordinates(center, 2)  # Distance en km
visualize_square(square_coords, center)
