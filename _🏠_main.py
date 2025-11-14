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
**FuelConsumption** data is based on of vehicles released in Canada 🇨🇦 between 1995 to 2024 ([source](https://open.canada.ca/data/en/dataset/98f1a129-f628-4ce4-b24d-6f16bf24dd64)). 

It contains: 

- 📈 ‎ **a dashboard** that let you see key metrics and trends
- 🚘 ‎ **a vehicle finder** to find cars based on their characteristics
- 💯 ‎ **an estimator of a car consumption and emissions** based on their characteristics

--- 

##### Technical stack

- **Python** (backend)
- **Streamlit** (frontend)
- **Polars** (data manipulation)
- **Altair** (data visualization)
"""
