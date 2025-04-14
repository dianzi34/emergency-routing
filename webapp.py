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


st.set_page_config(page_title="🚋 Route finder", layout="wide")

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


# new-added:Initialize the default hospital display (can be displayed without clicking on the map)
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

    # mark start point:fix the start maker miss issue when drag the radius
    st.session_state.markers.append({
        'name': 'You are here',
        'location': (location_orig[0], location_orig[1]),
        'icon': folium.Icon(color='red', icon='suitcase', prefix='fa')  # 或 icon='flag'
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

# if 'address_from' not in st.session_state:
#     st.session_state.address_from = ""

# Create a Leafmap map centered at the stored center
m = leafmap.Map(center=st.session_state.map_center, zoom=16, control_scale=True)
m.add_basemap(basemap)

# Add existing markers from session state
for marker in st.session_state.markers:
    m.add_marker(location=marker['location'], icon=marker['icon'])
    lat = marker['location'][0];
    lon = marker['location'][1];
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

        # new-added:show all the hospitals markers within the radius
        for hospital_point in hospitals_coordinates:
            name = hospital_point.get('name', 'Unnamed')
            geom = hospital_point['geometry']
            st.session_state.markers.append({
                'name': name,
                'location': (geom.y, geom.x),
                'icon': folium.Icon(color='blue', icon='plus', prefix='fa')
            })

        # m.add_marker(location=list(location_orig), icon=folium.Icon(color='red', icon='suitcase', prefix='fa'))
        # m.add_marker(location=list(location_dest), icon=folium.Icon(color='green', icon='street-view', prefix='fa'))

        # find the shortest path
        route = find_shortest_path(graph, location_orig, location_dest, optimizer)

        # osmnx.plot_route_folium(graph, route, m)
        # osmnx.plot.plot_graph_route(graph, route)
        route_path = osmnx.routing.route_to_gdf(graph, route)
        st.session_state.route_path = route_path
        # route_path.explore(m=m)

        # ===================

        # Update map center in session state
        st.session_state.map_center = (lat, lon)
        # Rerun the app to update the map immediately
        st.rerun()
    else:
        st.warning("Address not found for this location.")
else:
    st.info("Click on the map to get the address of that location.")