import streamlit as st
import altair as alt
import csv
import numpy as np
import pandas as pd

st.set_page_config(
    page_title="Fuel consumption - Dashboard",
    page_icon="📈",
)

st.title("📈 Dashboard")
# st.markdown("""This dashboard gives an overview of how car consume fuel.""")

def sep(val):
    return "{:,.0f}".format(val).replace(",", " ")

def perc(value, all_value):
    if value == all_value:
        return ""
    perc = (value - all_value) / all_value
    if perc > 0:
        return f'{round(perc * 100, 1)} %'
    else:
        return f'{round(perc * 100, 1)} %'

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

# Uniformize vehicle class
df['VEHICLE CLASS'] = df['VEHICLE CLASS'].str.capitalize()
df.loc[df['VEHICLE CLASS'].str.contains('Pickup truck'), 'VEHICLE CLASS'] = 'Pickup truck'
df.loc[df['VEHICLE CLASS'].str.contains('Station wagon'), 'VEHICLE CLASS'] = 'Station wagon'
df.loc[df['VEHICLE CLASS'].str.contains('Suv'), 'VEHICLE CLASS'] = 'SUV'
df.loc[df['VEHICLE CLASS'].str.contains('Van'), 'VEHICLE CLASS'] = 'Van'

# -------------- Metric --------------
df_2022 = df[df['YEAR'].dt.year == 2022]
df_2021 = df[df['YEAR'].dt.year == 2021]

model_in_2021 = df_2021['MAKE'].count()
model_in_2022 = df_2022['MAKE'].count()

comb_2021 = df_2021['COMB (L/100 km)'].mean()
comb_2022 = df_2022['COMB (L/100 km)'].mean()

emission_2021 = df_2021['EMISSIONS'].mean()
emission_2022 = df_2022['EMISSIONS'].mean()

st.header("Overview - YoY")

col1, col2, col3 = st.columns(3)
col1.metric("Number of models", f"{sep(model_in_2022)}", f"{perc(model_in_2022, model_in_2021)}")
col2.metric("Mixed consumption per 100km", f"{round(comb_2022, 1)} L", f"{round(comb_2022 - comb_2021, 2)} L", delta_color = 'inverse')
col3.metric("Vehicle emissions", f"{sep(emission_2022)} g/km", f"{perc(emission_2022, emission_2021)}", delta_color = 'inverse')

# ------------- Plotting -------------
# Number of model released by vehicle type
over_year_cars = df.groupby(['YEAR', 'VEHICLE CLASS'])['MAKE'].count().reset_index()
chart = alt.Chart(over_year_cars).mark_bar().encode(
    x = alt.X('year(YEAR):T', title='Year'),
    y = alt.Y('MAKE:Q', title='Number of models'),
    color = alt.Color('VEHICLE CLASS:N', title='Type of vehicle')
).properties(title = 'Number of model released by vehicle type')
st.altair_chart(chart, use_container_width=True)

# Vehicle fuel distribution over time
temp = df.groupby(['YEAR', 'FUEL']).size().reset_index(name='count')
temp['count'] = temp['count'] / temp.groupby('YEAR')['count'].transform('sum')
temp['YEAR'] = temp['YEAR'].dt.year
temp = temp.rename(columns={'YEAR': 'Year', 'FUEL': 'Fuel type', 'count': 'Percentage of fuel type'})

chart_fuel = alt.Chart(temp).mark_bar().encode(
    x=alt.X('Year:O', title='Year'),
    y=alt.Y('Percentage of fuel type:Q', title='Percentage of fuel type'),
    color=alt.Color('Fuel type:N', title='Fuel type'),
    tooltip=['Year', 'Fuel type', 'Percentage of fuel type']
).properties(title = 'Distribution of vehicle type of fuel')
st.altair_chart(chart_fuel, use_container_width=True)

# Type of fuel by vehicle type
temp = df.groupby(['VEHICLE CLASS', 'FUEL']).size().reset_index(name='count')
temp['count'] = temp['count'] / temp.groupby('VEHICLE CLASS')['count'].transform('sum')
temp = temp.rename(columns={'VEHICLE CLASS': 'Vehicle type', 'FUEL': 'Fuel type', 'count': 'Percentage of fuel type'})

order = df.groupby(['VEHICLE CLASS'])['MAKE'].count().sort_values(ascending=False).index.to_list()
chart_fuel = alt.Chart(temp).mark_bar().encode(
    x=alt.X('Percentage of fuel type:Q', title='Percentage of fuel type'),
    y=alt.Y('Vehicle type:O', sort = order, title = None),
    color=alt.Color('Fuel type:N', title='Fuel type'),
    tooltip=['Vehicle type', 'Fuel type', 'Percentage of fuel type']
).properties(title = 'Type of fuel by vehicle type')
st.altair_chart(chart_fuel, use_container_width=True)

st.markdown('### Vehicle emissions')

f_type = st.selectbox('Select a fuel type', df['FUEL'].unique(), index = 0)
temp = df.copy()
temp = temp[temp['FUEL'] == f_type]

# Compare vehicle emissions for a fuel type
temp2 = temp.groupby(['YEAR', 'VEHICLE CLASS'])['EMISSIONS'].mean().reset_index()

chart = alt.Chart(temp2).mark_line().encode(
    x = alt.X('year(YEAR):T', title='Year'),
    y = alt.Y('EMISSIONS:Q', title='Emissions (g/km)'),
    color = alt.Color('VEHICLE CLASS:N', title='Vehicle type')
).properties(title = f'Average emissions by vehicle type for {f_type}')
st.altair_chart(chart, use_container_width=True)

# Display the emissions by vehicle type over time
v_type = st.selectbox('Select a vehicle type', df['VEHICLE CLASS'].unique(), index = 0)
temp = df.copy()
temp = temp[temp['VEHICLE CLASS'] == v_type]
temp = temp.groupby(['YEAR', 'FUEL'])['EMISSIONS'].mean().reset_index()

chart = alt.Chart(temp).mark_line().encode(
    x = alt.X('year(YEAR):T', title='Year'),
    y = alt.Y('EMISSIONS:Q', title='Emissions (g/km)'),
    color = alt.Color('FUEL:N', title='Fuel type')
).properties(title = f'Average emissions by fuel type for {v_type}')
st.altair_chart(chart, use_container_width=True)