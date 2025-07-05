import streamlit as st
import polars as pl
import altair as alt
from utils import get_car_data, percentage_change

st.set_page_config(
    page_title="Fuel consumption - Dashboard", page_icon="📈", layout="wide"
)

st.title("📈 Dashboard")

df = get_car_data()

# -------------- Metric --------------

# Group by year and calculate the required metrics
metrics = (
    df.group_by("release_year")
    .agg(
        [
            pl.col("make").count().alias("model_count"),
            pl.col("fc_mixed").mean().alias("fc_mixed"),
            pl.col("emissions").mean().alias("emissions"),
        ]
    )
    .sort("release_year", descending=True)
)

# Display metrics
st.header("Overview - Year on Year")

col1, col2, col3 = st.columns(3)

col1.metric(
    label="Number of models",
    value=f"{metrics[0, 'model_count']:.0f}",
    delta=f"{percentage_change(metrics[0, 'model_count'], metrics[1, 'model_count']):.1%}",
)

col2.metric(
    label="Mixed consumption (L/100km)",
    value=f"{metrics[0, 'fc_mixed']:.1f} L",
    delta=f"{metrics[0, 'fc_mixed'] - metrics[1, 'fc_mixed']:.2f} L",
    delta_color="inverse",
)

col3.metric(
    label="Vehicle emissions",
    value=f"{metrics[0, 'emissions']:.0f} g/km",
    delta=f"{percentage_change(metrics[0, 'emissions'], metrics[1, 'emissions']):.2%}",
    delta_color="inverse",
)

# ------------- Plotting -------------

# Model count over time
temp = df.group_by("release_year").agg([pl.col("make").count().alias("model_count")])

chart = (
    alt.Chart(temp)
    .mark_line()
    .encode(
        x=alt.X(
            "release_year:O",
            title="Year",
            axis=alt.Axis(labelAngle=0, values=temp["release_year"].unique()[::2]),
        ),
        y=alt.Y("model_count:Q", title="Number of models"),
        tooltip=[
            alt.Tooltip("release_year:O", title="Year"),
            alt.Tooltip("model_count:Q", title="Number of models"),
        ],
    )
    .properties(title="Number of models released over time")
)
st.altair_chart(chart, use_container_width=True)

# Proportion of vehicle class over time
temp = (
    df.group_by(["release_year", "vehicle_class"])
    .agg([pl.col("make").count().alias("model_count")])
    .with_columns(
        [
            (
                pl.col("model_count") / pl.col("model_count").sum().over("release_year")
            ).alias("proportion")
        ]
    )
)

chart = (
    alt.Chart(temp)
    .mark_area()
    .encode(
        x=alt.X(
            "release_year:O",
            title="Year",
            axis=alt.Axis(labelAngle=0, values=temp["release_year"].unique()[::2]),
        ),
        y=alt.Y(
            "proportion:Q",
            title="Proportion of Vehicle Class",
            axis=alt.Axis(format="%"),
        ),
        color=alt.Color("vehicle_class:N", title="Vehicle Class"),
        tooltip=[
            alt.Tooltip("release_year:O", title="Year"),
            alt.Tooltip("vehicle_class:N", title="Vehicle Class"),
            alt.Tooltip("proportion:Q", title="Proportion", format=".2%"),
        ],
    )
    .properties(title="Vehicle Class Proportion Over Time")
)
st.altair_chart(chart, use_container_width=True)

# Proportion of vehicle fuel type over time
temp = (
    df.group_by(["release_year", "fuel_type"])
    .agg([pl.col("make").count().alias("model_count")])
    .with_columns(
        [
            (
                pl.col("model_count") / pl.col("model_count").sum().over("release_year")
            ).alias("proportion")
        ]
    )
)

