import pytest
import osmnx
import networkx as nx
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
from unittest.mock import patch, MagicMock

# Import functions from locator.py
import sys
import os
sys.path.append(os.path.abspath("./app"))
from app.locator  import (
    get_nearby_hospitals,
    get_hospital_name,
    get_location_from_hospitals,
    get_nearest_hospital,
    get_graph,
    custom_dijkstra,
    find_shortest_path
)

# Test data
@pytest.fixture
def mock_hospital_data():
    """Create a mock GeoDataFrame representing hospital data."""
    data = {
        'geometry': [
            Point(-121.94, 37.31),
            Point(-121.93, 37.32),
            Polygon([(-121.95, 37.30), (-121.94, 37.30), (-121.94, 37.31), (-121.95, 37.31)])
        ],
        'name': ['Hospital A', 'Hospital B', 'Hospital C'],
        'amenity': ['hospital', 'hospital', 'hospital'],
        'emergency': ['yes', None, 'yes']
    }
    
    # Create a multi-index with 'element' and 'id' like OSMnx returns
    index = pd.MultiIndex.from_tuples([
        ('node', 12345),
        ('node', 67890),
        ('way', 11111)
    ], names=['element', 'id'])
    
    return gpd.GeoDataFrame(data, index=index, crs='EPSG:4326')

@pytest.fixture
def mock_graph():
    """Create a mock street graph."""
    G = nx.DiGraph()
    
    # Add nodes
    G.add_node(1, x=-121.94, y=37.31)
    G.add_node(2, x=-121.93, y=37.32)
    G.add_node(3, x=-121.92, y=37.33)
    G.add_node(4, x=-121.91, y=37.32)
    
    # Add edges with weights
    G.add_edge(1, 2, length=100, time=30)
    G.add_edge(2, 3, length=150, time=40)
    G.add_edge(3, 4, length=120, time=35)
    G.add_edge(1, 4, length=300, time=80)
    
    return G

# Test get_nearby_hospitals
@patch('osmnx.features_from_point')
def test_get_nearby_hospitals(mock_features, mock_hospital_data):
    # Configure the mock to return the test data
    mock_features.return_value = mock_hospital_data
    
    # Test with default parameters
    result = get_nearby_hospitals(37.31, -121.93, radius=1000)
    mock_features.assert_called_with((37.31, -121.93), tags={'amenity': 'hospital'}, dist=1000)
    assert result is not None
    assert len(result) == 3
    
    # Test with emergency=True
    result = get_nearby_hospitals(37.31, -121.93, radius=1000, emergency=True)
    mock_features.assert_called_with((37.31, -121.93), tags={'amenity': 'hospital', 'emergency': 'yes'}, dist=1000)
    
    # Test with emergency=False
    result = get_nearby_hospitals(37.31, -121.93, radius=1000, emergency=False)
    mock_features.assert_called_with((37.31, -121.93), tags={'amenity': 'hospital', 'emergency': 'no'}, dist=1000)
    
    # Test when no hospitals are found
    mock_features.side_effect = osmnx._errors.InsufficientResponseError()
    result = get_nearby_hospitals(37.31, -121.93, radius=1000)
    assert result is None

# Test get_hospital_name
def test_get_hospital_name(mock_hospital_data):
    # Test with hospital data that has names
    result = get_hospital_name(mock_hospital_data)
    assert isinstance(result, list)
    assert len(result) == 3
    assert 'Hospital A' in result
    assert 'Hospital B' in result
    assert 'Hospital C' in result
    
    # Test with no name column
    mock_data_no_names = mock_hospital_data.drop(columns=['name'])
    result = get_hospital_name(mock_data_no_names)
    assert result == "Unnamed Hospital"

# Test get_location_from_hospitals
def test_get_location_from_hospitals(mock_hospital_data):
    result = get_location_from_hospitals(mock_hospital_data)
    
    # Check that we get the right number of hospitals
    assert len(result) == 3
    
    # Check structure of each hospital point
    for hospital in result:
        assert 'name' in hospital
        assert 'geometry' in hospital
        assert isinstance(hospital['geometry'], Point)
    
    # Check that the first two are unchanged (already Points)
    assert result[0]['geometry'].x == mock_hospital_data.iloc[0].geometry.x
    assert result[0]['geometry'].y == mock_hospital_data.iloc[0].geometry.y
    
    # Check that the Polygon was converted to a Point (centroid)
    assert isinstance(result[2]['geometry'], Point)
    assert result[2]['name'] == 'Hospital C'

