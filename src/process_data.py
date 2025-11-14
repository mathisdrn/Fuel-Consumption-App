from pathlib import Path

import polars as pl

# Data taken from https://open.canada.ca/data/en/dataset/98f1a129-f628-4ce4-b24d-6f16bf24dd64

file1 = Path("./data/raw/1995-2014-car-data.csv")
file2 = Path("./data/raw/2015-2024-car-data.csv")

df1 = pl.read_csv(file1)
df2 = pl.read_csv(file2)

df = pl.concat([df1, df2], how="vertical")

columns_name = {
    "Model year": "release_year",
    "Vehicle class": "vehicle_class",
    "Make": "make",
    "Model": "model",
    "Engine size (L)": "engine_size",
    "Cylinders": "cylinders",
    "Transmission": "transmission_info",
    "Fuel type": "fuel_type",
    "City (L/100 km)": "fc_city",
    "Highway (L/100 km)": "fc_highway",
    "Combined (L/100 km)": "fc_mixed",
    "CO2 emissions (g/km)": "emissions",
}

df = df.select(list(columns_name.keys())).rename(columns_name)

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
    "Van": ["VAN - CARGO", "VAN - PASSENGER", "Van: Passenger", "Van: Cargo"],
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
    "SUV": [
        "SUV - STANDARD",
        "SUV - SMALL",
        "SUV: Standard",
        "SUV: Small",
        "SUV",
        "Sport utility vehicle: Small",
        "Sport utility vehicle: Standard",
        "Sport utility vehicle",
    ],
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
    pl.col("transmission_info").str.extract(r"(\d+)").cast(pl.Int32).alias("gears"),
    pl.col("transmission_info")
    .str.extract(r"([A-Z]+)")
    .replace(transmission_mapping)
    .alias("transmission_type"),
).drop("transmission_info")

df = df.select(
    [
        "release_year",
        "make",
        "model",
        "vehicle_class",
        "fuel_type",
        "engine_size",
        "cylinders",
        "transmission_type",
        "gears",
        "fc_city",
        "fc_highway",
        "fc_mixed",
        "emissions",
    ]
).sort(["release_year", "make", "model", "vehicle_class"])

df.write_parquet(Path("./data/car_data.parquet"))
