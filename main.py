#!/usr/bin/env python
"""
Emergency Route Planning System
CS 5800 - Algorithms Final Project
"""

import argparse
import random
from graph import Graph
from example_usage import create_sample_map, test_simple_scenario, test_multiple_emergencies
from realistic_map import create_campus_map, simulate_campus_emergency

def parse_args():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description='Emergency Route Planning System')
    parser.add_argument('--mode', type=str, choices=['simple', 'multiple', 'campus'], 
                        default='simple', help='Run mode: simple example, multiple emergencies, or campus simulation')
    parser.add_argument('--emergency', type=str, help='Emergency location (used only in simple mode)')
    return parser.parse_args()

def main():
    """
    Main function
    """
    args = parse_args()
    
    if args.mode == 'simple':
        print("Running simple example mode")
        if args.emergency:
            # Create a simple map
            g = create_sample_map()
            
            # Use the specified emergency location
            emergency_location = args.emergency
            
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
        else:
            # Use the default example
            test_simple_scenario()
    
    elif args.mode == 'multiple':
        print("Running multiple emergencies mode")
        test_multiple_emergencies()
    
    elif args.mode == 'campus':
        print("Running campus simulation mode")
        simulate_campus_emergency()

if __name__ == "__main__":
    main()