from pathlib import Path
from pickle import load
from typing import Any, TypeGuard

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
    folder_path = Path(folder_path)
    model_path = folder_path / "lasso_regression.pkl"

    with open(model_path, "rb") as f:
        model = load(f)

    if not _is_pipeline(model):  # Runtime type safety
        raise TypeError("Loaded object is not a sklearn Pipeline instance.")

    return model


def _is_pipeline(obj: Any) -> TypeGuard[Pipeline]:
    """Type guard to ensure the loaded object is a sklearn Pipeline."""
    return isinstance(obj, Pipeline)


def percentage_change(new_value: float, old_value: float) -> float:
    if old_value == 0:
        return float("N/A")
    return (new_value - old_value) / old_value
