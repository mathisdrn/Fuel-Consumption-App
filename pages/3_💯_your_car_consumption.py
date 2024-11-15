import streamlit as st
import pandas as pd
import numpy as np
from utils import load_data, load_model

st.set_page_config(
    page_title="Your vehicle consumption",
    page_icon="💯",
    layout="wide",
    initial_sidebar_state="auto",
)

st.title("💯 Estimate your vehicle consumption")
st.write("Give us some informations about your vehicle and we will estimate its fuel consumption and CO2 emissions.")

df = load_data('data/fuel_consumption.csv')

# Create a form to get user input
with st.form(key='my_form'):
    col1, col2 = st.columns(2)
    with col1:
        make = st.selectbox('Make', df['make'].unique())
        release_year = st.text_input('Release year', value=2010, max_chars=4)
        transmission_type = st.selectbox('Transmission type', df['transmission_type'].unique())
        engine_size = st.slider('Engine size (L)', df['engine_size'].min(), df['engine_size'].max())
    with col2:
        vehicle_class = st.selectbox('Vehicle class', df['vehicle_class'].unique())
        fuel = st.selectbox('Fuel type', df['fuel_type'].unique())
        gears = st.selectbox('Gears', np.concatenate([df['gears'].dropna().unique(), ['Continuous variable']]))
        cylinders = st.slider('Cylinders', df['cylinders'].min(), df['cylinders'].max(), step=1)

    submitted = st.form_submit_button(label='Submit')

if submitted:
    car_features = {
        'make': [make],
        'release_year': [int(release_year)],
        'vehicle_class': [vehicle_class],
        'fuel_type': [fuel],
        'transmission_type': [transmission_type],
        'gears': [np.nan if gears == 'Continuous variable' else gears],
        'engine_size': [float(engine_size)],
        'cylinders': [int(cylinders)]
    }
    car_features_df = pd.DataFrame(car_features)
    
    # Load model
    model = load_model()
    
    # Predict
    result = model.predict(df).reshape(-1,)
    
    st.header('🛢️ &nbsp; Your results !')
    st.markdown(f"#### 💨 &nbsp; Emissions : {result[0]:.0f} g/km")
    st.markdown(f"#### 🔃 &nbsp; Mixed consumption : {result[1]:.1f} L/100 km")
    st.markdown(f"#### 🏙️ &nbsp; City consumption : {result[2]:.1f} L/100 km")
    st.markdown(f"#### 🛣️ &nbsp; Highway consumption : {result[3]:.1f} L/100 km")