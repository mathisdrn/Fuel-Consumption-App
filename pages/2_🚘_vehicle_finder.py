import polars as pl
import streamlit as st

from src.utils import dataframe_explorer, display_columns_name_mapping, load_car_data

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

# Manual Filters for Make and Model
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
df = dataframe_explorer(df, excluded_columns=["Make", "Model"])

# Display the final dataframe
st.dataframe(
    df,
    width="stretch",
    hide_index=True,
)
