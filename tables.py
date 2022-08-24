import streamlit as st
import pandas as pd

st.set_page_config(
     page_title="ASDI",
     page_icon="🧊",
     layout="wide",
     initial_sidebar_state="expanded",
     
 )

st.write ("""
# Recommender
""")

d = pd.read_csv ("crop_attributes.csv")
df = pd.DataFrame(data=d)

# a = st.slider('sidebar for testing', 5, 10, 9)

# df['result'] = df['data'] + a
# st.write(df)

# Now this will show the filtered row in the dataframe as you change the inputs

with st.form("my_form"):
    st.write("Enter your soil details to get a recommendation:")
    soil_ph = st.number_input('Enter the soil PH', key=1)
    potassium = st.number_input('Enter the potassium level', key=2)
    nitrogen = st.number_input('Enter the nitrogen level', key=3)




    submitted = st.form_submit_button("Submit your crop information")
    if submitted:
        st.write("soil ph -", soil_ph)
        st.write("potassium -", potassium)
        st.write("nitrogen -", nitrogen)


min_ph_soil = st.selectbox('Min PH', df['min_ph_soil'].unique())
max_ph_soil = st.selectbox('Max PH', df['max_ph_soil'].unique())




newDF = (df[df['min_ph_soil'] >= min_ph_soil])


st.write(newDF[newDF['max_ph_soil'] <= max_ph_soil])
