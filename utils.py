from pathlib import Path
import pandas as pd
import pandera as pa
from pandera.typing import DataFrame
import streamlit as st
import pickle

class CarModelData(pa.DataFrameModel):
    release_year: int = pa.Field(coerce=True, gt=1999, lt=2050)
    vehicle_class: pd.CategoricalDtype = pa.Field(coerce=True)
    make: str = pa.Field(coerce=True)
    model: str = pa.Field(coerce=True)
    engine_size: float = pa.Field(coerce=True)
    cylinders: pd.CategoricalDtype = pa.Field(coerce=True)
    transmission_type: pd.CategoricalDtype = pa.Field(coerce=True)
    gears: pd.CategoricalDtype = pa.Field(coerce=True, nullable=True)
    fuel_type: pd.CategoricalDtype = pa.Field(coerce=True)
    fc_city: float = pa.Field(coerce=True)
    fc_highway: float = pa.Field(coerce=True)
    fc_mixed: float = pa.Field(coerce=True)
    emissions: int = pa.Field(coerce=True)
    
display_columns_name_mapping = {
    'release_year': 'Release year',
    'vehicle_class': 'Vehicle class',
    'make': 'Make',
    'model': 'Model',
    'engine_size': 'Engine size (L)',
    'cylinders': 'Cylinders',
    'transmission_type': 'Transmission',
    'gears': 'Gears',
    'fuel_type': 'Fuel Type',
    'fc_city': 'City (L/100 km)',
    'fc_highway': 'Highway (L/100 km)',
    'fc_mixed': 'Mixed (L/100 km)',
    'emissions': 'CO2 emissions (g/km)'
}

@st.cache_data
def load_data(filepath) -> DataFrame[CarModelData]:
    df = pd.read_csv(filepath)
    columns_name = {
        'YEAR': 'release_year', 
        'VEHICLE CLASS': 'vehicle_class',
        'MAKE': 'make', 
        'MODEL': 'model',
        'ENGINE SIZE': 'engine_size',
        'CYLINDERS': 'cylinders', 
        'TRANSMISSION': 'transmission_type',
        'FUEL': 'fuel_type',
        'FUEL CONSUMPTION': 'fc_city',
        'HWY (L/100 km)': 'fc_highway', 
        'COMB (L/100 km)': 'fc_mixed', 
        'EMISSIONS': 'emissions'
    }

    df = df[columns_name.keys()]
    df = df.rename(columns=columns_name)
    
    # Map fuel type to name
    fuel_mapping = {
        'X': 'Regular gasoline', 
        'Z': 'Premium gasoline', 
        'D': 'Diesel', 
        'E': 'Ethanol (E85)', 
        'N': 'Natural Gas'
    }
    df['fuel_type'] = df['fuel_type'].map(fuel_mapping)
    
    # Extract transmission digits as number of gears
    df['gears'] = df['transmission_type'].str.extract(r'(\d+)$')
    df['gears'] = pd.to_numeric(df['gears'], errors='coerce')
    # Remove digits from transmission column
    df['transmission_type'] = df['transmission_type'].str.replace(r'\d+$', '', regex=True)
    # Map transmission type to name
    transmission_mapping = {
        'A': 'Automatic',
        'AM': 'Automated manual',
        'AS': 'Automatic with select shift',
        'AV': 'Continuously variable',
        'M': 'Manual'
    }
    df['transmission_type'] = df['transmission_type'].map(transmission_mapping)
    
    # Format string columns
    df['make'] = df['make'].str.title()
    df['vehicle_class'] = df['vehicle_class'].str.capitalize()
    
    # Remove vehicle class size details
    df['vehicle_class'] = df['vehicle_class'].str.replace(r' - .+|: .+', '', regex=True)

    # Reorder columns
    df = df[CarModelData.__annotations__.keys()]
    
    return df

def percentage_change(new_value, old_value):
    try:
        return (new_value - old_value) / old_value
    except ZeroDivisionError:
        return "N/A"
    
@st.cache_data
def load_model():
    model = pickle.load(open('data/lasso_regression.pkl', 'rb'))
    return model