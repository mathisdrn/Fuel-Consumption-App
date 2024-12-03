import streamlit as st
import altair as alt
import pandas as pd
from utils import get_car_data, percentage_change

st.set_page_config(
    page_title="Fuel consumption - Dashboard",
    page_icon="📈",
    layout = "wide"
)

st.title("📈 Dashboard")

df = get_car_data() 

# -------------- Metric --------------

# Group by year and calculate the required metrics
metrics_df = df.groupby(df['release_year']).agg(
    model_count=('make', 'count'),
    mixed_consumption=('fc_mixed', 'mean'),
    emissions=('emissions', 'mean')
).reset_index()

# Extract metrics for 2021 and 2022
m_2021 = metrics_df[metrics_df['release_year'] == 2021].iloc[0]
m_2022 = metrics_df[metrics_df['release_year'] == 2022].iloc[0]

# Display metrics
st.header("Overview - Year on Year")

col1, col2, col3 = st.columns(3)
col1.metric("Number of models", f"{m_2021['model_count']:.0f}", f"{percentage_change(m_2022['model_count'], m_2021['model_count']):.1%}")
col2.metric("Mixed consumption (L/100km)", f"{m_2022['mixed_consumption']:.1f} L", f"{m_2022['mixed_consumption'] - m_2021['mixed_consumption']:.2f} L", delta_color='inverse')
col3.metric("Vehicle emissions", f"{m_2022['emissions']:.0f} g/km", f"{percentage_change(m_2022['emissions'], m_2021['emissions']):.2%}", delta_color='inverse')

# ------------- Plotting -------------

# Number of models released over time
temp = df.groupby('release_year').size().reset_index(name='model_count')

chart = alt.Chart(temp).mark_line().encode(
    x=alt.X('release_year:O', title='Year', axis=alt.Axis(labelAngle=0, values=temp['release_year'].unique()[::2])),
    y=alt.Y('model_count:Q', title='Number of models'),
    tooltip=['release_year', 'model_count']
).properties(title='Number of models released over time')
st.altair_chart(chart, use_container_width=True)

# Vehicle class proportion over time
temp = df.groupby(['release_year', 'vehicle_class']).size().reset_index(name='model_count')
temp['proportion'] = temp['model_count'] / temp.groupby('release_year')['model_count'].transform('sum') 

chart = alt.Chart(temp).mark_area().encode(
    x=alt.X('release_year:O', title='Year', axis=alt.Axis(labelAngle=0, values=temp['release_year'].unique()[::2])),
    y=alt.Y('proportion:Q', title='Proportion of Vehicle Class', axis=alt.Axis(format='%')),
    color=alt.Color('vehicle_class:N', title='Vehicle Class'),
    tooltip=[
        alt.Tooltip('release_year:O', title='Year'),
        alt.Tooltip('vehicle_class:N', title='Vehicle Class'),
        alt.Tooltip('proportion:Q', title='Proportion', format='.2%')]
).properties(title='Vehicle Class Proportion Over Time')
st.altair_chart(chart, use_container_width=True)

# Vehicle fuel type proportion over time
temp = df.groupby(['release_year', 'fuel_type']).size().reset_index(name='model_count')
temp['proportion'] = temp['model_count'] / temp.groupby('release_year')['model_count'].transform('sum')

chart_fuel = alt.Chart(temp).mark_bar().encode(
    x=alt.X('release_year:O', title='Year', axis=alt.Axis(labelAngle=0, values=temp['release_year'].unique()[::2])),
    y=alt.Y('proportion:Q', title='Percentage of Fuel Type', axis=alt.Axis(format='%')),
    color=alt.Color('fuel_type:N', title='Fuel Type'),
    tooltip=[
        alt.Tooltip('release_year:O', title='Year'),
        alt.Tooltip('fuel_type:N', title='Fuel Type'),
        alt.Tooltip('proportion:Q', title='Percentage', format='.2%')]
).properties(title='Vehicle Fuel Type Proportion Over Time')
st.altair_chart(chart_fuel, use_container_width=True)

# Fuel type proportion versus vehicle type
temp = df.groupby(['vehicle_class', 'fuel_type']).size().reset_index(name='model_count')
temp['proportion'] = temp['model_count'] / temp.groupby('vehicle_class')['model_count'].transform('sum')

order = df.groupby(['vehicle_class'])['make'].count().sort_values(ascending=False).index.to_list()

chart_fuel = alt.Chart(temp).mark_bar().encode(
    x=alt.X('proportion:Q', title='Fuel Type Proportion', axis=alt.Axis(format='%')),
    y=alt.Y('vehicle_class:O', sort=order, title=None),
    color=alt.Color('fuel_type:N', title='Fuel Type'),
    tooltip=[
        alt.Tooltip('vehicle_class:O', title='Vehicle Type'),
        alt.Tooltip('fuel_type:N', title='Fuel Type'),
        alt.Tooltip('proportion:Q', title='Percentage', format='.2%')
    ]
).properties(title='Fuel Type Proportion versus Vehicle Type')
st.altair_chart(chart_fuel, use_container_width=True)

st.markdown('### Vehicle emissions')

# Vehicle emissions over time for a specific fuel type
fuel_type = st.selectbox('Select a fuel type', df['fuel_type'].unique(), index=0)

temp = df[df['fuel_type'] == fuel_type]
temp = temp.groupby(['release_year', 'vehicle_class'])['emissions'].mean().reset_index()

chart_emissions = alt.Chart(temp).mark_line().encode(
    x=alt.X('release_year:O', title='Year', axis=alt.Axis(labelAngle=0, values=temp['release_year'].unique()[::2])),
    y=alt.Y('emissions:Q', title='Emissions (g/km)'),
    color=alt.Color('vehicle_class:N', title='Vehicle Type'),
    tooltip=[
        alt.Tooltip('release_year:O', title='Year'),
        alt.Tooltip('vehicle_class:N', title='Vehicle Type'),
        alt.Tooltip('emissions:Q', title='Emissions (g/km)', format='.2f')]
).properties(title=f'Average Emissions by Vehicle Type for {fuel_type}')
st.altair_chart(chart_emissions, use_container_width=True)

# Vehicle emissions over time for a specific vehicle class
vehicle_class = st.selectbox('Select a vehicle type', df['vehicle_class'].unique(), index=0)

temp = df[df['vehicle_class'] == vehicle_class]
temp = temp.groupby(['release_year', 'fuel_type'])['emissions'].mean().reset_index()

chart_emissions = alt.Chart(temp).mark_line().encode(
    x=alt.X('release_year:O', title='Year', axis=alt.Axis(labelAngle=0, values=temp['release_year'].unique()[::2])),
    y=alt.Y('emissions:Q', title='Emissions (g/km)'),
    color=alt.Color('fuel_type:N', title='Fuel Type'),
    tooltip=[
        alt.Tooltip('release_year:O', title='Year'),
        alt.Tooltip('fuel_type:N', title='Fuel Type'),
        alt.Tooltip('emissions:Q', title='Emissions (g/km)', format='.2f')]
).properties(title=f'Average Emissions by Fuel Type for {vehicle_class}')
st.altair_chart(chart_emissions, use_container_width=True)