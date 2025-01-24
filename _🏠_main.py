import streamlit as st
from streamlit_extras.mention import mention 

st.set_page_config(
    page_title="Fuel consumption",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title('⛽︎ Fuel consumption')

mention(
    label="Mathis Derenne",
    icon="github",
    url="https://github.com/mathisdrn",
)

st.markdown("""
### Project description            
            
The **FuelConsumptionApp** provides you with tools and visual to help you understand trends in vehicle release.
It is based on [data](https://www.kaggle.com/datasets/ahmettyilmazz/fuel-consumption) about vehicle's characteristic, consumptions and emissions of vehicle released in Canada 🇨🇦 between 2000 to 2022.
Fuel consumption ratings have been adjusted to reflect the improved testing that is more representative of everyday driving. 

##### Pages

- 📈 ‎ **dashboard** : display main metrics and charts
- 🚘 ‎ **vehicle finder** : find a car based on its characteristics
- 💯 ‎ **your car consumption** : estimate your car's emissions and fuel consumption based on its characteristics

##### Technologies

- **Python** (backend)
- **Streamlit** (frontend)
- **Polars** (data manipulation)
- **Altair** (data visualization)
""")
