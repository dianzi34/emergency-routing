import heapq
import matplotlib.pyplot as plt # type: ignore
import networkx as nx # type: ignore
import numpy as np # type: ignore

class Graph:
    """
    Weighted graph representing a geographical area
    """
    
    def __init__(self):
        """
        Initialize an empty graph
        """
        # Store graph using adjacency list
        # Format: {node_id: [(neighbor_id, distance), ...]}
        self.graph = {}
        # Store node positions for visualization
        self.node_positions = {}
        # Store hospital information
        # Format: {hospital_id: {"capacity": current_capacity, "max_capacity": max_capacity}}
        self.hospitals = {}
    
    def add_node(self, node_id, x, y, is_hospital=False, capacity=0):
        """
        Add a node to the graph
        
        Args:
            node_id: Unique identifier for the node
            x, y: Coordinates for the node position
            is_hospital: Boolean indicating if the node is a hospital
            capacity: If a hospital, its maximum capacity
        """
        if node_id not in self.graph:
            self.graph[node_id] = []
            self.node_positions[node_id] = (x, y)
            
            if is_hospital:
                self.hospitals[node_id] = {
                    "capacity": 0,  # Current used capacity
                    "max_capacity": capacity  # Maximum capacity
                }
    
    def add_edge(self, from_node, to_node, distance):
        """
        Add an edge to the graph
        
        Args:
            from_node: Starting node ID
            to_node: Target node ID
            distance: Distance between the two nodes
        """
        if from_node in self.graph and to_node in self.graph:
            # Ensure we don't add duplicate edges
            for i, (neighbor, _) in enumerate(self.graph[from_node]):
                if neighbor == to_node:
                    self.graph[from_node][i] = (to_node, distance)
                    break
            else:
                self.graph[from_node].append((to_node, distance))
            
            # For undirected graph, add the reverse edge
            for i, (neighbor, _) in enumerate(self.graph[to_node]):
                if neighbor == from_node:
                    self.graph[to_node][i] = (from_node, distance)
                    break
            else:
                self.graph[to_node].append((from_node, distance))
    
    def get_available_hospitals(self):
        """
        Return a list of hospitals with available capacity
        """
        available = []
        for hospital_id, info in self.hospitals.items():
            if info["capacity"] < info["max_capacity"]:
                available.append(hospital_id)
        return available
    
    def update_hospital_capacity(self, hospital_id, delta=1):
        """
        Update hospital capacity
        
        Args:
            hospital_id: Hospital ID
            delta: Capacity change value, default is 1 (add one patient)
        
        Returns:
            bool: Whether the operation was successful
        """
        if hospital_id in self.hospitals:
            new_capacity = self.hospitals[hospital_id]["capacity"] + delta
            if 0 <= new_capacity <= self.hospitals[hospital_id]["max_capacity"]:
                self.hospitals[hospital_id]["capacity"] = new_capacity
                return True
        return False
    
    def dijkstra(self, start_node):
        """
        Calculate the shortest path from the start node to all other nodes using Dijkstra's algorithm
        
        Args:
            start_node: Starting node ID
        
        Returns:
            tuple: (distances, predecessors)
                distances: Dictionary, {node_id: shortest distance from start node to this node}
                predecessors: Dictionary, {node_id: previous node in the shortest path}
        """
        if start_node not in self.graph:
            return {}, {}
        
        # Initialize distance and predecessor dictionaries
        distances = {node: float('infinity') for node in self.graph}
        predecessors = {node: None for node in self.graph}
        distances[start_node] = 0
        
        # Use priority queue (min heap) to select the closest unvisited node
        priority_queue = [(0, start_node)]
        
        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)
            
            # If we found a longer distance, skip
            if current_distance > distances[current_node]:
                continue
            
            # Check all neighbors
            for neighbor, weight in self.graph[current_node]:
                distance = current_distance + weight
                
                # If we found a shorter path, update the distance and add to queue
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    predecessors[neighbor] = current_node
                    heapq.heappush(priority_queue, (distance, neighbor))
        
        return distances, predecessors
    
    def find_nearest_available_hospital(self, start_node):
        """
        Find the path to the nearest available hospital from the starting node
        
        Args:
            start_node: Emergency location node ID
        
        Returns:
            tuple: (hospital_id, path, distance)
                hospital_id: ID of the nearest available hospital
                path: Path from the starting node to the hospital
                distance: Total distance of the path
        """
        # Get all available hospitals
        available_hospitals = self.get_available_hospitals()
        if not available_hospitals:
            return None, [], float('infinity')
        
        # Run Dijkstra's algorithm
        distances, predecessors = self.dijkstra(start_node)
        
        # Find the nearest available hospital
        nearest_hospital = None
        min_distance = float('infinity')
        
        for hospital in available_hospitals:
            if hospital in distances and distances[hospital] < min_distance:
                min_distance = distances[hospital]
                nearest_hospital = hospital
        
        if nearest_hospital is None:
            return None, [], float('infinity')
        
        # Reconstruct the path from the starting node to the hospital
        path = []
        current = nearest_hospital
        
        while current is not None:
            path.append(current)
            current = predecessors[current]
        
        # Reverse the path to start from the starting node
        path.reverse()
        
        return nearest_hospital, path, min_distance
    
    def visualize(self, path=None, emergency_node=None, hospital_node=None, figure=None, ax=None):
        """
        Visualize the graph and path
        
        Args:
            path: Path to highlight, list of node IDs
            emergency_node: Emergency location node ID
            hospital_node: Target hospital node ID
            figure: Matplotlib figure object (optional)
            ax: Matplotlib axes object (optional)
        """
        # Use provided figure and ax or create new ones
        if figure is None or ax is None:
            fig = plt.figure(figsize=(12, 10))
            ax = fig.add_subplot(111)
        else:
            fig = figure
            
        # Create NetworkX graph for visualization
        G = nx.Graph()
        
        # Add all nodes
        for node_id in self.graph:
            G.add_node(node_id, pos=self.node_positions[node_id])
        
        # Add all edges
        for node_id, neighbors in self.graph.items():
            for neighbor, weight in neighbors:
                if neighbor > node_id:  # Prevent adding duplicate edges
                    G.add_edge(node_id, neighbor, weight=weight)
        
        # Get node positions for plotting
        pos = nx.get_node_attributes(G, 'pos')
        
        # Draw all nodes
        node_colors = []
        for node in G.nodes():
            if node == emergency_node:
                node_colors.append('red')  # Emergency location is red
            elif node == hospital_node:
                node_colors.append('green')  # Target hospital is green
            elif node in self.hospitals:
                if self.hospitals[node]["capacity"] < self.hospitals[node]["max_capacity"]:
                    node_colors.append('lime')  # Hospital with capacity is light green
                else:
                    node_colors.append('orange')  # Full capacity hospital is orange
            else:
                node_colors.append('lightgray')  # Normal node is gray
        
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=500, ax=ax)
        
        # Draw all edges
        nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5, ax=ax)
        
        # If a path exists, highlight it
        if path and len(path) > 1:
            path_edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
            nx.draw_networkx_edges(G, pos, edgelist=path_edges, 
                                 width=3.0, edge_color='blue', ax=ax)
        
        # Show node labels
        nx.draw_networkx_labels(G, pos, font_size=10, ax=ax)
        
        # Show edge weights
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)
        
        # Add legend
        emergency = plt.Line2D([], [], color='red', marker='o', linestyle='None',
                              markersize=10, label='Emergency Location')
        target_hospital = plt.Line2D([], [], color='green', marker='o', linestyle='None',
                                    markersize=10, label='Target Hospital')
        available_hospital = plt.Line2D([], [], color='lime', marker='o', linestyle='None',
                                      markersize=10, label='Hospital with Capacity')
        full_hospital = plt.Line2D([], [], color='orange', marker='o', linestyle='None',
                                 markersize=10, label='Full Capacity Hospital')
        normal_node = plt.Line2D([], [], color='lightgray', marker='o', linestyle='None',
                               markersize=10, label='Normal Node')
        path_line = plt.Line2D([], [], color='blue', marker=None, linewidth=3,
                             label='Shortest Path')
        
        ax.legend(handles=[emergency, target_hospital, available_hospital, 
                           full_hospital, normal_node, path_line], loc='best')
        
        ax.set_title('Emergency Route Planning')
        ax.axis('off')
        fig.tight_layout()
        
        # Only show the plot if we created a new figure
        if figure is None:
            plt.show()
        
        return fig, ax
        
    def get_path_details(self, path):
        """
        Get detailed information about the path
        
        Args:
            path: Path, list of node IDs
            
        Returns:
            tuple: (total_distance, segment_details)
                total_distance: Total distance
                segment_details: List of path segment details, each containing start, end and distance
        """
        if not path or len(path) < 2:
            return 0, []
        
        total_distance = 0
        segment_details = []
        
        for i in range(len(path) - 1):
            from_node = path[i]
            to_node = path[i + 1]
            
            # Find the distance between these two nodes
            for neighbor, weight in self.graph[from_node]:
                if neighbor == to_node:
                    distance = weight
                    break
            
            total_distance += distance
            segment_details.append({
                'from': from_node,
                'to': to_node,
                'distance': distance
            })
        
        return total_distance, segment_details