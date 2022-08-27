import streamlit as st
import pandas as pd
import numpy as np
from streamlit_option_menu import option_menu
import streamlit.components.v1 as html

# Page 1: Settings Page
# Page 2: Descriptive Views, FCC constraints, plot distribution of the number of constraints
# Page 3: based on the number of constraints, figure out which ones are modifiable --> if modifable, re-calcaulte the percentage of land with constraints (as-is and to-be)


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

#splicing out fcc cols for further calculation
new_df = isdasoil_df.iloc[:, 8:]
new_df = new_df.drop('fcc_no_constraints',axis=1)
list_of_cols = list(new_df.columns)

def cal_no_constraints(df):
    # calculates the % of land with no constraints
    filtered_df = isdasoil_df.loc[(isdasoil_df['fcc_al_toxicity'] == 0) 
                                & (isdasoil_df['fcc_calcareous'] == 0)
                                & (isdasoil_df['fcc_gravelly'] == 0)
                                & (isdasoil_df['fcc_high_erosion_risk_-_shallow_depth'] == 0)
                                & (isdasoil_df['fcc_high_erosion_risk_-_steep_slope'] == 0)
                                & (isdasoil_df['fcc_high_erosion_risk_-_textual_contrast'] == 0)
                                & (isdasoil_df['fcc_high_leaching_potential'] == 0)
                                & (isdasoil_df['fcc_low_k'] == 0)
                                & (isdasoil_df['fcc_no_data'] == 0)
                                & (isdasoil_df['fcc_shallow'] == 0)
                                & (isdasoil_df['fcc_slope'] == 0)
                                & (isdasoil_df['fcc_sulfidic'] == 0)
                            ]
    filtered_len = len(filtered_df)
    total_rows = len(isdasoil_df)
    no_constraints_percent = (filtered_len/total_rows) * 100

    return no_constraints_percent

st.header("Percentage of Land with no constraints")
st.subheader(str(cal_no_constraints(isdasoil_df))+"% able to grow")


# this part returns a dictionary of all the fcc % values mapping by percentage
fcc_dict = {}


for col in list_of_cols:
    value = (new_df[col] == 1).sum()
    total_rows = len(new_df.index)
    percent_of = (value / total_rows) *100
    fcc_dict[col] = percent_of 

def clean_fcc_dict(fcc_dict):
    keys_to_drop = []
    for key,value in fcc_dict.items():
        if value ==0:
            keys_to_drop.append(key)
        else:
            value = value.round(2)
            fcc_dict[key] = value
    
    for item in keys_to_drop:
        del fcc_dict[item]
    
    return fcc_dict

st.write("below shows the average of the soil information")

st.write(clean_fcc_dict(fcc_dict))

st.write("nitrogen:", soil_nitro_avg)
st.write("phosphorous:", soil_phos_avg)
st.write("potassium:", soil_pota_avg)
st.write("pH:", soil_pH)

st.header("Crop Recommender")


# optimal score - state too low or too high

# country is rwanda - temp and rainfall hardcode value


st.write(crop_attribute_df)

suitable_crops = {}

#below appends a list of  crops that meets falls within the range of min max into a dictonary to display into a table
potassium_checker = (soil_pota_avg >= crop_attribute_df["min_potassium"]) & (soil_pota_avg <= crop_attribute_df["max_potassium"])
pota = crop_attribute_df.loc[potassium_checker, "Crop"].tolist()

phosphorus_checker = (soil_phos_avg >= crop_attribute_df["min_phosphorus"]) & (soil_phos_avg <= crop_attribute_df["max_phosphorus"])
pho = crop_attribute_df.loc[phosphorus_checker, "Crop"].tolist()
# st.write(pho)

ph_checker = (soil_pH >= crop_attribute_df["min_ph_soil"]) & (soil_pH <= crop_attribute_df["max_ph_soil"])
ph = crop_attribute_df.loc[ph_checker, "Crop"].tolist()
# st.write(ph)

for crop in pota:
    if crop not in suitable_crops.keys():
        suitable_crops[crop] = ['this area has optimal levels of potassium for {}'.format(crop)]
    else:
        suitable_crops[crop].append('this are has optimal levels of potassium for {}'.format(crop))

for crop in pho:
    if crop not in suitable_crops.keys():
        suitable_crops[crop] = ['this area has optimal levels of phosphorus for {}'.format(crop)]
    else:
        suitable_crops[crop].append("this are has optimal levels of phosphorus for {}".format(crop))

for crop in ph:
    if crop not in suitable_crops.keys():
        suitable_crops[crop] = ['this area has optimal levels of pH levels for {}'.format(crop)]
    else:
        suitable_crops[crop].append("this are has optimal levels of pH levels for {}".format(crop))


st.write(suitable_crops)

for crop in suitable_crops:
    st.subheader(crop)


#converting the dict to df
recommended = pd.DataFrame.from_dict(suitable_crops)
st.write(recommended)


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
