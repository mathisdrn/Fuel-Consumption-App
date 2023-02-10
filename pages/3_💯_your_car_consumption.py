import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="💯 Your vehicle consumption",
    page_icon="💯",
    layout="centered",
    initial_sidebar_state="auto",
)

st.title("💯 What\'s your vehicle consumption")
st.write("""Give us some informations about your vehicle and it will predict its fuel consumption and CO2 emissions.""")
            
def load_data():
    df = pd.read_csv('data/fuel_consumption.csv', parse_dates=['YEAR'])
    # Change Type of fuel to name
    df['FUEL'] = df['FUEL'].replace({'X': 'Regular gasoline', 'Z': 'Premium gasoline', 'D': 'Diesel', 'E': 'Ethanol (E85)', 'N': 'Natural Gas'})
    # Extract last caracter of transmission as number of gears
    # ie. 816 cars have continuous variable transmission and don't have a number of gears
    df['GEARS'] = df['TRANSMISSION'].str.extract(r'(\d+)$', expand=False)
    df['TRANSMISSION'] = df['TRANSMISSION'].str.replace(r'\d+$', '')
    df['TRANSMISSION'] = df['TRANSMISSION'].replace({'A': 'Automatic', 'AM': 'Automated manual', 'AS': 'Automatic with select shift', 'AV': 'Continuously variable', 'M': 'Manual'})
    # Rename FUEL CONSUMPTION to CITY (L/100 km)
    df = df.drop(columns=['COMB (mpg)'], axis = 1)
    df = df.rename(columns={'FUEL CONSUMPTION': 'CITY (L/100 km)'})
    df['MAKE'] = df['MAKE'].str.capitalize()

    # Uniformize vehicle class
    df['VEHICLE CLASS'] = df['VEHICLE CLASS'].str.capitalize()
    df.loc[df['VEHICLE CLASS'].str.contains('Pickup truck'), 'VEHICLE CLASS'] = 'Pickup truck'
    df.loc[df['VEHICLE CLASS'].str.contains('Station wagon'), 'VEHICLE CLASS'] = 'Station wagon'
    df.loc[df['VEHICLE CLASS'].str.contains('Suv'), 'VEHICLE CLASS'] = 'SUV'
    df.loc[df['VEHICLE CLASS'].str.contains('Van'), 'VEHICLE CLASS'] = 'Van'

    # rename YEAR, VEHICLE CLASS, MAKE, MODEL, ENGINE SIZE, CYLINDERS, TRANSMISSION, FUEL, CITY (L/100 km), HWY (L/100 km), COMB (L/100 km), CO2 EMISSIONS (g/km)
    df = df.rename(columns={'YEAR': 'Release year', 'GEARS' : 'Gears', 'VEHICLE CLASS': 'Vehicle class', 'MAKE': 'Make', 'MODEL': 'Model', 'ENGINE SIZE': 'Engine size (L)', 'CYLINDERS': 'Cylinders', 'TRANSMISSION': 'Transmission', 'FUEL': 'Fuel', 'CITY (L/100 km)': 'City (L/100 km)', 'COMB (L/100 km)': 'Mixed consumption (L/100 km)', 'HWY (L/100 km)': 'Highway (L/100 km)', 'EMISSIONS': 'CO2 emissions (g/km)'})
    df['Release year'] = df['Release year'].dt.year
    # Target - Features
    X = df[['Make', 'Release year', 'Vehicle class', 'Fuel', 'Transmission', 'Gears', 'Engine size (L)', 'Cylinders']]
    Y = df[['CO2 emissions (g/km)', 'Mixed consumption (L/100 km)', 'City (L/100 km)', 'Highway (L/100 km)']]

    return X, Y

X, Y = load_data()

# Get unique parameters for each feature
make = X['Make'].unique()
vehicle_class = X['Vehicle class'].unique()
fuel = X['Fuel'].unique()
transmission = X['Transmission'].unique()
gears = X[X['Gears'].notnull()]['Gears'].unique()
gears.sort()
# append to numpy.ndarray 'Continuous variable'
gears = np.append(gears, 'Continuous variable')

min_eng, max_eng = float(X['Engine size (L)'].min()), float(X['Engine size (L)'].max())
min_cyl, max_cyl = float(X['Cylinders'].min()), float(X['Cylinders'].max())
min_release, max_release = float(X['Release year'].min()), float(X['Release year'].max())

def create_df(make, release_year, vehicle_class, fuel, transmission, gears, engine_size, cylinders):
    # if gears is continuous variable, set it to NaN
    if gears == 'Continuous variable':
        df['Gears'] = 2
    df = pd.DataFrame(data=[[make, release_year, vehicle_class, fuel, transmission, gears, engine_size, cylinders]],
                      columns=['Make', 'Release year', 'Vehicle class', 'Fuel', 'Transmission', 'Gears', 'Engine size (L)', 'Cylinders'])
    # Make sure the data types are correct
    df['Release year'] = df['Release year'].astype('int64')
    df['Engine size (L)'] = df['Engine size (L)'].astype('float64')
    df['Cylinders'] = df['Cylinders'].astype('int64')
    # df['Gears'] = df['Gears'].astype('float64')
    return df

# Create a form to get user input
with st.form(key='my_form'):
    col1, col2 = st.columns(2)
    with col1:
        make = st.selectbox('Make', make)
        release_year = st.text_input('Release year', value = 2010, max_chars = 4)
        transmission = st.selectbox('Transmission', transmission)
        engine_size = st.slider('Engine size (L)', min_eng, max_eng, min_eng)
    with col2:
        vehicle_class = st.selectbox('Vehicle class', vehicle_class)
        fuel = st.selectbox('Fuel', fuel)
        gears = st.selectbox('Gears', gears)
        cylinders = st.slider('Cylinders', int(min_cyl), int(max_cyl), step = 1)

    submitted = st.form_submit_button(label='Submit')

import joblib

if submitted:
    df = create_df(make, release_year, vehicle_class, fuel, transmission, gears, engine_size, cylinders)
    # st.write(df)
    # st.write(df.dtypes)
    # Load model
    model = joblib.load('prediction_model.pkl')
    # Predict
    st.header('🛢️ Your results !')
    result = model.predict(df).reshape(-1,)
    st.markdown(f"""

#### 💨 &nbsp; Emissions : {round(int(result[0]))} g/km

#### 🔃 &nbsp; Mixed consumption : {round(int(result[1]), 1)} L/100 km

#### 🏙️ &nbsp; City consumption : {round(int(result[2]), 1)} L/100 km

#### 🛣️ &nbsp; Highway consumption : {round(int(result[3]), 1)} L/100 km
""")