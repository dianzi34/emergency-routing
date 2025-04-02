from graph import Graph
import random
import matplotlib.pyplot as plt # type: ignore

def create_campus_map():
    """
    Create a campus map example, including buildings, roads, and nearby hospitals
    """
    g = Graph()
    
    # Main campus buildings and locations (nodes)
    campus_buildings = {
        # Format: 'ID': (x, y, building name)
        'MC': (10, 15, 'Main Building'),
        'LIB': (15, 15, 'Library'),
        'SCI': (20, 15, 'Science Building'),
        'ENG': (10, 10, 'Engineering Building'),
        'CMP': (15, 10, 'Computer Science Building'),
        'ART': (20, 10, 'Arts Building'),
        'GYM': (10, 5, 'Gymnasium'),
        'CAF': (15, 5, 'Cafeteria'),
        'DRM': (20, 5, 'Dormitory')
    }
    
    # Outer locations and intersections
    outer_locations = {
        # Format: 'ID': (x, y, location description)
        'N1': (5, 20, 'North Intersection 1'),
        'N2': (15, 20, 'North Intersection 2'),
        'N3': (25, 20, 'North Intersection 3'),
        'E1': (25, 15, 'East Intersection 1'),
        'E2': (25, 10, 'East Intersection 2'),
        'E3': (25, 5, 'East Intersection 3'),
        'S1': (5, 0, 'South Intersection 1'),
        'S2': (15, 0, 'South Intersection 2'),
        'S3': (25, 0, 'South Intersection 3'),
        'W1': (5, 15, 'West Intersection 1'),
        'W2': (5, 10, 'West Intersection 2'),
        'W3': (5, 5, 'West Intersection 3')
    }
    
    # Hospital locations and capacities
    hospitals = {
        # Format: 'ID': (x, y, hospital name, capacity)
        'H1': (3, 18, 'North Hospital', 10),
        'H2': (28, 18, 'Northeast Hospital', 15),
        'H3': (28, 3, 'Southeast Hospital', 8),
        'H4': (3, 3, 'Southwest Hospital', 12),
        'H5': (15, 25, 'Central Hospital', 20)
    }
    
    # Add all buildings as nodes
    for node_id, (x, y, _) in campus_buildings.items():
        g.add_node(node_id, x, y)
    
    # Add all outer locations as nodes
    for node_id, (x, y, _) in outer_locations.items():
        g.add_node(node_id, x, y)
    
    # Add all hospitals as nodes
    for node_id, (x, y, _, capacity) in hospitals.items():
        g.add_node(node_id, x, y, True, capacity)
    
    # Add campus internal roads (edges)
    campus_roads = [
        ('MC', 'LIB', 5),
        ('LIB', 'SCI', 5),
        ('MC', 'ENG', 5),
        ('LIB', 'CMP', 5),
        ('SCI', 'ART', 5),
        ('ENG', 'CMP', 5),
        ('CMP', 'ART', 5),
        ('ENG', 'GYM', 5),
        ('CMP', 'CAF', 5),
        ('ART', 'DRM', 5),
        ('GYM', 'CAF', 5),
        ('CAF', 'DRM', 5)
    ]
    
    # Add outer roads
    outer_roads = [
        # North side roads
        ('N1', 'N2', 10),
        ('N2', 'N3', 10),
        # East side roads
        ('N3', 'E1', 5),
        ('E1', 'E2', 5),
        ('E2', 'E3', 5),
        ('E3', 'S3', 5),
        # South side roads
        ('S1', 'S2', 10),
        ('S2', 'S3', 10),
        # West side roads
        ('N1', 'W1', 5),
        ('W1', 'W2', 5),
        ('W2', 'W3', 5),
        ('W3', 'S1', 5)
    ]
    
    # Connect campus to outer roads
    campus_to_outer = [
        ('MC', 'N2', 5),
        ('SCI', 'E1', 5),
        ('DRM', 'E3', 5),
        ('GYM', 'S1', 5),
        ('CAF', 'S2', 5),
        ('DRM', 'S3', 5),
        ('MC', 'W1', 5),
        ('ENG', 'W2', 5),
        ('GYM', 'W3', 5)
    ]
    
    # Connect hospitals to nearest intersections
    hospital_connections = [
        ('H1', 'N1', 3),
        ('H1', 'W1', 3),
        ('H2', 'N3', 3),
        ('H2', 'E1', 3),
        ('H3', 'E3', 3),
        ('H3', 'S3', 3),
        ('H4', 'S1', 3),
        ('H4', 'W3', 3),
        ('H5', 'N2', 5)
    ]
    
    # Add all roads to the graph
    for from_node, to_node, distance in campus_roads + outer_roads + campus_to_outer + hospital_connections:
        g.add_edge(from_node, to_node, distance)
    
    return g

def simulate_campus_emergency():
    """
    Simulate emergency situations on a campus map
    """
    # Create campus map
    g = create_campus_map()
    
    # Emergency locations on campus
    campus_buildings = ['MC', 'LIB', 'SCI', 'ENG', 'CMP', 'ART', 'GYM', 'CAF', 'DRM']
    
    print("Campus Emergency Response System Simulation")
    print("=" * 50)
    
    # Display map in initial state
    g.visualize()
    print("Initial state: All hospitals have capacity")
    for h_id, info in g.hospitals.items():
        print(f"  {h_id}: {info['capacity']}/{info['max_capacity']}")
    print("-" * 50)
    
    # Simulate multiple emergencies
    num_emergencies = 10
    for i in range(num_emergencies):
        # Randomly select an emergency location
        emergency_location = random.choice(campus_buildings)
        
        print(f"\nEmergency {i+1}: Occurring at {emergency_location}")
        
        # Find the nearest available hospital
        hospital, path, distance = g.find_nearest_available_hospital(emergency_location)
        
        if hospital:
            print(f"Assigned to hospital {hospital}, distance: {distance}")
            print(f"Path: {' -> '.join(path)}")
            
            # Get detailed path information
            total_distance, segments = g.get_path_details(path)
            print(f"\nPath details (total distance: {total_distance}):")
            for j, segment in enumerate(segments, 1):
                print(f"  Segment {j}: {segment['from']} -> {segment['to']} ({segment['distance']})")
            
            # Update hospital capacity
            g.update_hospital_capacity(hospital)
            print(f"\nUpdated capacity for hospital {hospital}: "
                 f"{g.hospitals[hospital]['capacity']}/{g.hospitals[hospital]['max_capacity']}")
            
            # Visualize the path
            g.visualize(path, emergency_location, hospital)
        else:
            print("No available hospital found! All hospitals are at full capacity.")
            g.visualize(emergency_node=emergency_location)
        
        print("\nCurrent hospital status:")
        for h_id, info in g.hospitals.items():
            print(f"  {h_id}: {info['capacity']}/{info['max_capacity']}")
        
        print("-" * 50)
        
        # End simulation if all hospitals are full
        if not g.get_available_hospitals():
            print("All hospitals are at full capacity. Ending simulation.")
            break
    
    print("\nSimulation complete")

if __name__ == "__main__":
    simulate_campus_emergency()