import uuid
import gpxpy.gpx
import folium


def generate_gpx(route, graph):
    gpx = gpxpy.gpx.GPX()
    track = gpxpy.gpx.GPXTrack(name="Generated Route")
    gpx.tracks.append(track)
    segment = gpxpy.gpx.GPXTrackSegment()
    track.segments.append(segment)

    coords = []
    for node in route:
        if 'y' in graph.nodes[node] and 'x' in graph.nodes[node]:
            lat, lon = graph.nodes[node]['y'], graph.nodes[node]['x']
            if lat is not None and lon is not None:
                segment.points.append(gpxpy.gpx.GPXTrackPoint(lat, lon))
                coords.append((lat, lon))

    if len(coords) < 2:
        raise ValueError("Insufficient coordinates for GPX generation")

    gpx_file = f"trace_{uuid.uuid4()}.gpx"
    with open(gpx_file, "w") as f:
        f.write(gpx.to_xml())

    return gpx_file, coords


def generate_map(coords, center_point):
    m = folium.Map(location=center_point, zoom_start=14)
    folium.PolyLine(coords, color="blue", weight=2.5, opacity=1).add_to(m)
    map_file = f"map_{uuid.uuid4()}.html"
    m.save(map_file)
    return map_file
