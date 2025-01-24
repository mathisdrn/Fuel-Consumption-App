import streamlit as st
import pandas as pd
from streamlit_extras.dataframe_explorer import dataframe_explorer
from utils import get_car_data, display_columns_name_mapping

st.set_page_config(
    page_title="Vehicle finder",
    page_icon="🚘",
    layout="wide",
    initial_sidebar_state="auto",
)

st.title('🚘 Vehicle finder')

st.markdown("Find a vehicle from it's caracteristics")

# Load and preprocess data
df = get_car_data()

# Convert to Pandas DataFrame
df = df.to_pandas()

df = df.rename(columns=display_columns_name_mapping)

col1, col2 = st.columns(2)

# Filter by make
with col1:
    selected_make = st.selectbox('Make', sorted(df['Make'].unique()), index=None, placeholder="Select a make")

if selected_make:
    df = df[df['Make'] == selected_make]

# Filter by model
with col2:
    selected_model = st.selectbox('Model', sorted(df['Model'].unique()), index=None, placeholder="Select a model")

if selected_model:
    df = df[df['Model'] == selected_model]

# Manual filter

col_for_manual_filter = ['Release year', 'Vehicle class', 'Fuel Type', 'Transmission', 'Gears', 'Engine size (L)', 'Cylinders', 'CO2 emissions (g/km)', 'Mixed (L/100 km)']
# Filter column that only have one unique value
for col in col_for_manual_filter:
    if df[col].nunique() == 1:
        col_for_manual_filter.remove(col)
# Remove manual filter if there is only one row
if df.shape[0] == 1:
    col_for_manual_filter = []

filtered_indices = dataframe_explorer(df[col_for_manual_filter]).index
df = df[df.index.isin(filtered_indices)]

# Sort and display
df = df.sort_values(by=['Make', 'Model', 'Release year', 'Vehicle class', 'Fuel Type', 'Transmission', 'Gears'], ascending=False)

col_display_order = ['Release year', 'Make', 'Model', 'Vehicle class', 'Engine size (L)', 'Cylinders', 'Transmission', 'Gears', 'Fuel Type', 'City (L/100 km)', 'Highway (L/100 km)', 'Mixed (L/100 km)', 'CO2 emissions (g/km)']

st.dataframe(df, use_container_width=True, hide_index=True, column_order=col_display_order)