import osmnx as ox

graph_cache = {}

def get_graph(city):
    """
    Charge un graphe routier pour une ville donnée.

    Cette fonction vérifie si le graphe de la ville spécifiée est déjà présent dans le cache.
    Si c'est le cas, le graphe en cache est retourné. Sinon, le graphe est téléchargé en utilisant
    la bibliothèque osmnx, projeté dans un système métrique, stocké dans le cache, puis retourné.

    Args:
        city (str): Le nom de la ville pour laquelle récupérer le graphe.

    Returns:
        networkx.MultiDiGraph: Le graphe de la ville spécifiée ou None en cas d'erreur.
    """
    if city in graph_cache:
        return graph_cache[city]
    else:
        try:
            graph = ox.graph_from_place(city, network_type="walk")
            graph = ox.project_graph(graph)  # Projeter dans un système métrique
            print(f"Graph for '{city}' successfully created with {len(graph.nodes)} nodes.")
            graph_cache[city] = graph
            return graph
        except Exception as e:
            print(f"Error loading graph for {city}: {e}")
            return None