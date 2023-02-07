import streamlit as st

st.set_page_config(
    page_title="⛽︎ Fuel consumption",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="auto",
)

st.title('⛽︎ Fuel consumption')
st.markdown("""
Author : Mathis Derenne (https://github.com/mathisdrn)

---
""")
st.header('Project description')
st.markdown("""
This project aims at providing a deeper understanding of how caractheristic of a car impact fuel consumption.

### Components :
- dashboard : display main metrics and charts
- model training : train a model to predict the fuel consumption of a car based on existing pool of cars
- prediction : predict the fuel consumption of a car based on its characteristics

### About the data :

**Source** : https://www.kaggle.com/datasets/ahmettyilmazz/fuel-consumption

**Description** :
> Datasets provide model-specific fuel consumption ratings and estimated carbon dioxide emissions for new light-duty vehicles for retail sale in Canada 🇨🇦.
>
> To help you compare vehicles from different model years, the fuel consumption ratings for 2000 to 2022 vehicles have been adjusted to reflect the improved testing that is more representative of everyday driving. Note that these are approximate values that were generated from the original ratings, not from vehicle testing.
""")
