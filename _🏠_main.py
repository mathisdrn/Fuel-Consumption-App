import streamlit as st
from streamlit_extras.mention import mention

st.set_page_config(
    page_title="FuelConsumption",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title("⛽︎ FuelConsumption")

mention(
    label="Mathis Derenne",
    icon="github",
    url="https://github.com/mathisdrn",
)

"""
---
**FuelConsumption** is a website where you can explore and visualise trends in car releases over time.

It focuses on the relation between **fuel type** and **vehicle class** with regard to **fuel efficiency** and **emissions**. 
It is based on [data](https://www.kaggle.com/datasets/ahmettyilmazz/fuel-consumption) that covers vehicles released in Canada 🇨🇦 from 2000 to 2022.

##### Features

- 📈 ‎ **dashboard** : display main metrics and charts
- 🚘 ‎ **vehicle finder** : find a car based on its characteristics
- 💯 ‎ **your car consumption** : estimate your car's emissions and fuel consumption based on its characteristics

##### Technologies

- **Python** (backend)
- **Streamlit** (frontend)
- **Polars** (data manipulation)
- **Altair** (data visualization)
"""
