import polars as pl
import streamlit as st

from src.utils import load_car_data, load_model

st.set_page_config(
    page_title="Your vehicle consumption",
    page_icon="💯",
    layout="centered",
    initial_sidebar_state="auto",
)

st.title("💯 Estimate your vehicle consumption")
st.write(
    "Give us some informations about your vehicle and we will estimate its fuel consumption and CO2 emissions."
)

df = load_car_data()

col1, col2 = st.columns(2)
with col1:
    make = st.selectbox(label="Make", options=df["make"].unique().sort())
    release_year = st.selectbox(label="Release year", options=range(2025, 1979, -1))
    transmission_type = st.selectbox(
        label="Transmission type", options=df["transmission_type"].unique().sort()
    )
    engine_size = st.slider(
        label="Engine size (L)",
        min_value=df["engine_size"].min(),
        max_value=df["engine_size"].max(),
        value=2.0,
        step=0.1,
        format="%.1f L",
    )
with col2:
    vehicle_class = st.selectbox(
        label="Vehicle class", options=df["vehicle_class"].unique().sort()
    )
    fuel = st.selectbox(label="Fuel type", options=df["fuel_type"].unique().sort())
    gears = st.slider(
        label="Gears",
        min_value=df["gears"].min(),
        max_value=df["gears"].max(),
        value=5,
        step=1,
        format="%.0f",
    )
    cylinders = st.slider(
        label="Cylinders",
        min_value=df["cylinders"].min(),
        max_value=df["cylinders"].max(),
        value=4,
        step=1,
    )

car_features = {
    "make": [make],
    "release_year": [int(release_year)],
    "vehicle_class": [vehicle_class],
    "fuel_type": [fuel],
    "transmission_type": [transmission_type],
    "gears": [None if transmission_type == "Continuously variable" else gears],
    "engine_size": [float(engine_size)],
    "cylinders": [int(cylinders)],
}

car_features_df = pl.DataFrame(car_features)

# Load model
model = load_model()

# Predict
result = model.predict(car_features_df).reshape(-1)

st.header("Estimate")
st.markdown(f"#### 💨 &nbsp; Emissions : {result[0]:.0f} g/km")
st.markdown(f"#### 🔃 &nbsp; Mixed consumption : {result[1]:.1f} L/100 km")
st.markdown(f"#### 🏙️ &nbsp; City consumption : {result[2]:.1f} L/100 km")
st.markdown(f"#### 🛣️ &nbsp; Highway consumption : {result[3]:.1f} L/100 km")
