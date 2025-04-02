from graph import Graph

def create_sample_map():
    """
    Create a sample map for testing
    """
    g = Graph()
    
    # Add nodes: (node_id, x coordinate, y coordinate, is hospital, capacity)
    # Normal landmarks and intersections
    g.add_node('A', 0, 0)
    g.add_node('B', 2, 0)
    g.add_node('C', 4, 0)
    g.add_node('D', 6, 0)
    g.add_node('E', 0, 2)
    g.add_node('F', 2, 2)
    g.add_node('G', 4, 2)
    g.add_node('H', 6, 2)
    g.add_node('I', 0, 4)
    g.add_node('J', 2, 4)
    g.add_node('K', 4, 4)
    g.add_node('L', 6, 4)
    
    # Hospital locations with different capacities
    g.add_node('H1', 1, 1, True, 2)  # Small hospital, capacity of 2
    g.add_node('H2', 5, 1, True, 3)  # Medium hospital, capacity of 3
    g.add_node('H3', 3, 3, True, 5)  # Large hospital, capacity of 5
    
    # Add roads (edges)
    # Horizontal roads
    g.add_edge('A', 'B', 2)
    g.add_edge('B', 'C', 2)
    g.add_edge('C', 'D', 2)
    g.add_edge('E', 'F', 2)
    g.add_edge('F', 'G', 2)
    g.add_edge('G', 'H', 2)
    g.add_edge('I', 'J', 2)
    g.add_edge('J', 'K', 2)
    g.add_edge('K', 'L', 2)
    
    # Vertical roads
    g.add_edge('A', 'E', 2)
    g.add_edge('E', 'I', 2)
    g.add_edge('B', 'F', 2)
    g.add_edge('F', 'J', 2)
    g.add_edge('C', 'G', 2)
    g.add_edge('G', 'K', 2)
    g.add_edge('D', 'H', 2)
    g.add_edge('H', 'L', 2)
    
    # Connect hospitals
    g.add_edge('A', 'H1', 1.4)  # √2 ≈ 1.4
    g.add_edge('B', 'H1', 1.4)
    g.add_edge('E', 'H1', 1.4)
    g.add_edge('F', 'H1', 1.4)
    
    g.add_edge('C', 'H2', 1.4)
    g.add_edge('D', 'H2', 1.4)
    g.add_edge('G', 'H2', 1.4)
    g.add_edge('H', 'H2', 1.4)
    
    g.add_edge('F', 'H3', 1.4)
    g.add_edge('G', 'H3', 1.4)
    g.add_edge('J', 'H3', 1.4)
    g.add_edge('K', 'H3', 1.4)
    
    return g

def test_simple_scenario():
    """
    Test a simple scenario: one emergency case
    """
    g = create_sample_map()
    
    # Assume an emergency at node I
    emergency_location = 'I'
    
    # Find the nearest hospital with capacity
    hospital, path, distance = g.find_nearest_available_hospital(emergency_location)
    
    print(f"Emergency at node {emergency_location}")
    
    if hospital:
        print(f"Nearest available hospital is {hospital}, distance: {distance}")
        print(f"Shortest path: {' -> '.join(path)}")
        
        # Get detailed path information
        total_distance, segments = g.get_path_details(path)
        print(f"\nPath details (total distance: {total_distance}):")
        for i, segment in enumerate(segments, 1):
            print(f"  Segment {i}: {segment['from']} -> {segment['to']} ({segment['distance']})")
        
        # Update hospital capacity
        g.update_hospital_capacity(hospital)
        print(f"\nUpdated capacity for hospital {hospital}: "
              f"{g.hospitals[hospital]['capacity']}/{g.hospitals[hospital]['max_capacity']}")
        
        # Visualize the path
        g.visualize(path, emergency_location, hospital)
    else:
        print("No available hospital found")
        g.visualize(emergency_node=emergency_location)

def test_multiple_emergencies():
    """
    Test a scenario with multiple emergencies
    """
    g = create_sample_map()
    
    # Define multiple emergency locations
    emergencies = ['I', 'L', 'A', 'D', 'K', 'E']
    
    print("Simulating multiple emergencies occurring in sequence:\n")
    
    for i, location in enumerate(emergencies, 1):
        print(f"Emergency {i}: Location {location}")
        
        # Find the nearest available hospital
        hospital, path, distance = g.find_nearest_available_hospital(location)
        
        if hospital:
            print(f"  Assigned to hospital {hospital}, distance: {distance}")
            print(f"  Path: {' -> '.join(path)}")
            
            # Update hospital capacity
            g.update_hospital_capacity(hospital)
            print(f"  Hospital {hospital} now at capacity: "
                  f"{g.hospitals[hospital]['capacity']}/{g.hospitals[hospital]['max_capacity']}")
            
            # Visualize
            g.visualize(path, location, hospital)
        else:
            print("  No available hospital found! All hospitals are at full capacity.")
            g.visualize(emergency_node=location)
        
        print("\nCurrent hospital status:")
        for h_id, info in g.hospitals.items():
            print(f"  {h_id}: {info['capacity']}/{info['max_capacity']}")
        
        print("-" * 50)

if __name__ == "__main__":
    print("Testing single emergency")
    print("=" * 50)
    test_simple_scenario()
    
    print("\n\nTesting multiple emergencies")
    print("=" * 50)
    test_multiple_emergencies()