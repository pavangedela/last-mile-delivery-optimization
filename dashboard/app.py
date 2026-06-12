import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import plotly.express as px
import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

from database.db_connection import get_connection

st.set_page_config(
    page_title="Last Mile Delivery Dashboard",
    layout="wide"
)

st.title("🚚 Last Mile Delivery Optimization Dashboard")

# ==========================
# DATABASE CONNECTION
# ==========================

# DATABASE CONNECTION

conn = get_connection()
st.write("Connected to database")

st.write(
    pd.read_sql("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    """, conn)
)

customers = pd.read_sql("""
SELECT *
FROM customers
ORDER BY customer_id
LIMIT 500
""", conn)

routes = pd.read_sql("""
SELECT *
FROM routes
ORDER BY route_id
""", conn)
drivers = pd.read_sql("""
SELECT *
FROM drivers
""", conn)

depot = pd.read_sql("""
SELECT *
FROM depot
LIMIT 1
""", conn)

st.write(customers.head())

status_filter = st.selectbox(
    "Route Status",
    ["All", "Planned", "Started", "Completed"]
)

if status_filter != "All":
    routes = routes[
        routes["route_status"] == status_filter
    ]
# ==========================
# KPI CALCULATIONS
# ==========================

total_customers = len(customers)
total_routes = len(routes)

total_distance = (
    routes["total_distance"].sum()
    if not routes.empty else 0
)

total_load = (
    routes["total_load"].sum()
    if not routes.empty else 0
)

vehicle_capacity = 1200  # 3 vehicles × 400 kg

utilization = round(
    (total_load / vehicle_capacity) * 100,
    2
) if vehicle_capacity > 0 else 0

# ==========================
# KPI CARDS
# ==========================

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Customers", total_customers)

with col2:
    st.metric("Routes", total_routes)

with col3:
    st.metric("Distance (km)", total_distance)

with col4:
    st.metric("Load (kg)", total_load)

with col5:
    st.metric("Utilization (%)", utilization)

st.divider()

# ==========================
# VEHICLE FILTER
# ==========================

if not routes.empty:

    selected_vehicle = st.selectbox(
        "Select Vehicle",
        ["All"] + list(routes["vehicle_id"].unique())
    )

    if selected_vehicle == "All":
        routes_display = routes
    else:
        routes_display = routes[
            routes["vehicle_id"] == selected_vehicle
        ]
else:
    routes_display = routes

# ==========================
# ROUTES TABLE
# ==========================

st.subheader("Saved Routes")

st.dataframe(
    routes, width="stretch"
)

# ==========================
# DOWNLOAD BUTTON
# ==========================

if not routes.empty:

    csv = routes.to_csv(index=False)

    st.download_button(
        label="📥 Download Routes CSV",
        data=csv,
        file_name="optimized_routes.csv",
        mime="text/csv"
    )

st.divider()

# ==========================
# VEHICLE SUMMARY
# ==========================

st.subheader("Vehicle Summary")

summary = routes.groupby("vehicle_id").agg({
    "total_distance": "sum",
    "total_load": "sum"
}).reset_index()

st.dataframe(summary, width="stretch")

# Vehicle Utilization %
summary["utilization"] = (
    summary["total_load"] / 400 * 100
)

st.subheader("Vehicle Utilization (%)")

fig3 = px.bar(
    summary,
    x="vehicle_id",
    y="utilization",
    title="Vehicle Utilization (%)"
)

st.plotly_chart(fig3)

st.divider()


# ==========================
# CUSTOMER MAP
# ==========================

# Customer Locations + Routes
st.subheader("Customer Locations & Routes")

center_lat = customers["latitude"].mean()
center_lon = customers["longitude"].mean()

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=12
)
bounds = [
    [customers["latitude"].min(), customers["longitude"].min()],
    [customers["latitude"].max(), customers["longitude"].max()]
]

m.fit_bounds(bounds)

warehouse_lat = depot.iloc[0]["latitude"]
warehouse_lon = depot.iloc[0]["longitude"]

folium.Marker(
    [warehouse_lat, warehouse_lon],
    popup="Warehouse",
    icon=folium.Icon(
        color="red",
        icon="home"
    )
).add_to(m)

# Customer markers
marker_cluster = MarkerCluster().add_to(m)
for _, row in customers.iterrows():
    folium.Marker(
        location=[
            row["latitude"],
            row["longitude"]
        ],
        popup=f"""
Customer: {row['customer_id']}<br>
Demand: {row['demand']}
"""
    ).add_to(marker_cluster)

# --------------------------------
# DRAW ROUTES
# --------------------------------

route_colors = {
    "V1": "red",
    "V2": "blue",
    "V3": "green"
}

for _, route in routes.iterrows():

    vehicle = route["vehicle_id"]

    try:
        nodes = eval(route["route_coordinates"])
    except:
        continue

    coordinates = []

    for node in nodes:

        if node == 0:
            continue

        if node >= len(customers):
            continue

        customer = customers.iloc[node]

        coordinates.append([
            customer["latitude"],
            customer["longitude"]
        ])

    if len(coordinates) > 1:

        folium.PolyLine(
            coordinates,
            color=route_colors.get(vehicle, "black"),
            weight=5,
            opacity=0.8,
            tooltip=vehicle
        ).add_to(m)

st_folium(
    m,
    width="stretch",
    height=850
)

st.divider()

st.subheader("Distance per Vehicle")

fig = px.bar(
    routes,
    x="vehicle_id",
    y="total_distance",
    color="vehicle_id",
    title="Distance Travelled by Each Vehicle"
)

st.plotly_chart(fig)

st.subheader("Load Distribution")

fig2 = px.pie(
    routes,
    names="vehicle_id",
    values="total_load",
    title="Load Distribution Across Vehicles"
)

st.plotly_chart(fig2)

st.subheader("Driver Information")

driver_summary = pd.merge(
    routes,
    drivers,
    on="vehicle_id",
    how="left"
)

st.dataframe(
    driver_summary[
        [
            "vehicle_id",
            "driver_name",
            "phone",
            "total_load",
            "total_distance"
        ]
    ],
    width="stretch"
)

st.subheader("Route Status Distribution")

status_counts = routes["route_status"].value_counts()

fig_status = px.pie(
    values=status_counts.values,
    names=status_counts.index,
    title="Route Status Distribution"
)

st.plotly_chart(fig_status)

st.subheader("Update Route Status")

selected_route = st.selectbox(
    "Select Route",
    routes["route_id"].tolist()
)

new_status = st.selectbox(
    "New Status",
    ["Planned", "Started", "Completed"]
)

if st.button("Update Status"):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE routes
        SET route_status = %s
        WHERE route_id = %s
        """,
        (
            new_status,
            selected_route
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

    st.success(
        f"Route {selected_route} updated to {new_status}"
    )

st.divider()

st.subheader("🚚 Delivery Progress Simulator")

selected_vehicle = st.selectbox(
    "Select Vehicle for Simulation",
    routes["vehicle_id"].unique(),
    key="simulation_vehicle"
)

if st.button("Start Delivery Simulation"):

    import time

    progress_bar = st.progress(0)

    status_text = st.empty()

    for i in range(101):

        progress_bar.progress(i)

        status_text.write(
            f"Vehicle {selected_vehicle} Progress: {i}%"
        )

        time.sleep(0.03)

    st.success(
        f"Vehicle {selected_vehicle} Delivery Completed!"
    )