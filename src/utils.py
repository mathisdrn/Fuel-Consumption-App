import pickle
from pathlib import Path

import polars as pl
import streamlit as st
from sklearn.pipeline import Pipeline

DATA_PATH = Path("data/")

# Mapping of columns name to display name
display_columns_name_mapping = {
    "release_year": "Release year",
    "make": "Make",
    "model": "Model",
    "vehicle_class": "Vehicle class",
    "fuel_type": "Fuel Type",
    "engine_size": "Engine size (L)",
    "cylinders": "Cylinders",
    "transmission_type": "Transmission",
    "gears": "Gears",
    "fc_city": "City (L/100 km)",
    "fc_highway": "Highway (L/100 km)",
    "fc_mixed": "Mixed (L/100 km)",
    "emissions": "CO2 emissions (g/km)",
}


@st.cache_data
def load_car_data(folder_path: str | Path = DATA_PATH) -> pl.DataFrame:
    """Load the processed car data from a parquet file."""
    folder_path = Path(folder_path)
    df = pl.read_parquet(folder_path / "car_data.parquet")

    return df


@st.cache_data
def load_model(folder_path: str | Path = DATA_PATH) -> Pipeline:
    """Load the trained scikit-learn Pipeline model from a pickle file."""
    model_path = Path(folder_path) / "lasso_regression.pkl"

    with model_path.open("rb") as f:
        model = pickle.load(f)  # noqa: S301 deserialization is safe here

    return model


def percentage_change(new_value: float, old_value: float) -> float:
    if old_value == 0:
        return float("N/A")
    return (new_value - old_value) / old_value
