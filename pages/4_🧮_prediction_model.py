import streamlit as st
import pandas as pd
import numpy as np

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
            
st.info("""Note : best model is already saved and ready to use. It's not useful to execute without any additional data.""", icon = 'ℹ️')
st.warning("There are about 17 000 rows in the dataset. The training of RandomForestRegressor with 20 set of parameters that are cross validated 5 times takes 100 fittings of the 89 columns of the data to get result of training. Execution may take some times (≈ 5 minutes)", icon = '⚠️')

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
        ('lasso', Lasso())]
        , memory = cachedir)

    return pipeline

from sklearn.model_selection import GridSearchCV

from tempfile import mkdtemp
cachedir = mkdtemp()

def execute_pipeline(pipeline, X, Y):
    param = {
        'lasso__alpha': np.geomspace(0.00001, 5, 10),
    }
    
    grid = GridSearchCV(pipeline, param_grid = param, cv=5, verbose=2, n_jobs=-1, scoring = 'r2', refit = True)

    
    with st.spinner('This may take up to a minute...'):
        grid.fit(X, Y)
    return grid

def result(grid):
    st.success(f"""**Fitting completed :**""", icon = '✅')
    st.markdown(f"""
Best parameter is {grid.best_params_}

R2 score of **{round(grid.best_score_, 3)}**

> Interpretation : the model is able to explain {round(grid.best_score_ * 100)}% of the variance in the data. 
""")

import joblib

def save_model(grid):
    best_model = grid.best_estimator_
    st.write('#### Saving model')
    joblib.dump(best_model, 'prediction_model.pkl')
    st.success('Best Model saved', icon = '✅')

if st.button('Run the training of models'):
    st.markdown('### Loading data')
    X, Y = load_data()

    st.markdown('### Building pipeline')
    pipeline = create_pipeline(X)
    st.info("""
A complex pipeline with multiple regressors have been used. A r2 score of 85% was achieved by RandomForestRegressor.
However some constraint came with it : 
- long computation time (> 20 minutes)
- the export of the model was over 500 Mo
The notebooks for this model can be found in the repository but the version implemented here is using Lasso and is tuned by GridSearchCV over 10 parameters by 5 cross validation.
""")

    st.markdown('### Training model : Lasso')
    grid = execute_pipeline(pipeline, X, Y)
    result(grid)
    save_model(grid)