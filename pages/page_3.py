import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

import utils.functions as functions

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

# reading in all the data
crop_attribute_df = pd.read_csv ("data/crop_attributes.csv")
isdasoil_df = pd.read_csv("data/sample_isdasoil_data.csv")

st.header("Properties based on the location you selected: ")

# country-level weather and rainfall
country_code = 'rw' #will come from reverse geocode, hardcode first
country = 'Rwanda' #will come from reverse geocode, hardcode first
st.write(f'Selected country: {country}')

temp = functions.extract_country_weather(country_code, 'temp')
rainfall = functions.extract_country_weather(country_code, 'rainfall')

col1, col2 = st.columns(2)

with col1:
    st.caption(f'Monthly Rainfall in {country} (2021)')
    st.dataframe(rainfall.style.format("{:.2f}"))

    c = alt.Chart(rainfall.T.reset_index(), title=f"Monthly Rainfall in {country}").mark_line().encode(
        alt.X('index',title='Month'),
        alt.Y('rainfall', title='Total Rainfall (mm)'),
        tooltip=[
            alt.Tooltip("index", title="Month"),
            alt.Tooltip("rainfall", title="Total Rainfall (mm)")]
    ).interactive()
    st.altair_chart(c, use_container_width=True)
    st.write(f'Total annual rainfall in {country} is ', float(rainfall.sum(axis=1)))

with col2:
    st.caption(f'Monthly Temperature in {country} (2021)')
    st.dataframe(temp.style.format("{:.2f}"))
    c = alt.Chart(temp.T.reset_index(), title=f"Monthly Temperature in {country}").mark_line().encode(
        alt.X('index',title='Month'),
        alt.Y('temp', title='Average Temp (C)'),
        tooltip=[
            alt.Tooltip("index", title="Month"),
            alt.Tooltip("temp", title="Average Temp (C)")]
    ).interactive()
    st.altair_chart(c, use_container_width=True)
    st.write(f'Average temperature in {country} is ', float(temp.sum(axis=1))/12)

st.write(isdasoil_df)

#getting averages of soil table
soil_nitro_avg = isdasoil_df["Soil Nitrogen"].mean()
soil_phos_avg = isdasoil_df["Soil Phosphorous"].mean()
soil_pota_avg = isdasoil_df["Soil Potassium"].mean()
soil_pH = isdasoil_df["Soil pH"].mean()
fcc_med = isdasoil_df["Fertility Capability Classification"].median()

#splicing out fcc cols for further calculation
constraints_df = isdasoil_df.iloc[:, 8:]
constraints_df = constraints_df.drop('fcc_no_constraints',axis=1)
list_of_cols = list(constraints_df.columns)

# print(list_of_cols)

def cal_no_constraints(filtered_df, cols_list):
    # calculates the % of land with no constraints
    for col in cols_list:
        filtered_df = filtered_df.loc[(filtered_df[col] == 0)]
    
    filtered_len = len(filtered_df)
    total_rows = len(isdasoil_df)
    no_constraints_percent = (filtered_len/total_rows) * 100

    return no_constraints_percent


def cal_growable_mods(cols_list):
    cols_list = cols_list.copy()
    modifiable_list = ['fcc_al_toxicity', 'fcc_calcareous',
                        'fcc_gravelly','fcc_high_erosion_risk_-_shallow_depth',
                        'fcc_high_erosion_risk_-_steep_slope', 'fcc_high_leaching_potential',
                        'fcc_low_k','fcc_no_constraints',
                        'fcc_shallow','fcc_slope','fcc_sulfidic']

    for col in modifiable_list:
        if col in cols_list:
            # print(col)
            cols_list.remove(col)
    
    # st.write(cols_list)
    # print(cols_list)    
    value = cal_no_constraints(isdasoil_df,cols_list)
    return value

col1, col2 = st.columns(2)
with col1:
    st.subheader("Percentage of Land with no constraints")
    st.write(str(cal_no_constraints(isdasoil_df,list_of_cols))+"% able to grow")
with col2:
    st.subheader("Percentage of land growable with modifications")
    st.write(str(cal_growable_mods(list_of_cols))+ "% able to grow")


# this part generates the FCC charts
constraints_sum =constraints_df.sum(axis = 0 , skipna = True).to_frame()
constraints_sum.reset_index(inplace=True)
constraints_sum.columns =['fcc','Count']

constraints_sum=constraints_sum[constraints_sum!=0].dropna()


bar_chart = alt.Chart(constraints_sum).mark_bar().encode(
    y='Count', x='fcc').properties(height=500)
st.altair_chart(bar_chart, use_container_width=True)




# this part returns a dictionary of all the fcc % values mapping by percentage
fcc_dict = {}


for col in list_of_cols:
    value = (constraints_df[col] == 1).sum()
    total_rows = len(constraints_df.index)
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
# pota.append('lentil')

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


# st.write(suitable_crops)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.subheader("Crops")
with col2:
    st.subheader("Description")
with col3:
    st.subheader("Suitability")
with col4:
    st.subheader("Modifiers")

for crop in suitable_crops:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.subheader(crop)
        st.write("insert image")
    
    with col2:
        st.write("lorem-ipsum")
    
    with col3:
        for desc in suitable_crops[crop]:
            st.write('- ' + desc)


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