chart_fuel = (
    alt.Chart(temp)
    .mark_bar()
    .encode(
        x=alt.X(
            "release_year:O",
            title="Year",
            axis=alt.Axis(labelAngle=0, values=temp["release_year"].unique()[::2]),
        ),
        y=alt.Y(
            "proportion:Q", title="Percentage of Fuel Type", axis=alt.Axis(format="%")
        ),
        color=alt.Color("fuel_type:N", title="Fuel Type"),
        tooltip=[
            alt.Tooltip("release_year:O", title="Year"),
            alt.Tooltip("fuel_type:N", title="Fuel Type"),
            alt.Tooltip("proportion:Q", title="Percentage", format=".2%"),
        ],
    )
    .properties(title="Vehicle Fuel Type Proportion Over Time")
)
st.altair_chart(chart_fuel, use_container_width=True)

# Fuel type proportion versus vehicle type
temp = (
    df.group_by(["vehicle_class", "fuel_type"])
    .agg([pl.col("make").count().alias("model_count")])
    .with_columns(
        [
            (
                pl.col("model_count")
                / pl.col("model_count").sum().over("vehicle_class")
            ).alias("proportion")
        ]
    )
)

# Order vehicle classes by model count
order = (
    df.group_by("vehicle_class")
    .agg([pl.col("make").count().alias("model_count")])
    .sort("model_count", descending=True)["vehicle_class"]
    .to_list()
)

chart_fuel = (
    alt.Chart(temp)
    .mark_bar()
    .encode(
        x=alt.X(
            "proportion:Q", title="Fuel Type Proportion", axis=alt.Axis(format="%")
        ),
        y=alt.Y("vehicle_class:O", sort=order, title=None),
        color=alt.Color("fuel_type:N", title="Fuel Type"),
        tooltip=[
            alt.Tooltip("vehicle_class:O", title="Vehicle Type"),
            alt.Tooltip("fuel_type:N", title="Fuel Type"),
            alt.Tooltip("proportion:Q", title="Percentage", format=".2%"),
        ],
    )
    .properties(title="Fuel Type Proportion versus Vehicle Type")
)
st.altair_chart(chart_fuel, use_container_width=True)

st.markdown("### Vehicle emissions")

# Vehicle emissions over time for a specific fuel type
fuel_type = st.selectbox("Select a fuel type", df["fuel_type"].unique(), index=0)

temp = (
    df.filter(pl.col("fuel_type") == fuel_type)
    .group_by(["release_year", "vehicle_class"])
    .agg([pl.col("emissions").mean().alias("emissions")])
)

chart_emissions = (
    alt.Chart(temp)
    .mark_line()
    .encode(
        x=alt.X(
            "release_year:O",
            title="Year",
            axis=alt.Axis(labelAngle=0, values=temp["release_year"].unique()[::2]),
        ),
        y=alt.Y("emissions:Q", title="Emissions (g/km)"),
        color=alt.Color("vehicle_class:N", title="Vehicle Type"),
        tooltip=[
            alt.Tooltip("release_year:O", title="Year"),
            alt.Tooltip("vehicle_class:N", title="Vehicle Type"),
            alt.Tooltip("emissions:Q", title="Emissions (g/km)", format=".2f"),
        ],
    )
    .properties(title=f"Average Emissions by Vehicle Type for {fuel_type}")
)
st.altair_chart(chart_emissions, use_container_width=True)

# Vehicle emissions over time for a specific vehicle class
vehicle_class = st.selectbox(
    "Select a vehicle type", df["vehicle_class"].unique(), index=0
)

temp = (
    df.filter(pl.col("vehicle_class") == vehicle_class)
    .group_by(["release_year", "fuel_type"])
    .agg([pl.col("emissions").mean().alias("emissions")])
)

chart_emissions = (
    alt.Chart(temp)
    .mark_line()
    .encode(
        x=alt.X(
            "release_year:O",
            title="Year",
            axis=alt.Axis(labelAngle=0, values=temp["release_year"].unique()[::2]),
        ),
        y=alt.Y("emissions:Q", title="Emissions (g/km)"),
        color=alt.Color("fuel_type:N", title="Fuel Type"),
        tooltip=[
            alt.Tooltip("release_year:O", title="Year"),
            alt.Tooltip("fuel_type:N", title="Fuel Type"),
            alt.Tooltip("emissions:Q", title="Emissions (g/km)", format=".2f"),
        ],
    )
    .properties(title=f"Average Emissions by Fuel Type for {vehicle_class}")
)
st.altair_chart(chart_emissions, use_container_width=True)
