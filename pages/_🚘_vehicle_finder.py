import streamlit as st
import pandas as pd
from streamlit_extras.no_default_selectbox import selectbox
from streamlit_extras.dataframe_explorer import dataframe_explorer

st.set_page_config(
    page_title="🚘 Vehicle finder",
    page_icon="🚘",
    layout="centered",
    initial_sidebar_state="auto",
)

st.title('🚘 Vehicle finder')

st.markdown("""Find a vehicle from it's caracteristics""")

# Load data

df = pd.read_csv('data/fuel_consumption.csv', parse_dates=['YEAR'])
# Change Type of fuel to name
df['FUEL'] = df['FUEL'].replace({'X': 'Regular gasoline', 'Z': 'Premium gasoline', 'D': 'Diesel', 'E': 'Ethanol (E85)', 'N': 'Natural Gas'})
# Replace Model by full name
df['MODEL'] = df['MODEL'].replace({'4WD/4X4': 'Four-wheel drive', 'AWD': 'All-wheel drive', 'CNG': 'Compressed natural gas', 'FFV': 'Flexible-fuel vehicle', 'NGV': 'Natural gas vehicle', '#': 'High output engine'})
# Extract last caracter of transmission as number of gears
# ie. 816 cars have continuous variable transmission and don't have a number of gears
df['GEARS'] = df['TRANSMISSION'].str.extract(r'(\d+)$', expand=False)
df['TRANSMISSION'] = df['TRANSMISSION'].str.replace(r'\d+$', '')
df['TRANSMISSION'] = df['TRANSMISSION'].replace({'A': 'Automatic', 'AM': 'Automated manual', 'AS': 'Automatic with select shift', 'AV': 'Continuously variable', 'M': 'Manual'})
# Rename FUEL CONSUMPTION to CITY (L/100 km)
df = df.drop(columns=['COMB (mpg)'], axis = 1)
df = df.rename(columns={'FUEL CONSUMPTION': 'CITY (L/100 km)'})
# Capitalize MAKE
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
# reorder column
df = df[['Make', 'Model', 'Release year', 'Vehicle class', 'Fuel', 'Transmission', 'Gears', 'Engine size (L)', 'Cylinders', 'CO2 emissions (g/km)', 'Mixed consumption (L/100 km)', 'City (L/100 km)', 'Highway (L/100 km)']]
filter = df.copy()

col1, col2 = st.columns(2)
with col1:
    make = selectbox('Make', df['Make'].unique())
if make:
    filter = filter[df['Make'] == make] 

with col2:
    options = filter['Model'].unique()
    options.sort()
    model = selectbox('Model', options)
if model:
    filter = filter[filter['Model'] == model]

col_manually_filter = filter[['Release year', 'Vehicle class', 'Fuel', 'Transmission', 'Gears', 'Engine size (L)', 'Cylinders', 'CO2 emissions (g/km)', 'Mixed consumption (L/100 km)', 'City (L/100 km)', 'Highway (L/100 km)']]
index_col_manually_filter = dataframe_explorer(col_manually_filter).index

filter = filter[filter.index.isin(index_col_manually_filter)]
filter = filter.sort_values(by = ['Make', 'Model', 'Release year', 'Vehicle class', 'Fuel', 'Transmission', 'Gears'])
filter = filter.reset_index(drop=True)
st.dataframe(filter, use_container_width=True)