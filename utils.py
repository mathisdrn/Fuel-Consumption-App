from pathlib import Path
import polars as pl
import pandera as pa
from pandera.typing import DataFrame
import streamlit as st
import joblib

MODEL_PATH = Path("data/lasso_regression.pkl")

class CarModelData(pa.DataFrameModel):
  release_year: int = pa.Field(coerce=True, gt=1999, lt=2050)
  vehicle_class: pl.Categorical = pa.Field(coerce=True)
  make: str = pa.Field(coerce=True)
  model: str = pa.Field(coerce=True)
  engine_size: float = pa.Field(coerce=True)
  cylinders: pl.Categorical = pa.Field(coerce=True)
  transmission_type: pl.Categorical = pa.Field(coerce=True)
  gears: int = pa.Field(coerce=True, nullable=True)
  fuel_type: pl.Categorical = pa.Field(coerce=True)
  fc_city: float = pa.Field(coerce=True)
  fc_highway: float = pa.Field(coerce=True)
  fc_mixed: float = pa.Field(coerce=True)
  emissions: int = pa.Field(coerce=True)


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
def load_car_data(filepath) -> DataFrame[CarModelData]:
  columns_name = {
    "YEAR": "release_year",
    "VEHICLE CLASS": "vehicle_class",
    "MAKE": "make",
    "MODEL": "model",
    "ENGINE SIZE": "engine_size",
    "CYLINDERS": "cylinders",
    "TRANSMISSION": "transmission_type",
    "FUEL": "fuel_type",
    "FUEL CONSUMPTION": "fc_city",
    "HWY (L/100 km)": "fc_highway",
    "COMB (L/100 km)": "fc_mixed",
    "EMISSIONS": "emissions",
  }

  fuel_mapping = {
    "X": "Regular gasoline",
    "Z": "Premium gasoline",
    "D": "Diesel",
    "E": "Ethanol (E85)",
    "N": "Natural Gas",
  }

  transmission_mapping = {
    "A": "Automatic",
    "AM": "Automated manual",
    "AS": "Automatic with select shift",
    "AV": "Continuously variable",
    "M": "Manual",
  }

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

  vehicle_class_mapping = {
    v: k for k, values in vehicle_class_category.items() for v in values
  }

  df = (
    pl.read_csv(filepath)
    .select(columns_name.keys())
    .rename(columns_name)
    .with_columns(
      [
        pl.col("fuel_type").replace(fuel_mapping),
        pl.col("vehicle_class").replace(vehicle_class_mapping),
        pl.col("transmission_type").str.extract(r"(\d+)$").cast(pl.Int32).alias("gears"),
        pl.col("transmission_type").str.replace(r"\d+", "").replace(transmission_mapping),
        pl.col("make").str.to_titlecase(),
        pl.col("model").str.to_titlecase(),
        ]
    )
    .select(list(CarModelData.__annotations__.keys()))
  )

  return df


# Allows caching between pages
def get_car_data() -> DataFrame[CarModelData]:
  if "car_data" not in st.session_state:
    st.session_state.car_data = load_car_data("data/fuel_consumption.csv")
  return st.session_state.car_data


def percentage_change(new_value, old_value):
  try:
    return (new_value - old_value) / old_value
  except ZeroDivisionError:
    return "N/A"


@st.cache_data
def load_model():
  model = joblib.load(MODEL_PATH)
  return model