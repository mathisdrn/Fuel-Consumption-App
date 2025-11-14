import polars as pl
import streamlit as st
from streamlit_extras.dataframe_explorer import dataframe_explorer

from src.utils import display_columns_name_mapping, load_car_data

st.set_page_config(
    page_title="Vehicle finder",
    page_icon="🚘",
    layout="wide",
    initial_sidebar_state="auto",
)

st.title("🚘 Vehicle finder")

st.markdown("Find a vehicle from it's caracteristics")

# Load and preprocess data
df = load_car_data()

df = df.rename(display_columns_name_mapping)

# Filters

col1, col2 = st.columns(2)
with col1:
    selected_make = st.selectbox(
        "Make", df["Make"].unique().sort(), index=None, placeholder="Select a make"
    )
    if selected_make:
        df = df.filter(pl.col("Make") == selected_make)

with col2:
    selected_model = st.selectbox(
        "Model", df["Model"].unique().sort(), index=None, placeholder="Select a model"
    )
    if selected_model:
        df = df.filter(pl.col("Model") == selected_model)

# Automatic filters

extra_cols_to_filter = [
    "Release year",
    "Vehicle class",
    "Fuel Type",
    "Transmission",
    "Gears",
    "Engine size (L)",
    "Cylinders",
    "CO2 emissions (g/km)",
    "Mixed (L/100 km)",
]

# Only propose to filter columns that have more than 1 unique value

# Way 1
col_for_manual_filter = df.select(
    [s for s in df if (s.name in extra_cols_to_filter) and s.n_unique() > 1]
).columns

# Way 2
col_for_manual_filter = (
    df.select(extra_cols_to_filter)
    .select(pl.all().n_unique())
    .transpose(include_header=True, header_name="column", column_names=["n_unique"])
    .filter(pl.col("n_unique") > 1)
    .get_column("column")
    .to_list()
)

# Way 3
col_for_manual_filter = [col for col in extra_cols_to_filter if df[col].n_unique() > 1]

# Convert to a Pandas DataFrame -> no support for Polars in dataframe_explorer
df = df.to_pandas()

filtered_indices = dataframe_explorer(df[col_for_manual_filter]).index
df = df[df.index.isin(filtered_indices)]

st.dataframe(
    df,
    width="stretch",
    hide_index=True,
)
