import pandas as pd
import streamlit as st

df = pd.read_csv('./data/farming_supplies_places.csv')
st.dataframe(df)