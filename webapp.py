import streamlit as st
import folium
import osmnx
import networkx as nx
import leafmap.foliumap as leafmap
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

from app.locator import *

BASEMAPS = ['Satellite', 'Roadmap', 'Terrain', 'Hybrid', 'OpenStreetMap']
TRAVEL_MODE = ['Drive', 'Walk', 'Bike']
TRAVEL_OPTIMIZER = ['Length', 'Time']

ADDRESS_DEFAULT = "Grand Place, Bruxelles"
DIRECTION_MODE = [' ', 'click', 'address']


def clear_text():
    st.session_state["go_from"] = ""
    st.session_state["go_to"] = ""


st.set_page_config(page_title="🏥 Nearest Hospital Finder", layout="wide")

# Add simple page switching logic
if 'show_map' not in st.session_state:
    st.session_state.show_map = False

# Enhanced homepage with better visuals and layout
if not st.session_state.show_map:
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .big-font {
        font-size:50px !important;
        font-weight:bold;
        color:#2c3e50;
        margin-bottom:10px;
    }
    .subtitle {
        font-size:25px;
        color:#34495e;
        margin-bottom:30px;
    }
    .card {
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .card-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 15px;
        color: #3498db;
    }
    .icon-text {
        font-size: 18px;
        margin-left: 10px;
        vertical-align: middle;
    }
    .feature-icon {
        font-size: 24px;
        vertical-align: middle;
        color: #3498db;
    }
    .step-number {
        background-color: #3498db;
        color: white;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        display: inline-block;
        text-align: center;
        line-height: 30px;
        margin-right: 10px;
    }
    .header-container {
        padding: 40px 0;
        text-align: center;
        background: linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%);
        border-radius: 10px;
        margin-bottom: 30px;
    }
    .btn-primary {
        background-color: #e74c3c;
        padding: 15px 30px;
        font-size: 20px;
        font-weight: bold;
        border-radius: 50px;
        border: none;
        color: white;
        cursor: pointer;
        transition: all 0.3s ease;
        display: block;
        text-align: center;
        margin: 30px auto;
        max-width: 300px;
    }
    .btn-primary:hover {
        background-color: #c0392b;
        transform: scale(1.05);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header section
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    st.markdown('<p class="big-font">🏥 Nearest Hospital Finder</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Emergency medical assistance at your fingertips</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content with columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Features section with icons
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🚀 Key Features</div>', unsafe_allow_html=True)
        st.markdown("""
        <p><span class="feature-icon">🗺️</span><span class="icon-text">Interactive map with click-to-select location</span></p>
        <p><span class="feature-icon">📍</span><span class="icon-text">Instant address detection at selected points</span></p>
        <p><span class="feature-icon">🏥</span><span class="icon-text">Quick discovery of nearby hospitals</span></p>
        <p><span class="feature-icon">🛣️</span><span class="icon-text">Visualization of shortest paths to hospitals</span></p>
        <p><span class="feature-icon">⚡</span><span class="icon-text">Fast pathfinding with custom algorithm</span></p>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # About section
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📱 About the App</div>', unsafe_allow_html=True)
        st.markdown("""
        This interactive application helps users find the closest hospital during emergencies.
        Using real-time OpenStreetMap data, it visualizes the shortest path to nearby hospitals,
        helping you reach medical assistance as quickly as possible.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # How it works section with numbered steps
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🧭 How It Works</div>', unsafe_allow_html=True)
        st.markdown("""
        <p><span class="step-number">1</span> Click on the map to select your location</p>
        <p><span class="step-number">2</span> The app retrieves your address</p>
        <p><span class="step-number">3</span> Nearby hospitals are identified</p>
        <p><span class="step-number">4</span> The shortest path is calculated</p>
        <p><span class="step-number">5</span> Route and hospital details are displayed</p>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Technology stack
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🛠️ Powered By</div>', unsafe_allow_html=True)
        st.markdown("""
        - Streamlit
        - OpenStreetMap
        - OSMnx
        - NetworkX
        - Folium
        - Geopy
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Single CTA button that actually works
    if st.button("Start Finding Hospitals", type="primary", use_container_width=True):
        st.session_state.show_map = True
        st.rerun()

# Original map functionality code, only displayed when show_map is True
else:
    # Add a button to return to the homepage
    if st.button("← Back to Home"):
        st.session_state.show_map = False
        st.rerun()
        
    st.title("🚋 Route Finder")
    
    # ====== SIDEBAR ======
    with st.sidebar:
        st.title("Choose you travel settings")

        st.markdown("A simple app that finds and displays the shortest path between two points on a map.")

        basemap = st.selectbox("Choose basemap", BASEMAPS)
        if basemap in BASEMAPS[:-1]:
            basemap = basemap.upper()

        # transport = st.selectbox("Choose transport", TRAVEL_MODE)
        optimizer = st.selectbox("Choose optimizer", TRAVEL_OPTIMIZER)

        # TODO: integrate the emergency and availability options
        emergency = st.toggle("Emergency?", value=False)
        availability = st.toggle("Check Availability?", value=False)

        # TODO: show all the hospitals markers
        radius = st.slider("Search radius (in meters)", min_value=10000, max_value=50000, value=10000, step=1000)

    # ====== MAIN PAGE ======


    # Define the initial coordinates for the map (e.g., San Francisco)
    neu_sv = (37.33765749541021, -121.88963941434811)


    # Initialize session state variables
    if 'markers' not in st.session_state:
        st.session_state.markers = []
    if 'map_center' not in st.session_state:
        st.session_state.map_center = neu_sv
    if 'map_initialized' not in st.session_state:
        st.session_state.map_initialized = False


    # Initialize the default hospital display (can be displayed without clicking on the map)
    if 'last_radius' not in st.session_state:
        st.session_state.last_radius = radius

    if radius != st.session_state.last_radius:
        # radius change, update the map
        center_point = st.session_state.get("map_center", neu_sv)
        graph, location_orig, location_dest, hospitals_coordinates, hospital_name = get_graph(center_point, radius)
        if graph is None or location_dest is None:
            st.session_state.markers = [{
                'name': 'You are here',
                'location': center_point,
                'icon': folium.Icon(color='red', icon='suitcase', prefix='fa')
            }]
            st.warning(
                "No hospitals found within the selected radius. Try increasing radius or selecting a different location.")
            st.stop()

        st.session_state.markers = []

        # mark start point: fix the start maker missing issue when dragging the radius
        st.session_state.markers.append({
            'name': 'You are here',
            'location': (location_orig[0], location_orig[1]),
            'icon': folium.Icon(color='red', icon='suitcase', prefix='fa')  # or icon='flag'
        })

        # mark the hospitals
        for hospital_point in hospitals_coordinates:
            name = hospital_point.get('name', 'Unnamed')
            geom = hospital_point['geometry']
            st.session_state.markers.append({
                'name': name,
                'location': (geom.y, geom.x),
                'icon': folium.Icon(color='blue', icon='plus', prefix='fa')
            })

        # update the shortest path
        route = find_shortest_path(graph, location_orig, location_dest, optimizer)
        route_path = osmnx.routing.route_to_gdf(graph, route)
        st.session_state.route_path = route_path

        # update states
        st.session_state.last_radius = radius
        st.session_state.map_center = center_point
        st.session_state.map_initialized = True


    if 'default_mark' not in st.session_state:
        st.session_state.default_mark = []
        st.session_state.default_mark.append({
            'location': neu_sv,
            'icon': folium.Icon(color='green', icon='eye', prefix='fa')
        })
    if 'route_path' not in st.session_state:
        st.session_state.route_path = None

    # Create a Leafmap map centered at the stored center
    m = leafmap.Map(center=st.session_state.map_center, zoom=16, control_scale=True)
    m.add_basemap(basemap)

    # Add existing markers from session state
    for marker in st.session_state.markers:
        m.add_marker(location=marker['location'], icon=marker['icon'])
        lat = marker['location'][0]
        lon = marker['location'][1]
        st.success(f"📫 Name/Address: {marker['name']}")
        st.write(f"📍 Coordinates: ({lat:.5f}, {lon:.5f})")

    if st.session_state.route_path is not None:
        st.session_state.route_path.explore(m=m)

    # Display the map in the Streamlit app and capture click events
    map_data = m.to_streamlit(height=500, bidirectional=True)

    # Initialize the geolocator
    geolocator = Nominatim(user_agent="streamlit-geocoder")

    # Check if the user has clicked on the map
    if map_data and map_data.get("last_clicked"):
        last_click = map_data["last_clicked"]
        if "lat" in last_click and "lng" in last_click:
            lat = last_click["lat"]
            lon = last_click["lng"]
        # Extract latitude and longitude from the click event
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]
        # st.write(f"📍 Coordinates: ({lat:.5f}, {lon:.5f})")

        # Perform reverse geocoding to get the address
        try:
            location = geolocator.reverse((lat, lon), exactly_one=True, timeout=5)
        except Exception as e:
            st.error(f"⚠️ Reverse geocoding failed: {e}")
            location = None

        if location:
            st.success(f"📫 Address: {location.address}")
            st.info("Wait for few seconds until the nearest hospital is found.")
            # Add a new marker to session state
            st.session_state.markers = []

            # ===================
            graph, location_orig, location_dest, hospitals_coordinates, hospital_name = get_graph((lat, lon), radius)

            # Check if the graph is None (no hospitals found will show in app )
            if graph is None or location_dest is None :
                st.session_state.map_center = (lat, lon)
                st.session_state.markers = [{
                    'name': location.address,
                    'location': (lat, lon),
                    'icon': folium.Icon(color='red', icon='suitcase', prefix='fa')
                }]
                st.warning(
                    "No hospitals found within the selected radius. Try increasing radius or selecting a different location.")
                st.stop()
                # st.rerun()

            st.session_state.markers.append({
                'name': location.address,
                'location': location_orig,
                'icon': folium.Icon(color='red', icon='suitcase', prefix='fa')
            })
            st.session_state.markers.append({
                'name': hospital_name,
                'location': location_dest,
                'icon': folium.Icon(color='green', icon='street-view', prefix='fa')
            })

            # Show all hospital markers within the radius
            for hospital_point in hospitals_coordinates:
                name = hospital_point.get('name', 'Unnamed')
                geom = hospital_point['geometry']
                st.session_state.markers.append({
                    'name': name,
                    'location': (geom.y, geom.x),
                    'icon': folium.Icon(color='blue', icon='plus', prefix='fa')
                })

            # Find the shortest path
            route = find_shortest_path(graph, location_orig, location_dest, optimizer)
            route_path = osmnx.routing.route_to_gdf(graph, route)
            st.session_state.route_path = route_path

            # Update map center in session state
            st.session_state.map_center = (lat, lon)
            # Rerun the app to update the map immediately
            st.rerun()
        else:
            st.warning("Address not found for this location.")
    else:
        st.info("Click on the map to get the address of that location.")