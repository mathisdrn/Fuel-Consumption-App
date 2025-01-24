import streamlit as st
import polars as pl
import numpy as np
from utils import get_car_data, load_model

st.set_page_config(
    page_title="Your vehicle consumption",
    page_icon="💯",
    layout="centered",
    initial_sidebar_state="auto",
)

st.title("💯 Estimate your vehicle consumption")
st.write("Give us some informations about your vehicle and we will estimate its fuel consumption and CO2 emissions.")

df = get_car_data()

col1, col2 = st.columns(2)
with col1:
    make = st.selectbox('Make', df['make'].unique().sort())
    release_year = st.text_input('Release year', value=2010)
    transmission_type = st.selectbox('Transmission type', df['transmission_type'].unique().sort())
    engine_size = st.slider('Engine size (L)', df['engine_size'].min(), df['engine_size'].max(), step=0.1, value=2.0, format='%.1f L')
with col2:
    vehicle_class = st.selectbox('Vehicle class', df['vehicle_class'].unique().sort())
    fuel = st.selectbox('Fuel type', df['fuel_type'].unique().sort())
    gears = st.slider('Gears', df['gears'].min(), df['gears'].max(), step=1, value=5, format='%.0f')
    cylinders = st.slider('Cylinders', df['cylinders'].min(), df['cylinders'].max(), step=1, value=4)

car_features = {
    'make': [make],
    'release_year': [int(release_year)],
    'vehicle_class': [vehicle_class],
    'fuel_type': [fuel],
    'transmission_type': [transmission_type],
    'gears': [gears if transmission_type != 'Continuously variable' else np.nan],
    'engine_size': [float(engine_size)],
    'cylinders': [int(cylinders)]
}

car_features_df = pl.DataFrame(car_features)

# Load model
model = load_model()

# Predict
result = model.predict(car_features_df).reshape(-1)

st.header('Estimate')
st.markdown(f"#### 💨 &nbsp; Emissions : {result[0]:.0f} g/km")
st.markdown(f"#### 🔃 &nbsp; Mixed consumption : {result[1]:.1f} L/100 km")
st.markdown(f"#### 🏙️ &nbsp; City consumption : {result[2]:.1f} L/100 km")
st.markdown(f"#### 🛣️ &nbsp; Highway consumption : {result[3]:.1f} L/100 km")