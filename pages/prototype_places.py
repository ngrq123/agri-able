import pandas as pd
import streamlit as st

import utils.functions as functions

point = st.session_state['default_point']

if 'selected_point' in st.session_state:
    point = st.session_state['selected_point']

res = functions.reverse_geocode(point)
selected_country_code = res['address']['country_code']

countries_df = pd.read_csv('./data/africa_countries.csv')
selected_country = countries_df.loc[countries_df['Alpha-2 code'] \
    .str.lower() == selected_country_code] \
    ['Country'].values[0]

st.header('List of Farming Supplies in ' + selected_country)

df = pd.read_csv('./data/farming_supplies_places.csv')
print(df['Country'].values[0], '|', selected_country)
filtered_df = df.loc[df['Country'] == selected_country]

if filtered_df.shape[0] > 0:
    st.dataframe(filtered_df)
else:
    st.markdown('No places with farming supplies found in ' + selected_country + '. Do check with your local communities.')