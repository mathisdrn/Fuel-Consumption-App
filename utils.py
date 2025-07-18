from pathlib import Path

import dataframely as dy
import joblib
import polars as pl
import streamlit as st
from streamlit.runtime import exists as st_runtime_exists


# Define a dummy decorator to replace st.cache_data when not in a Streamlit context
def _noop_decorator(func):
    return func


# If not running in a Streamlit context, replace st.cache_data with the dummy decorator
if not st_runtime_exists():
    st.cache_data = _noop_decorator


MODEL_PATH = Path("data/lasso_regression.pkl")
DATA_PATH = Path("data/fuel_consumption.csv")


class CarDataSchema(dy.Schema):
    release_year = dy.Integer(nullable=False)
    vehicle_class = dy.String(nullable=False)
    make = dy.String(nullable=False)
    model = dy.String(nullable=False)
    engine_size = dy.Float(nullable=False)
    cylinders = dy.Integer(nullable=False)
    transmission_type = dy.String(nullable=False)
    gears = dy.Integer(nullable=True)
    fuel_type = dy.String(nullable=False)
    fc_city = dy.Float(nullable=False)
    fc_highway = dy.Float(nullable=False)
    fc_mixed = dy.Float(nullable=False)
    emissions = dy.Integer(nullable=False)


# Create a mapping for display names of columns
display_columns_name_mapping = {
    "release_year": "Release year",
    "vehicle_class": "Vehicle class",
    "make": "Make",
    "model": "Model",
    "engine_size": "Engine size (L)",
    "cylinders": "Cylinders",
    "transmission_type": "Transmission",
    "gears": "Gears",
    "fuel_type": "Fuel Type",
    "fc_city": "City (L/100 km)",
    "fc_highway": "Highway (L/100 km)",
    "fc_mixed": "Mixed (L/100 km)",
    "emissions": "CO2 emissions (g/km)",
}


@st.cache_data
def load_car_data(filepath=DATA_PATH) -> pl.DataFrame:
    columns_name = {
        "YEAR": "release_year",
        "VEHICLE CLASS": "vehicle_class",
        "MAKE": "make",
        "MODEL": "model",
        "ENGINE SIZE": "engine_size",
        "CYLINDERS": "cylinders",
        "TRANSMISSION": "transmission_info",
        "FUEL": "fuel_type",
        "FUEL CONSUMPTION": "fc_city",
        "HWY (L/100 km)": "fc_highway",
        "COMB (L/100 km)": "fc_mixed",
        "EMISSIONS": "emissions",
    }

    df: pl.LazyFrame = (
        pl.scan_csv(filepath).select(list(columns_name.keys())).rename(columns_name)
    )

    fuel_mapping = {
        "X": "Regular gasoline",
        "Z": "Premium gasoline",
        "D": "Diesel",
        "E": "Ethanol (E85)",
        "N": "Natural Gas",
    }

    df = df.with_columns(pl.col("fuel_type").replace(fuel_mapping))

    vehicle_class_category = {
        "Minivan": ["MINIVAN", "Minivan"],
        "Van": ["VAN - CARGO", "VAN - PASSENGER", "Van: Passenger"],
        "Subcompact": ["Subcompact", "SUBCOMPACT", "MINICOMPACT", "Minicompact"],
        "Compact": ["Compact", "COMPACT"],
        "Mid-size": ["Mid-size", "MID-SIZE"],
        "Full-size": ["Full-size", "FULL-SIZE"],
        "Station wagon": [
            "STATION WAGON - SMALL",
            "Station wagon: Small",
            "Station wagon: Mid-size",
            "STATION WAGON - MID-SIZE",
        ],
        "Two-seater": ["TWO-SEATER", "Two-seater"],
        "SUV": ["SUV - STANDARD", "SUV - SMALL", "SUV: Standard", "SUV: Small", "SUV"],
        "Pickup truck": [
            "PICKUP TRUCK - SMALL",
            "Pickup truck: Standard",
            "Pickup truck: Small",
            "PICKUP TRUCK - STANDARD",
        ],
        "Special purpose vehicle": [
            "Special purpose vehicle",
            "SPECIAL PURPOSE VEHICLE",
        ],
    }

    # Flatten and inverse the vehicle class mapping
    vehicle_class_mapping = {
        v: k for k, values in vehicle_class_category.items() for v in values
    }

    df = df.with_columns(pl.col("vehicle_class").replace(vehicle_class_mapping))

    transmission_mapping = {
        "A": "Automatic",
        "AM": "Automated manual",
        "AS": "Automatic with select shift",
        "AV": "Continuously variable",
        "M": "Manual",
    }

    df = df.with_columns(
        pl.col("transmission_info")
        .str.extract(r"([A-Z]+)")
        .replace(transmission_mapping)
        .alias("transmission_type"),
        pl.col("transmission_info").str.extract(r"(\d+)").cast(pl.Int32).alias("gears"),
    )

    # Ensure the DataFrame matches the CarDataSchema
    df = CarDataSchema.validate(df, cast=True)

    return df


def percentage_change(new_value: float, old_value: float) -> float:
    if old_value == 0:
        return float("N/A")
    return (new_value - old_value) / old_value


@st.cache_data
def load_model(filepath=MODEL_PATH):
    model = joblib.load(filepath)
    return model


if __name__ == "__main__":
    car_data = load_car_data(DATA_PATH)
    car_data.glimpse()

    model = load_model()
    print(model)
