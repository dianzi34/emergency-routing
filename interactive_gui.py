#!/usr/bin/env python
"""
Interactive GUI for Emergency Route Planning System
Extends the project with a dynamic user interface
"""

import os
# Set Qt platform explicitly for macOS
os.environ['QT_QPA_PLATFORM'] = 'cocoa'  # For macOS

import sys
import matplotlib
matplotlib.use('Qt5Agg')  # Use Qt backend for better integration
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QComboBox, QLabel, 
                             QSlider, QGroupBox, QGridLayout, QSpinBox, 
                             QTabWidget, QTextEdit, QSplitter)
from PyQt5.QtCore import Qt

# Import project modules
from graph import Graph
from example_usage import create_sample_map
from realistic_map import create_campus_map

class EmergencyRoutingGUI(QMainWindow):
    """Main window for the interactive emergency routing application"""
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Interactive Emergency Route Planning System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create the main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create tabs for different map types
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Create tabs for different maps
        self.simple_map_tab = QWidget()
        self.campus_map_tab = QWidget()
        self.tab_widget.addTab(self.simple_map_tab, "Simple Grid Map")
        self.tab_widget.addTab(self.campus_map_tab, "Campus Map")
        
        print("Setting up simple map tab...")
        # Set up the simple map tab
        self.setup_simple_map_tab()
        
        print("Setting up campus map tab...")
        # Set up the campus map tab
        self.setup_campus_map_tab()
        
        # Connect tab change signal
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # Initialize the current map
        self.current_map = 'simple'
        self.on_tab_changed(0)  # Trigger initial setup for the first tab
        print("GUI initialization complete")
    
    def setup_simple_map_tab(self):
        """Set up the simple grid map tab"""
        layout = QHBoxLayout(self.simple_map_tab)
        
        # Create left panel for controls
        left_panel = QGroupBox("Controls")
        left_panel_layout = QVBoxLayout(left_panel)
        
        # Create figure for matplotlib
        self.simple_figure = Figure(figsize=(8, 6), dpi=100)
        self.simple_canvas = FigureCanvas(self.simple_figure)
        
        # Add emergency location selection
        location_group = QGroupBox("Emergency Location")
        location_layout = QVBoxLayout(location_group)
        self.simple_location_combo = QComboBox()
        self.simple_location_combo.addItems(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L'])
        self.simple_location_combo.setCurrentText('I')  # Default as in example
        location_layout.addWidget(self.simple_location_combo)
        left_panel_layout.addWidget(location_group)
        
        # Add hospital capacity controls
        hospital_group = QGroupBox("Hospital Capacity")
        hospital_layout = QGridLayout(hospital_group)
        
        # Hospital H1
        hospital_layout.addWidget(QLabel("H1:"), 0, 0)
        self.h1_capacity = QSpinBox()
        self.h1_capacity.setMinimum(0)
        self.h1_capacity.setMaximum(10)
        self.h1_capacity.setValue(2)
        hospital_layout.addWidget(self.h1_capacity, 0, 1)
        self.h1_current = QSpinBox()
        self.h1_current.setMinimum(0)
        self.h1_current.setMaximum(10)
        self.h1_current.setValue(0)
        hospital_layout.addWidget(self.h1_current, 0, 2)
        
        # Hospital H2
        hospital_layout.addWidget(QLabel("H2:"), 1, 0)
        self.h2_capacity = QSpinBox()
        self.h2_capacity.setMinimum(0)
        self.h2_capacity.setMaximum(10) 
        self.h2_capacity.setValue(3)
        hospital_layout.addWidget(self.h2_capacity, 1, 1)
        self.h2_current = QSpinBox()
        self.h2_current.setMinimum(0)
        self.h2_current.setMaximum(10)
        self.h2_current.setValue(0)
        hospital_layout.addWidget(self.h2_current, 1, 2)
        
        # Hospital H3
        hospital_layout.addWidget(QLabel("H3:"), 2, 0)
        self.h3_capacity = QSpinBox()
        self.h3_capacity.setMinimum(0)
        self.h3_capacity.setMaximum(10)
        self.h3_capacity.setValue(5)
        hospital_layout.addWidget(self.h3_capacity, 2, 1)
        self.h3_current = QSpinBox()
        self.h3_current.setMinimum(0)
        self.h3_current.setMaximum(10)
        self.h3_current.setValue(0)
        hospital_layout.addWidget(self.h3_current, 2, 2)
        
        left_panel_layout.addWidget(hospital_group)
        
        # Add run button
        self.simple_run_btn = QPushButton("Find Shortest Path")
        self.simple_run_btn.clicked.connect(self.run_simple_map)
        left_panel_layout.addWidget(self.simple_run_btn)
        
        # Add simulation button
        self.simple_simulate_btn = QPushButton("Run Simulation")
        self.simple_simulate_btn.clicked.connect(self.run_simple_simulation)
        left_panel_layout.addWidget(self.simple_simulate_btn)
        
        # Add reset button
        self.simple_reset_btn = QPushButton("Reset")
        self.simple_reset_btn.clicked.connect(self.reset_simple_map)
        left_panel_layout.addWidget(self.simple_reset_btn)
        
        # Add results text box
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout(results_group)
        self.simple_results = QTextEdit()
        self.simple_results.setReadOnly(True)
        results_layout.addWidget(self.simple_results)
        left_panel_layout.addWidget(results_group)
        
        # Add visualization panel
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.addWidget(self.simple_canvas)
        self.simple_toolbar = NavigationToolbar(self.simple_canvas, self)
        right_layout.addWidget(self.simple_toolbar)
        
        # Create a splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 900])  # Initial sizes
        
        layout.addWidget(splitter)
        
        # Initialize the graph
        self.simple_graph = create_sample_map()
        
        # Plot the initial state
        self.plot_simple_map()
    
    def setup_campus_map_tab(self):
        """Set up the campus map tab"""
        layout = QHBoxLayout(self.campus_map_tab)
        
        # Create left panel for controls
        left_panel = QGroupBox("Controls")
        left_panel_layout = QVBoxLayout(left_panel)
        
        # Create figure for matplotlib
        self.campus_figure = Figure(figsize=(8, 6), dpi=100)
        self.campus_canvas = FigureCanvas(self.campus_figure)
        
        # Add emergency location selection
        location_group = QGroupBox("Emergency Location")
        location_layout = QVBoxLayout(location_group)
        self.campus_location_combo = QComboBox()
        self.campus_location_combo.addItems(['MC', 'LIB', 'SCI', 'ENG', 'CMP', 'ART', 'GYM', 'CAF', 'DRM'])
        location_layout.addWidget(self.campus_location_combo)
        left_panel_layout.addWidget(location_group)
        
        # Add hospital capacity controls
        hospital_group = QGroupBox("Hospital Status")
        hospital_layout = QGridLayout(hospital_group)
        
        # Labels
        hospital_layout.addWidget(QLabel("Hospital"), 0, 0)
        hospital_layout.addWidget(QLabel("Max"), 0, 1)
        hospital_layout.addWidget(QLabel("Current"), 0, 2)
        
        # Hospital H1
        hospital_layout.addWidget(QLabel("H1:"), 1, 0)
        self.ch1_capacity = QLabel("10")
        hospital_layout.addWidget(self.ch1_capacity, 1, 1)
        self.ch1_current = QSpinBox()
        self.ch1_current.setMinimum(0)
        self.ch1_current.setMaximum(10)
        self.ch1_current.setValue(0)
        hospital_layout.addWidget(self.ch1_current, 1, 2)
        
        # Hospital H2
        hospital_layout.addWidget(QLabel("H2:"), 2, 0)
        self.ch2_capacity = QLabel("15")
        hospital_layout.addWidget(self.ch2_capacity, 2, 1)
        self.ch2_current = QSpinBox()
        self.ch2_current.setMinimum(0)
        self.ch2_current.setMaximum(15)
        self.ch2_current.setValue(0)
        hospital_layout.addWidget(self.ch2_current, 2, 2)
        
        # Hospital H3
        hospital_layout.addWidget(QLabel("H3:"), 3, 0)
        self.ch3_capacity = QLabel("8")
        hospital_layout.addWidget(self.ch3_capacity, 3, 1)
        self.ch3_current = QSpinBox()
        self.ch3_current.setMinimum(0)
        self.ch3_current.setMaximum(8)
        self.ch3_current.setValue(0)
        hospital_layout.addWidget(self.ch3_current, 3, 2)
        
        # Hospital H4
        hospital_layout.addWidget(QLabel("H4:"), 4, 0)
        self.ch4_capacity = QLabel("12")
        hospital_layout.addWidget(self.ch4_capacity, 4, 1)
        self.ch4_current = QSpinBox()
        self.ch4_current.setMinimum(0)
        self.ch4_current.setMaximum(12)
        self.ch4_current.setValue(0)
        hospital_layout.addWidget(self.ch4_current, 4, 2)
        
        # Hospital H5
        hospital_layout.addWidget(QLabel("H5:"), 5, 0)
        self.ch5_capacity = QLabel("20")
        hospital_layout.addWidget(self.ch5_capacity, 5, 1)
        self.ch5_current = QSpinBox()
        self.ch5_current.setMinimum(0)
        self.ch5_current.setMaximum(20)
        self.ch5_current.setValue(0)
        hospital_layout.addWidget(self.ch5_current, 5, 2)
        
        left_panel_layout.addWidget(hospital_group)
        
        # Add run button
        self.campus_run_btn = QPushButton("Find Shortest Path")
        self.campus_run_btn.clicked.connect(self.run_campus_map)
        left_panel_layout.addWidget(self.campus_run_btn)
        
        # Add simulation button
        self.campus_simulate_btn = QPushButton("Run Simulation")
        self.campus_simulate_btn.clicked.connect(self.run_campus_simulation)
        left_panel_layout.addWidget(self.campus_simulate_btn)
        
        # Add reset button
        self.campus_reset_btn = QPushButton("Reset")
        self.campus_reset_btn.clicked.connect(self.reset_campus_map)
        left_panel_layout.addWidget(self.campus_reset_btn)
        
        # Add results text box
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout(results_group)
        self.campus_results = QTextEdit()
        self.campus_results.setReadOnly(True)
        results_layout.addWidget(self.campus_results)
        left_panel_layout.addWidget(results_group)
        
        # Add visualization panel
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.addWidget(self.campus_canvas)
        self.campus_toolbar = NavigationToolbar(self.campus_canvas, self)
        right_layout.addWidget(self.campus_toolbar)
        
        # Create a splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 900])  # Initial sizes
        
        layout.addWidget(splitter)
        
        # Initialize the graph
        self.campus_graph = create_campus_map()
        
        # Plot the initial state
        self.plot_campus_map()
    
    def on_tab_changed(self, index):
        """Handle tab changes"""
        if index == 0:
            self.current_map = 'simple'
        else:
            self.current_map = 'campus'
    
    def plot_simple_map(self):
        """Plot the simple grid map"""
        self.simple_figure.clear()
        ax = self.simple_figure.add_subplot(111)
        
        # Draw the graph
        self.simple_graph.visualize(figure=self.simple_figure, ax=ax)
        
        self.simple_canvas.draw()
    
    def plot_campus_map(self):
        """Plot the campus map"""
        self.campus_figure.clear()
        ax = self.campus_figure.add_subplot(111)
        
        # Draw the graph
        self.campus_graph.visualize(figure=self.campus_figure, ax=ax)
        
        self.campus_canvas.draw()
    
    def run_simple_map(self):
        """Run the algorithm on the simple map with current settings"""
        # Update hospital capacities
        self.simple_graph.hospitals['H1']['max_capacity'] = self.h1_capacity.value()
        self.simple_graph.hospitals['H2']['max_capacity'] = self.h2_capacity.value()
        self.simple_graph.hospitals['H3']['max_capacity'] = self.h3_capacity.value()
        
        self.simple_graph.hospitals['H1']['capacity'] = self.h1_current.value()
        self.simple_graph.hospitals['H2']['capacity'] = self.h2_current.value()
        self.simple_graph.hospitals['H3']['capacity'] = self.h3_current.value()
        
        # Get the emergency location
        emergency_location = self.simple_location_combo.currentText()
        
        # Find the nearest available hospital
        hospital, path, distance = self.simple_graph.find_nearest_available_hospital(emergency_location)
        
        # Clear previous results
        self.simple_results.clear()
        
        if hospital:
            # Get path details
            total_distance, segments = self.simple_graph.get_path_details(path)
            
            # Update results
            result_text = f"Emergency at location: {emergency_location}\n"
            result_text += f"Nearest available hospital: {hospital}\n"
            result_text += f"Total distance: {total_distance}\n\n"
            result_text += f"Path: {' -> '.join(path)}\n\n"
            result_text += "Path details:\n"
            
            for i, segment in enumerate(segments, 1):
                result_text += f"  Segment {i}: {segment['from']} -> {segment['to']} ({segment['distance']})\n"
            
            self.simple_results.setText(result_text)
            
            # Update hospital capacity (simulate adding a patient)
            self.simple_graph.update_hospital_capacity(hospital)
            
            # Update capacity display
            if hospital == 'H1':
                self.h1_current.setValue(self.simple_graph.hospitals['H1']['capacity'])
            elif hospital == 'H2':
                self.h2_current.setValue(self.simple_graph.hospitals['H2']['capacity'])
            elif hospital == 'H3':
                self.h3_current.setValue(self.simple_graph.hospitals['H3']['capacity'])
            
            # Update visualization
            self.simple_figure.clear()
            ax = self.simple_figure.add_subplot(111)
            self.simple_graph.visualize(path=path, emergency_node=emergency_location, 
                                        hospital_node=hospital, figure=self.simple_figure, ax=ax)
            self.simple_canvas.draw()
        else:
            self.simple_results.setText(f"No available hospital found for emergency at {emergency_location}!")
            
            # Update visualization
            self.simple_figure.clear()
            ax = self.simple_figure.add_subplot(111)
            self.simple_graph.visualize(emergency_node=emergency_location, 
                                        figure=self.simple_figure, ax=ax)
            self.simple_canvas.draw()
    
    def run_simple_simulation(self):
        """Run a simulation with multiple emergencies on the simple map"""
        # Reset capacities to their maximums to start fresh
        self.h1_current.setValue(0)
        self.h2_current.setValue(0)
        self.h3_current.setValue(0)
        
        self.simple_graph.hospitals['H1']['capacity'] = 0
        self.simple_graph.hospitals['H2']['capacity'] = 0
        self.simple_graph.hospitals['H3']['capacity'] = 0
        
        # Define a sequence of emergency locations
        emergencies = ['I', 'L', 'A', 'D', 'K', 'E']
        
        # Clear previous results
        self.simple_results.clear()
        result_text = "Simulation Results:\n" + "="*50 + "\n\n"
        
        # Run each emergency
        for i, location in enumerate(emergencies, 1):
            result_text += f"Emergency {i}: Location {location}\n"
            
            # Find the nearest available hospital
            hospital, path, distance = self.simple_graph.find_nearest_available_hospital(location)
            
            if hospital:
                # Update hospital capacity
                self.simple_graph.update_hospital_capacity(hospital)
                
                # Update capacity display
                if hospital == 'H1':
                    self.h1_current.setValue(self.simple_graph.hospitals['H1']['capacity'])
                elif hospital == 'H2':
                    self.h2_current.setValue(self.simple_graph.hospitals['H2']['capacity'])
                elif hospital == 'H3':
                    self.h3_current.setValue(self.simple_graph.hospitals['H3']['capacity'])
                
                result_text += f"  Assigned to hospital {hospital}, distance: {distance}\n"
                result_text += f"  Path: {' -> '.join(path)}\n"
                result_text += f"  Hospital {hospital} now at capacity: {self.simple_graph.hospitals[hospital]['capacity']}/{self.simple_graph.hospitals[hospital]['max_capacity']}\n"
            else:
                result_text += "  No available hospital found! All hospitals are at full capacity.\n"
            
            result_text += "\nHospital status after emergency:\n"
            for h_id, info in self.simple_graph.hospitals.items():
                result_text += f"  {h_id}: {info['capacity']}/{info['max_capacity']}\n"
            
            result_text += "-"*50 + "\n"
            
            # Check if all hospitals are full
            if not self.simple_graph.get_available_hospitals():
                result_text += "\nAll hospitals are at full capacity. Ending simulation.\n"
                break
        
        # Display final results
        self.simple_results.setText(result_text)
        
        # Update visualization (last emergency)
        if hospital:
            self.simple_figure.clear()
            ax = self.simple_figure.add_subplot(111)
            self.simple_graph.visualize(path=path, emergency_node=location, 
                                      hospital_node=hospital, figure=self.simple_figure, ax=ax)
        else:
            self.simple_figure.clear()
            ax = self.simple_figure.add_subplot(111)
            self.simple_graph.visualize(emergency_node=location, 
                                      figure=self.simple_figure, ax=ax)
        
        self.simple_canvas.draw()
    
    def reset_simple_map(self):
        """Reset the simple map to its initial state"""
        # Reset the graph
        self.simple_graph = create_sample_map()
        
        # Reset hospital capacity controls
        self.h1_capacity.setValue(2)
        self.h2_capacity.setValue(3)
        self.h3_capacity.setValue(5)
        
        self.h1_current.setValue(0)
        self.h2_current.setValue(0)
        self.h3_current.setValue(0)
        
        # Reset emergency location
        self.simple_location_combo.setCurrentText('I')
        
        # Clear results
        self.simple_results.clear()
        
        # Update visualization
        self.plot_simple_map()
    
    def run_campus_map(self):
        """Run the algorithm on the campus map with current settings"""
        # Update hospital capacities
        self.campus_graph.hospitals['H1']['capacity'] = self.ch1_current.value()
        self.campus_graph.hospitals['H2']['capacity'] = self.ch2_current.value()
        self.campus_graph.hospitals['H3']['capacity'] = self.ch3_current.value()
        self.campus_graph.hospitals['H4']['capacity'] = self.ch4_current.value() 
        self.campus_graph.hospitals['H5']['capacity'] = self.ch5_current.value()
        
        # Get the emergency location
        emergency_location = self.campus_location_combo.currentText()
        
        # Find the nearest available hospital
        hospital, path, distance = self.campus_graph.find_nearest_available_hospital(emergency_location)
        
        # Clear previous results
        self.campus_results.clear()
        
        if hospital:
            # Get path details
            total_distance, segments = self.campus_graph.get_path_details(path)
            
            # Update results
            result_text = f"Emergency at location: {emergency_location}\n"
            result_text += f"Nearest available hospital: {hospital}\n"
            result_text += f"Total distance: {total_distance}\n\n"
            result_text += f"Path: {' -> '.join(path)}\n\n"
            result_text += "Path details:\n"
            
            for i, segment in enumerate(segments, 1):
                result_text += f"  Segment {i}: {segment['from']} -> {segment['to']} ({segment['distance']})\n"
            
            self.campus_results.setText(result_text)
            
            # Update hospital capacity (simulate adding a patient)
            self.campus_graph.update_hospital_capacity(hospital)
            
            # Update capacity display
            if hospital == 'H1':
                self.ch1_current.setValue(self.campus_graph.hospitals['H1']['capacity'])
            elif hospital == 'H2':
                self.ch2_current.setValue(self.campus_graph.hospitals['H2']['capacity'])
            elif hospital == 'H3':
                self.ch3_current.setValue(self.campus_graph.hospitals['H3']['capacity'])
            elif hospital == 'H4':
                self.ch4_current.setValue(self.campus_graph.hospitals['H4']['capacity'])
            elif hospital == 'H5':
                self.ch5_current.setValue(self.campus_graph.hospitals['H5']['capacity'])
            
            # Update visualization
            self.campus_figure.clear()
            ax = self.campus_figure.add_subplot(111)
            self.campus_graph.visualize(path=path, emergency_node=emergency_location, 
                                      hospital_node=hospital, figure=self.campus_figure, ax=ax)
            self.campus_canvas.draw()
        else:
            self.campus_results.setText(f"No available hospital found for emergency at {emergency_location}!")
            
            # Update visualization
            self.campus_figure.clear()
            ax = self.campus_figure.add_subplot(111)
            self.campus_graph.visualize(emergency_node=emergency_location, 
                                      figure=self.campus_figure, ax=ax)
            self.campus_canvas.draw()
    
    def run_campus_simulation(self):
        """Run a simulation with multiple emergencies on the campus map"""
        # Reset capacities to start fresh
        self.ch1_current.setValue(0)
        self.ch2_current.setValue(0)
        self.ch3_current.setValue(0)
        self.ch4_current.setValue(0)
        self.ch5_current.setValue(0)
        
        self.campus_graph.hospitals['H1']['capacity'] = 0
        self.campus_graph.hospitals['H2']['capacity'] = 0
        self.campus_graph.hospitals['H3']['capacity'] = 0
        self.campus_graph.hospitals['H4']['capacity'] = 0
        self.campus_graph.hospitals['H5']['capacity'] = 0
        
        # Get all campus buildings
        campus_buildings = ['MC', 'LIB', 'SCI', 'ENG', 'CMP', 'ART', 'GYM', 'CAF', 'DRM']
        
        # Clear previous results
        self.campus_results.clear()
        result_text = "Campus Simulation Results:\n" + "="*50 + "\n\n"
        
        # Run simulation with 10 random emergencies
        import random
        num_emergencies = 10
        
        for i in range(num_emergencies):
            # Randomly select an emergency location
            location = random.choice(campus_buildings)
            
            result_text += f"Emergency {i+1}: Location {location}\n"
            
            # Find the nearest available hospital
            hospital, path, distance = self.campus_graph.find_nearest_available_hospital(location)
            
            if hospital:
                # Update hospital capacity
                self.campus_graph.update_hospital_capacity(hospital)
                
                # Update capacity display
                if hospital == 'H1':
                    self.ch1_current.setValue(self.campus_graph.hospitals['H1']['capacity'])
                elif hospital == 'H2':
                    self.ch2_current.setValue(self.campus_graph.hospitals['H2']['capacity'])
                elif hospital == 'H3':
                    self.ch3_current.setValue(self.campus_graph.hospitals['H3']['capacity'])
                elif hospital == 'H4':
                    self.ch4_current.setValue(self.campus_graph.hospitals['H4']['capacity'])
                elif hospital == 'H5':
                    self.ch5_current.setValue(self.campus_graph.hospitals['H5']['capacity'])
                
                result_text += f"  Assigned to hospital {hospital}, distance: {distance}\n"
                result_text += f"  Path: {' -> '.join(path)}\n"
                result_text += f"  Hospital {hospital} now at capacity: {self.campus_graph.hospitals[hospital]['capacity']}/{self.campus_graph.hospitals[hospital]['max_capacity']}\n"
            else:
                result_text += "  No available hospital found! All hospitals are at full capacity.\n"
            
            result_text += "\nHospital status after emergency:\n"
            for h_id, info in self.campus_graph.hospitals.items():
                result_text += f"  {h_id}: {info['capacity']}/{info['max_capacity']}\n"
            
            result_text += "-"*50 + "\n"
            
            # Check if all hospitals are full
            if not self.campus_graph.get_available_hospitals():
                result_text += "\nAll hospitals are at full capacity. Ending simulation.\n"
                break
        
        # Display final results
        self.campus_results.setText(result_text)
        
        # Update visualization (last emergency)
        if hospital:
            self.campus_figure.clear()
            ax = self.campus_figure.add_subplot(111)
            self.campus_graph.visualize(path=path, emergency_node=location, 
                                      hospital_node=hospital, figure=self.campus_figure, ax=ax)
        else:
            self.campus_figure.clear()
            ax = self.campus_figure.add_subplot(111)
            self.campus_graph.visualize(emergency_node=location, 
                                      figure=self.campus_figure, ax=ax)
        
        self.campus_canvas.draw()
    
    def reset_campus_map(self):
        """Reset the campus map to its initial state"""
        # Reset the graph
        self.campus_graph = create_campus_map()
        
        # Reset hospital capacity controls
        self.ch1_current.setValue(0)
        self.ch2_current.setValue(0)
        self.ch3_current.setValue(0)
        self.ch4_current.setValue(0)
        self.ch5_current.setValue(0)
        
        # Clear results
        self.campus_results.clear()
        
        # Update visualization
        self.plot_campus_map()


def main():
    """Main function to run the GUI application"""
    print("Starting application...")
    print("Creating application...")
    app = QApplication(sys.argv)
    print("Application created")
    
    print("Creating main window...")
    window = EmergencyRoutingGUI()
    print("Main window created")
    
    print("Showing window...")
    window.show()
    window.raise_()  # Bring window to front