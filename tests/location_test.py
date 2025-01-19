import osmnx as ox
city = "Paris"
graph = ox.graph_from_place(city, network_type="walk")
print(graph)
