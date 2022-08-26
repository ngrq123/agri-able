import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
     page_title="ASDI",
     page_icon="🧊",
     layout="wide",
     initial_sidebar_state="expanded",

)

# calling all the data
d = pd.read_csv ("crop_attributes.csv")
crop_attribute_df = pd.DataFrame(data=d)

isdasoil_df = pd.read_csv("sample_isdasoil_data.csv")
isdasoil_df = pd.DataFrame(data=isdasoil_df)

st.header("Properties based on the location you selected: ")

st.write(isdasoil_df)

#getting averages of soil table
soil_nitro_avg = isdasoil_df["Soil Nitrogen"].mean()
soil_phos_avg = isdasoil_df["Soil Phosphorous"].mean()
soil_pota_avg = isdasoil_df["Soil Potassium"].mean()
soil_pH = isdasoil_df["Soil pH"].mean()
fcc_med = isdasoil_df["Fertility Capability Classification"].median()


#this function converts the FCC score to the soil attributes
def fcc_conversion(score):
    num_to_text = {
        4: 'Slope',
        36: 'Slope, High erosion risk - steep slope',
        132: 'Slope, Al toxicity',
        164: 'Slope, High erosion risk - steep slope, Al toxicity',
        512: 'Low K',
        516: 'Slope, Low K',
        548: 'Slope, High erosion risk - steep slope, Low K',
        640: 'Al toxicity, Low K',
        644: 'Slope, Al toxicity, Low K',
        676: 'Slope, High erosion risk - steep slope, Al toxicity, Low K'}

    value = num_to_text[score]
    return value

st.write("below shows the average of the soil information")
st.write("nitrogen:", soil_nitro_avg)
st.write("phosphorous:", soil_phos_avg)
st.write("potassium:", soil_pota_avg)
st.write("pH:", soil_pH)
st.write("soil properties based on fcc:", fcc_conversion(fcc_med))

st.header("Crop Recommender")


st.write(crop_attribute_df)


#below appends a list of  crops that meets falls within the range of min max
st.subheader("potassium")
potassium_checker = (soil_pota_avg >= crop_attribute_df["min_potassium"]) & (soil_pota_avg <= crop_attribute_df["max_potassium"])
pota = crop_attribute_df.loc[potassium_checker, "Crop"].tolist()
st.write(pota)

#we need to check this
st.subheader("phosphorus")
phosphorus_checker = (soil_phos_avg >= crop_attribute_df["min_phosphorus"]) & (soil_phos_avg <= crop_attribute_df["max_phosphorus"])
pho = crop_attribute_df.loc[phosphorus_checker, "Crop"].tolist()
st.write(pho)

st.subheader("pH")
ph_checker = (soil_pH >= crop_attribute_df["min_ph_soil"]) & (soil_pH <= crop_attribute_df["max_ph_soil"])
ph = crop_attribute_df.loc[ph_checker, "Crop"].tolist()
st.write(ph)



# FORM code (in case we need it alter)

# with st.form("my_form"):
#     st.write("Enter the following details to get a recommendation:")
#     soil_ph = st.number_input('Enter the soil PH', key=1)
#     potassium = st.number_input('Enter the potassium level', key=2)
#     nitrogen = st.number_input('Enter the nitrogen level', key=3)

#     submitted = st.form_submit_button("Submit your crop information")
#     if submitted:
#         st.write("soil ph -", soil_ph)
#         st.write("potassium -", potassium)
#         st.write("nitrogen -", nitrogen)


# Sushil's code

# Now this will show the filtered row in the dataframe as you change the inputs

# min_ph_soil = st.selectbox('Min PH', crop_attribute_df['min_ph_soil'].unique())
# max_ph_soil = st.selectbox('Max PH', crop_attribute_df['max_ph_soil'].unique())



# newDF = (crop_attribute_df[crop_attribute_df['min_ph_soil'] >= min_ph_soil])


# st.write(newDF[newDF['max_ph_soil'] <= max_ph_soil])
