import hashlib
import pickle
import re
from datetime import datetime, time
from pathlib import Path
from typing import Any

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
    return pl.read_parquet(Path(folder_path) / "car_data.parquet")


@st.cache_data
def load_model(folder_path: str | Path = DATA_PATH) -> Pipeline:
    """Load the trained scikit-learn Pipeline model from a pickle file."""
    model_path = Path(folder_path) / "lasso_regression.pkl"

    with model_path.open("rb") as f:
        return pickle.load(f)  # noqa: S301 deserialization is safe here


def percentage_change(new_value: float, old_value: float) -> float:
    if old_value == 0:
        return float("N/A")
    return (new_value - old_value) / old_value


def _multiselect_options(df: pl.DataFrame, column: str) -> list[Any]:
    return df.get_column(column).drop_nulls().unique().sort().to_list()


def _default_slider_step(min_value: int | float, max_value: int | float) -> int | float:
    if isinstance(min_value, int) and isinstance(max_value, int):
        return max((max_value - min_value) // 100, 1)

    step = (float(max_value) - float(min_value)) / 100
    return step if step > 0 else 0.01


def _default_key_prefix(df: pl.DataFrame, available_columns: list[str]) -> str:
    schema_signature = tuple((name, repr(dtype)) for name, dtype in df.schema.items())
    key_material = repr((tuple(available_columns), schema_signature)).encode()
    return hashlib.md5(key_material, usedforsecurity=False).hexdigest()


def dataframe_explorer(
    df: pl.DataFrame,
    case_sensitive: bool = True,
    excluded_columns: list[str] | None = None,
    key_prefix: str | None = None,
) -> pl.DataFrame:
    """Add Streamlit controls to filter a Polars dataframe by selected columns."""
    filtered_df = df
    available_columns = [
        column
        for column in filtered_df.columns
        if column not in (excluded_columns or [])
    ]
    widget_key_base = key_prefix or _default_key_prefix(filtered_df, available_columns)

    with st.container():
        selected_columns = st.multiselect(
            "Filter dataframe on",
            available_columns,
            key=f"{widget_key_base}_multiselect",
        )

        for column in selected_columns:
            left, right = st.columns((1, 20))
            column_series = filtered_df.get_column(column)
            dtype = filtered_df.schema[column]

            # Streamlit filter widgets need at least one non-null value to render safely.
            if (
                column_series.is_empty()
                or column_series.null_count() == column_series.len()
            ):
                left.write("↳")
                right.caption(f"No values left for {column} after the current filters.")
                continue

            if dtype == pl.Categorical or column_series.n_unique() < 10:
                left.write("↳")
                options = _multiselect_options(filtered_df, column)
                selected_values = right.multiselect(
                    f"Values for {column}",
                    options,
                    default=options,
                    key=f"{widget_key_base}_{column}",
                )
                filtered_df = filtered_df.filter(pl.col(column).is_in(selected_values))
            elif dtype.is_numeric():
                left.write("↳")
                min_value = column_series.min()
                max_value = column_series.max()

                if min_value == max_value:
                    selected_values = right.multiselect(
                        f"Values for {column}",
                        [min_value],
                        default=[min_value],
                        key=f"{widget_key_base}_{column}",
                    )
                    filtered_df = filtered_df.filter(
                        pl.col(column).is_in(selected_values)
                    )
                    continue

                selected_range = right.slider(
                    f"Values for {column}",
                    min_value=min_value,
                    max_value=max_value,
                    value=(min_value, max_value),
                    step=_default_slider_step(min_value, max_value),
                    key=f"{widget_key_base}_{column}",
                )
                filtered_df = filtered_df.filter(
                    pl.col(column).is_between(*selected_range)
                )
            elif dtype in (pl.Date, pl.Datetime):
                left.write("↳")
                min_value = column_series.min()
                max_value = column_series.max()
                selected_dates = right.date_input(
                    f"Values for {column}",
                    value=(min_value, max_value),
                    key=f"{widget_key_base}_{column}",
                )

                if len(selected_dates) != 2:
                    continue

                start_date, end_date = selected_dates
                if dtype == pl.Datetime:
                    start_value = datetime.combine(start_date, time.min)
                    end_value = datetime.combine(end_date, time.max)
                else:
                    start_value = start_date
                    end_value = end_date

                filtered_df = filtered_df.filter(
                    pl.col(column).is_between(start_value, end_value)
                )
            else:
                left.write("↳")
                search_pattern = right.text_input(
                    f"Pattern in {column}",
                    key=f"{widget_key_base}_{column}",
                )

                if search_pattern:
                    pattern = (
                        search_pattern
                        if case_sensitive
                        else f"(?i){re.escape(search_pattern)}"
                    )
                    filtered_df = filtered_df.filter(
                        pl.col(column)
                        .cast(pl.String)
                        .fill_null("")
                        .str.contains(pattern, literal=case_sensitive)
                    )

    return filtered_df