# Test get_nearest_hospital
def test_get_nearest_hospital():
    hospital_points = [
        {'name': 'Hospital A', 'geometry': Point(-121.94, 37.31)},
        {'name': 'Hospital B', 'geometry': Point(-121.93, 37.32)},
        {'name': 'Hospital C', 'geometry': Point(-121.945, 37.315)}
    ]
    
    # Test with a point closer to Hospital A
    origin = (37.311, -121.941)
    location, name = get_nearest_hospital(hospital_points, origin)
    assert name == 'Hospital A'
    assert location == (37.31, -121.94)
    
    # Test with a point closer to Hospital B
    origin = (37.321, -121.931)
    location, name = get_nearest_hospital(hospital_points, origin)
    assert name == 'Hospital B'
    assert location == (37.32, -121.93)
    
    # Test with empty hospital list
    location, name = get_nearest_hospital([], (37.31, -121.94))
    assert location is None
    assert name is None

# Test custom_dijkstra
def test_custom_dijkstra(mock_graph):
    # Test basic path finding
    path = custom_dijkstra(mock_graph, 1, 4, weight='length')
    assert path == [1, 4]  # Shortest path is direct 1->4
    
    # Test using a different weight
    path = custom_dijkstra(mock_graph, 1, 3, weight='time')
    assert path == [1, 2, 3]  # Path through intermediate node
    
    # Test unreachable target
    # Add a disconnected node
    mock_graph.add_node(5, x=-121.90, y=37.34)
    path = custom_dijkstra(mock_graph, 1, 5, weight='length')
    assert path is None

# Test find_shortest_path with mocked dependencies
@patch('osmnx.distance.nearest_nodes')
def test_find_shortest_path(mock_nearest_nodes, mock_graph):
    # Configure the mock
    mock_nearest_nodes.side_effect = lambda g, x, y: 1 if (x, y) == (-121.94, 37.31) else 4
    
    # Test with Length optimizer
    with patch('locator.custom_dijkstra', return_value=[1, 4]) as mock_dijkstra:
        route = find_shortest_path(
            mock_graph, 
            (37.31, -121.94),  # Origin
            (37.32, -121.91),  # Destination
            "Length"
        )
        
        # Verify the correct nodes were found and path calculated
        mock_nearest_nodes.assert_any_call(mock_graph, -121.94, 37.31)
        mock_nearest_nodes.assert_any_call(mock_graph, -121.91, 37.32)
        mock_dijkstra.assert_called_with(mock_graph, 1, 4)
        
        assert route == [1, 4]

# Test get_graph with mocked dependencies
@patch('locator.get_nearby_hospitals')
@patch('locator.get_location_from_hospitals')
@patch('locator.get_nearest_hospital')
@patch('osmnx.graph.graph_from_bbox')
def test_get_graph(
    mock_graph_from_bbox,
    mock_get_nearest_hospital, 
    mock_get_location_from_hospitals, 
    mock_get_nearby_hospitals,
    mock_hospital_data,
    mock_graph
):
    # Configure the mocks
    mock_get_nearby_hospitals.return_value = mock_hospital_data
    
    hospital_points = [
        {'name': 'Hospital A', 'geometry': Point(-121.94, 37.31)},
        {'name': 'Hospital B', 'geometry': Point(-121.93, 37.32)}
    ]
    mock_get_location_from_hospitals.return_value = hospital_points
    
    mock_get_nearest_hospital.return_value = ((37.31, -121.94), 'Hospital A')
    
    mock_graph_from_bbox.return_value = mock_graph
    
    # Test successful graph retrieval
    graph, loc_orig, loc_dest, hospitals, name = get_graph((37.31, -121.94), 10000)
    
    assert graph == mock_graph
    assert loc_orig == (37.31, -121.94)
    assert loc_dest == (37.31, -121.94)
    assert hospitals == hospital_points
    assert name == 'Hospital A'
    
    # Test when no hospitals are found
    mock_get_nearby_hospitals.return_value = None
    
    graph, loc_orig, loc_dest, hospitals, name = get_graph((37.31, -121.94), 10000)
    
    assert graph is None
    assert loc_orig == (37.31, -121.94)
    assert loc_dest is None
    assert hospitals == []
    assert name == "No hospital found"
    
    # Test with empty hospital dataframe
    empty_df = gpd.GeoDataFrame(columns=mock_hospital_data.columns)
    mock_get_nearby_hospitals.return_value = empty_df
    
    graph, loc_orig, loc_dest, hospitals, name = get_graph((37.31, -121.94), 10000)
    
    assert graph is None
    assert loc_orig == (37.31, -121.94)
    assert loc_dest is None
    assert hospitals == []
    assert name == "No hospital found"