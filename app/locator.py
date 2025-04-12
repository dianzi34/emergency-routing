import osmnx
import networkx as nx

from typing import Tuple, List
from networkx.classes.multidigraph import MultiDiGraph


# get all hospitals in the area with bounding box
def get_nearby_hospitals(lat, lon, radius=1000, emergency=None):
    """
    Retrieves a list of hospital names within a specified radius of the given coordinates.

    Parameters:
    - lat (float): Latitude of the location.
    - lon (float): Longitude of the location.
    - radius (int): Search radius in meters (default is 1000).

    Returns:
    - List of hospital names.
    """
    # Define the tags for hospitals
    tags = {'amenity': 'hospital'}
    if emergency is True:
        tags['emergency'] = 'yes'
    elif emergency is False:
        tags['emergency'] = 'no'

    # Retrieve hospital geometries within the specified radius
    hospitals = osmnx.features_from_point((lat, lon), tags=tags, dist=radius)

    # Extract hospital names
    # hospital_names = hospitals['name'].dropna().unique().tolist()

    return hospitals

# get the name of the hospital
def get_hospital_name(hospitals):
    """
    Get the name of the hospital from the OSM data
    Args:
        hospital: OSM data
    Returns:
        name: name of the hospital
    Example:
        name = get_hospital_name(hospital)
    """
    # check if the hospital has a name
    if 'name' in hospitals:
        return hospitals['name'].dropna().unique().tolist()
    else:
        return "Unnamed Hospital"




# check whether the hospital is open or not, filter out the closed ones


# get the location of each hospital
def get_location_from_hospitals(hospitals) -> Tuple[float, float]:
    """ 
    Get (lat, long) coordintates from address
    Args:
        address: string with address
    Returns:
        location: (lat, long) coordinates
    Example:
        location_orig = get_location_from_address("Gare du Midi, Bruxelles")
    """
    import numpy as np
    hospital_points = []
    for idx, row in hospitals.iterrows():
        geom = row.geometry
        if row.get('name') is np.nan:
            continue
        if geom.geom_type == 'Point':
            point = geom
        else:
            # For Polygon or MultiPolygon, compute the centroid
            point = geom.centroid
        hospital_points.append({'name': row.get('name', 'Unnamed'), 'geometry': point})

    return hospital_points

# find the cloest route to hospital

def get_nearest_hospital(hospital_points, origin):
    min_distance = 0

    for hospital in hospital_points:
        x1, y1 = hospital['geometry'].y, hospital['geometry'].x
        x2, y2 = origin
        distance = osmnx.distance.euclidean(x1, y1, x2, y2)
        if min_distance == 0 or distance < min_distance:
            min_distance = distance
            closest_hospital = hospital

    print(f"Closest hospital: {closest_hospital['name']}")


    return (closest_hospital['geometry'].y, closest_hospital['geometry'].x), closest_hospital['name']



def get_graph(geo_orig, radius):
    """ 
    Convert the origin and destination addresses into (lat, long) coordinates and find the 
    graph of streets from the bounding box.
    Args:
        address_orig: departure address
        address_dest: arrival address
    Returns:
        graph: street graph from OpenStreetMap
        location_orig: departure coordinates
        location_dest: arrival coordinates
    Example:
        graph, location_orig, location_dest = get_graph("Gare du Midi, Bruxelles", "Gare du Nord, Bruxelles")
    """

    MARGIN = 0.1

    # find location by address
    # location_orig = get_location_from_address(address_orig)
    # location_dest = get_location_from_address(address_dest)

    location_orig = geo_orig
    hospitals = get_nearby_hospitals(location_orig[0], location_orig[1], radius=radius)
    hospital_points = get_location_from_hospitals(hospitals)
    hospitals_coordinates = [hospital['geometry'] for hospital in hospital_points]
    location_dest, hospital_name = get_nearest_hospital(hospital_points, location_orig)

    print(f'Location orig: {location_orig}')
    print(f'Location dest: {location_dest}')

    north = max(location_orig[0],location_dest[0]) + MARGIN
    south = min(location_orig[0],location_dest[0]) - MARGIN
    west = max(location_orig[1],location_dest[1]) + MARGIN
    east = min(location_orig[1],location_dest[1]) - MARGIN

    print(f'North: {north}, South: {south}')
    print(f'West: {west}, East: {east}')

    graph = osmnx.graph.graph_from_bbox((west, south, east, north), network_type='drive')

    print("Graph created!")
    print(graph)
    return graph, location_orig, location_dest, hospitals_coordinates, hospital_name

import heapq

def custom_dijkstra(graph, source, target, weight='length'):
    """
    Compute the shortest path between source and target nodes in a graph using Dijkstra's algorithm.

    Parameters:
    - graph: A NetworkX graph.
    - source: The starting node.
    - target: The destination node.
    - weight: The edge attribute to use as weight (default is 'length').

    Returns:
    - path: A list of nodes representing the shortest path from source to target.
    """
    # Initialize the priority queue with the source node
    queue = [(0, source, [])]
    # Set to keep track of visited nodes
    visited = set()

    while queue:
        # Pop the node with the smallest distance
        (cost, current_node, path) = heapq.heappop(queue)

        # Skip if the node has already been visited
        if current_node in visited:
            continue

        # Add the current node to the path
        path = path + [current_node]

        # If the target is reached, return the path
        if current_node == target:
            return path

        # Mark the current node as visited
        visited.add(current_node)

        # Iterate over neighbors of the current node
        for neighbor, edge_attrs in graph[current_node].items():
            if neighbor not in visited:
                # Retrieve the weight of the edge
                edge_weight = edge_attrs.get(weight, 1)
                # Add the neighbor to the queue with the updated cost
                heapq.heappush(queue, (cost + edge_weight, neighbor, path))

    # If the target is not reachable, return None
    return None




def find_shortest_path(graph: MultiDiGraph, location_orig: Tuple[float], location_dest: Tuple[float], optimizer: str) -> List[int]:
    """
    Find the shortest path between two points from the street graph
    Args:
        graph: street graph from OpenStreetMap
        location_orig: departure coordinates
        location_dest: arrival coordinates
        optimizer: type of optimizer (Length or Time)
    Returns:
        route:
    """

    # find the nearest node to the departure and arrival location
    Y1, X1 = location_orig
    Y2, X2 = location_dest
    node_orig = osmnx.distance.nearest_nodes(graph, X1, Y1)
    node_dest = osmnx.distance.nearest_nodes(graph, X2, Y2)

    print("Nearest Orig Node Found!")
    print("Nearest Dest Node Found!")

    # route = nx.shortest_path(graph, node_orig, node_dest, weight=optimizer.lower())
    route = custom_dijkstra(graph, node_orig, node_dest)
    print("Shortest path found!")
    print(route)
    return route