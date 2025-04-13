# 🏥 Nearest Hospital Finder (emergency-routing)
An interactive Streamlit app that helps users find the closest hospital in San Francisco. It leverages real-time OpenStreetMap data, visualizes it with Folium, and computes the shortest path using OSMnx and NetworkX

---

## 🚀 Features

- Interactive map with click-to-select location functionality
- Reverse geocoding to display the address of the selected point
- Retrieval of nearby hospitals using OSMnx
- Visualization of the shortest path to the nearest hospital
- Custom Dijkstra's algorithm implementation for pathfinding

---

## 🛠️ Installation

**Clone the repositor**

   ```bash
   git clone https://github.com/dianzi34/emergency-routing.git
   cd emergency-routing
   ```


**Create a virtual environment (optional but recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```


**Install the required package**

   ```bash
   pip install -r requirements.txt
   ```


---

## ▶️ Running the App

Start the Streamlit application with the following command:


```bash
streamlit run webapp.py
```


This will open the app in your default web browser at `http://localhost:8501`.

---

## 📁 Project Structue


```plaintext
nearest-hospital-sf/
├── webapp.py               # Main Streamlit application     
├── requirements.txt        # List of Python dependencies
├── README.md               # Project documentation
└── .app/
    └── locator.py         # Core Code
```


---

## 📌 Dependences

Ensure the following Python packages are instaled:

- streamlit
- osmnx
- networkx
- folium
- geopy
- leafmap
- pandas
- geopandas

These are listed in the `requirements.txt` file.

---

## 🧭 How It Work

1. **Map Interaction**: Users click on the map to select a location.
2. **Reverse Geocoding**: The app retrieves the address of the selected point.
3. **Hospital Retrieval**: Nearby hospitals are fetched using OSMnx within a specified radius.
4. **Pathfinding**: The shortest path to the nearest hospital is computed using a custom Dijkstra's algorithm.
5. **Visualization**: The path and hospital location are displayed on th map.

---

## 📷 Screenshots/Gifs



---

## 📄 Lcense

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🙌 Acknowledgents

- [OpenStreetMap](https://www.openstreetmap.org/) formap data
- [Streamlit](https://streamlit.io/) for the web application framework
- [OSMnx](https://github.com/gboeing/osmnx) for street network analysis
- [Folium](https://python-visualization.github.io/folium/) for interactive maps

---
