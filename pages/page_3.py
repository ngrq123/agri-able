import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

import utils.functions as functions

# import hydralit_components as hc

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
isdasoil_df = pd.read_csv("data/isdasoil/sample_isdasoil_data_-2.4039269685152282_31.239624023437504_.csv")

description_df = pd.read_csv ("data/crops.csv")

st.header("Properties based on the location you selected: ")

# country-level weather and rainfall
country_code = 'rw' #will come from reverse geocode, hardcode first
country = 'Rwanda' #will come from reverse geocode, hardcode first
st.write(f'Selected country: {country}')

temp = functions.extract_country_weather(country_code, 'temp')
rainfall = functions.extract_country_weather(country_code, 'rainfall')

mean_rainfall = rainfall.mean(axis=1)
mean_temp = temp.mean(axis=1)

isdasoil_df['temp'] = mean_temp[0]
isdasoil_df['rainfall'] = mean_rainfall[0]


# isdasoil_df.insert(loc=0, column='rainfall', value = mean_rainfall[0])
# isdasoil_df.insert(loc=1, column='temp', value = mean_rainfall[0])

isdasoil_df_splice = isdasoil_df[['x_idx', 'y_idx', 'Fertility Capability Classification',
                                'Soil Nitrogen' ,'Soil Phosphorous', 'Soil Potassium', 'Soil pH', 'fcc_description']]
st.write(isdasoil_df_splice)


# this part prints out the distribution of all the soil properties
st.header("Distribution of Soil Properties")
col1, col2 = st.columns(2)
with col1:
    st.subheader("Soil Nitrogen")
    subset = isdasoil_df['Soil Nitrogen']
    counts = subset.value_counts()
    # st.write(counts)
    st.bar_chart(counts)

with col2:
    st.subheader("Soil Phosphorous")
    subset = isdasoil_df['Soil Phosphorous']
    counts = subset.value_counts()
    # st.write(counts)
    st.bar_chart(counts)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Soil Potassium")
    subset = isdasoil_df['Soil Potassium']
    counts = subset.value_counts()
    # st.write(counts)
    st.bar_chart(counts)

with col2:
    st.subheader("Soil pH")
    subset = isdasoil_df['Soil pH']
    counts = subset.value_counts()
    # st.write(counts)
    st.bar_chart(counts)


st.header("Weather and Temperature Information")
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


#getting averages of soil table
soil_nitro_avg = isdasoil_df["Soil Nitrogen"].mean()
soil_phos_avg = isdasoil_df["Soil Phosphorous"].mean()
soil_pota_avg = isdasoil_df["Soil Potassium"].mean()
soil_pH = isdasoil_df["Soil pH"].mean()
fcc_med = isdasoil_df["Fertility Capability Classification"].median()


# constraints_df = isdasoil_df.iloc[:, 8:]

constraints_df = isdasoil_df[['fcc_al_toxicity', 'fcc_calcareous','fcc_gravelly','fcc_high_erosion_risk_-_shallow_depth',
                                'fcc_high_erosion_risk_-_steep_slope','fcc_high_erosion_risk_-_textual_contrast', 
                                'fcc_high_leaching_potential','fcc_low_k', 'fcc_no_constraints', 'fcc_no_data',
                                'fcc_shallow' ,'fcc_slope', 'fcc_sulfidic']]

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


st.header("FCC Information about Selected Plot")
theme_neutral = {'bgcolor': '#f9f9f9','title_color': 'orange','content_color': 'orange','icon_color': 'orange', 'icon': 'fa fa-question-circle'}
theme_good = {'bgcolor': '#EFF8F7','title_color': 'green','content_color': 'green','icon_color': 'green', 'icon': 'fa fa-check-circle'}
col1, col2 = st.columns(2)

def theme(value):
    if float(value) > 50.0:
        return "theme_good"
    else:
        return "theme_neutral"

with col1:
    value = cal_no_constraints(isdasoil_df,list_of_cols)
    card_theme = theme(value)
    # hc.info_card(title= value ,content='Percentage of Land with no constraints',key='first',bar_value=value, theme_override=card_theme)
    
with col2:
    value2 = cal_growable_mods(list_of_cols)
    card_theme = theme(value2)
    # hc.info_card(title=value2, content='Percentage of land growable with modifications',key='sec',bar_value=value2, theme_override=card_theme)


# this part generates the FCC charts
constraints_sum =constraints_df.sum(axis = 0 , skipna = True).to_frame()
constraints_sum.reset_index(inplace=True)
constraints_sum.columns =['fcc','Count']

constraints_sum=constraints_sum[constraints_sum!=0].dropna()

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


col1, col2 = st.columns(2)
with col1:
    st.subheader("Proportion of land with FCC Constraints")
    bar_chart = alt.Chart(constraints_sum).mark_bar().encode(
        y='Count', x='fcc').properties(height=500)
    st.altair_chart(bar_chart, use_container_width=True)
    # st.write(clean_fcc_dict(fcc_dict))

with col2:
    st.subheader("Below shows the average of the soil information:")
    st.write("Nitrogen:", soil_nitro_avg)
    st.write("Phosphorous:", soil_phos_avg)
    st.write("Potassium:", soil_pota_avg)
    st.write("pH Levels:", soil_pH)
    st.write('Rainfall:', mean_rainfall[0])
    st.write('Temperature:', mean_temp[0])




# this part returns a dictionary of all the fcc % values mapping by percentage




st.header("Proposed Modifications")

st.header("Crop Recommender after FCC constraints modifications")


# st.write(crop_attribute_df)

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

mean_temp = mean_temp[0]
mean_rainfall = mean_rainfall[0]
# st.write(mean_rainfall)

temp_checker = (mean_temp >= crop_attribute_df["min_temp"]) & (mean_temp <= crop_attribute_df["max_temp"])
temp = crop_attribute_df.loc[temp_checker, "Crop"].tolist()

rainfall_checker = (mean_rainfall >= crop_attribute_df["min_rainfall"]) & (mean_rainfall <= crop_attribute_df["max_rainfall"])
temp = crop_attribute_df.loc[temp_checker, "Crop"].tolist()

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

for crop in temp:
    if crop not in suitable_crops.keys():
        suitable_crops[crop] = ['this area has optimal levels of temperature levels for {}'.format(crop)]
    else:
        suitable_crops[crop].append("this are has optimal levels of temperature for {}".format(crop))



# st.write(suitable_crops)


suitable_crops = dict(sorted(suitable_crops.items(), key= lambda x: len(x[1]), reverse=True))

# st.write(suitable_crops)

# st.write(description_df)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.subheader("Crops")
with col2:
    st.subheader("Image")
with col3:
    st.subheader("Description")
with col4:
    st.subheader("Suitability")
with col5:
    st.subheader("Adjustments")


for crop in suitable_crops:
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.subheader(crop)

    with col2:
        url = description_df.loc[description_df['Crop'] == crop]['URL'].item()
        st.image(url, use_column_width='always')
        
    
    with col3:
        description = description_df.loc[description_df['Crop'] == crop]['Description'].item()
        st.write(description)

    with col4:
        for desc in suitable_crops[crop]:
            st.write('- ' + desc)
    
    with col5:
        st.write("adjustment")

#converting the dict to df
# recommended = pd.DataFrame.from_dict(suitable_crops)
# st.write(recommended)


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
