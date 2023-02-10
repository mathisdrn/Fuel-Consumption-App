import streamlit as st
import pandas as pd
import numpy as np
import time

st.set_page_config(
    page_title="🧮 Prediction model",
    page_icon="🧮",
    layout="centered",
    initial_sidebar_state="auto",
)

st.title('🧮 Prediction model')
st.markdown("""
**Target :** Fuel consumption (Combined, City, Highway), CO2 emissions (g/km)

**Features :**

    Vehicle class
    Make
    Release year
    Engine size (L)
    Cylinders
    Transmission
    Fuel type
""")
            
st.info("""Note : best model is already saved and ready to use. It's not needed to execute without any additional data.""", icon = 'ℹ️')
def load_data():
    df = pd.read_csv('data/fuel_consumption.csv', parse_dates=['YEAR'])
    # Change Type of fuel to name
    df['FUEL'] = df['FUEL'].replace({'X': 'Regular gasoline', 'Z': 'Premium gasoline', 'D': 'Diesel', 'E': 'Ethanol (E85)', 'N': 'Natural Gas'})
    # Extract last caracter of transmission as number of gears
    # ie. 816 cars have continuous variable transmission and don't have a number of gears
    df['GEARS'] = df['TRANSMISSION'].str.extract(r'(\d+)$', expand=False)
    df['TRANSMISSION'] = df['TRANSMISSION'].str.replace(r'\d+$', '')
    df['TRANSMISSION'] = df['TRANSMISSION'].replace({'A': 'Automatic', 'AM': 'Automated manual', 'AS': 'Automatic with select shift', 'AV': 'Continuously variable', 'M': 'Manual'})
    # Rename FUEL CONSUMPTION to CITY (L/100 km)
    df = df.drop(columns=['COMB (mpg)'], axis = 1)
    df = df.rename(columns={'FUEL CONSUMPTION': 'CITY (L/100 km)'})
    df['MAKE'] = df['MAKE'].str.capitalize()

    # Uniformize vehicle class
    df['VEHICLE CLASS'] = df['VEHICLE CLASS'].str.capitalize()
    df.loc[df['VEHICLE CLASS'].str.contains('Pickup truck'), 'VEHICLE CLASS'] = 'Pickup truck'
    df.loc[df['VEHICLE CLASS'].str.contains('Station wagon'), 'VEHICLE CLASS'] = 'Station wagon'
    df.loc[df['VEHICLE CLASS'].str.contains('Suv'), 'VEHICLE CLASS'] = 'SUV'
    df.loc[df['VEHICLE CLASS'].str.contains('Van'), 'VEHICLE CLASS'] = 'Van'

    # rename YEAR, VEHICLE CLASS, MAKE, MODEL, ENGINE SIZE, CYLINDERS, TRANSMISSION, FUEL, CITY (L/100 km), HWY (L/100 km), COMB (L/100 km), CO2 EMISSIONS (g/km)
    df = df.rename(columns={'YEAR': 'Release year', 'GEARS' : 'Gears', 'VEHICLE CLASS': 'Vehicle class', 'MAKE': 'Make', 'MODEL': 'Model', 'ENGINE SIZE': 'Engine size (L)', 'CYLINDERS': 'Cylinders', 'TRANSMISSION': 'Transmission', 'FUEL': 'Fuel', 'CITY (L/100 km)': 'City (L/100 km)', 'COMB (L/100 km)': 'Mixed consumption (L/100 km)', 'HWY (L/100 km)': 'Highway (L/100 km)', 'EMISSIONS': 'CO2 emissions (g/km)'})
    df['Release year'] = df['Release year'].dt.year
    # Target - Features
    X = df[['Make', 'Release year', 'Vehicle class', 'Fuel', 'Transmission', 'Gears', 'Engine size (L)', 'Cylinders']]
    Y = df[['CO2 emissions (g/km)', 'Mixed consumption (L/100 km)', 'City (L/100 km)', 'Highway (L/100 km)']]

    st.write(f'The dataset contain {X.shape[0]} rows.')
    return X, Y

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from sklearn.linear_model import Lasso
from sklearn.model_selection import GridSearchCV

def create_pipeline(X):
    numerical = X.select_dtypes(include=['int64', 'float64']).columns.values.tolist()
    categorical = X.select_dtypes(include=['object']).columns.values.tolist()

    preprocessor = ColumnTransformer(
    transformers = [
        ('categorical', OneHotEncoder(handle_unknown='ignore'), categorical),
        ('numerical', StandardScaler(), numerical)
        ])
    
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('lasso', Lasso(max_iter = 3000))])

    return pipeline

def execute_pipeline(pipeline, X, Y):
    param = {
        'lasso__alpha': np.geomspace(0.00001, 1, 5),
    }
    
    grid = GridSearchCV(pipeline, param_grid = param, cv=3, verbose=2, n_jobs=-1, scoring = 'r2', refit = True)

    # time
    start = time.time()
    with st.spinner('This may take up to a minute...'):
        grid.fit(X, Y)
    end = time.time()
    st.success(f"""Fitting completed - Time elapsed : {round(end - start)} seconds.""", icon = '✅')
    return grid

def result(grid):
    st.markdown(f"""
Best parameter is {grid.best_params_}

R2 score of **{round(grid.best_score_, 2)}**

> Interpretation : the model is able to explain {round(grid.best_score_ * 100)}% of the variance in the data. 
""")

import joblib

def save_model(grid):
    best_model = grid.best_estimator_
    st.write('#### Saving model')
    # joblib.dump(best_model, 'prediction_model.pkl')
    st.success('Best Model saved', icon = '✅')


if st.button('Run the training of models'):
    st.markdown('### Loading data')
    X, Y = load_data()

    st.markdown('### Building pipeline')
    pipeline = create_pipeline(X)
    st.warning("""
A complex pipeline with multiple regressors was previously implemented. A R2 Score of 85 % was achieved by RandomForestRegressor.
However some constraint came with it :
- fitting several models, in average 100 times, on 22 000 rows and 89 columns took a long time (> 30 minutes)
- the size of the model was over 500 Mo and could no longer be loaded in 'your car consumption' .

While Streamlit can certainly handle the training of complex models, the application and public destined for this project do no justify such implementation.
This page rather intend to present a real time generic example of the process of training a model as well as a proof of concept that Streamlit can host complete data science project from displaying Dashboard, querying data from a server and retraining models within an appreciable UI.
""", icon = '⚠️')

    st.info("""
The lighter version implemented here uses Lasso regressor and is tuned by GridSearchCV over 5 parameters by 3 cross validation (15 fits).

The computationally intensive pipelines can be found in the repository of this Project.
""")

    st.markdown('### Training model : Lasso')
    grid = execute_pipeline(pipeline, X, Y)
    result(grid)
    save_model(grid)