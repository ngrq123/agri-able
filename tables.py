import streamlit as st
import pandas as pd

st.write ("""
# Table Recommender
""")

d = pd.read_csv ("crop_attributes.csv")
df = pd.DataFrame(data=d)

# a = st.slider('sidebar for testing', 5, 10, 9)

# df['result'] = df['data'] + a
# st.write(df)

# Now this will show the filtered row in the dataframe as you change the inputs
min_ph_soil = st.selectbox('Min PH', df['min_ph_soil'].unique())


newDF = (df[df['min_ph_soil'] >= min_ph_soil])

max_ph_soil = st.selectbox('Max PH', df['max_ph_soil'].unique())

st.write(newDF[newDF['max_ph_soil'] <= max_ph_soil])
