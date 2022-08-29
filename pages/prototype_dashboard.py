# from folium.plugins import Draw
from folium.plugins import Draw
from shapely.geometry import LineString
from streamlit_folium import st_folium
import folium
import pandas as pd
import streamlit as st

import utils.extract_isdasoil as isdasoil
import utils.functions as functions


DATASET_ID_MAPPING = {
    'Fertility Capability Classification': 'fcc',
    'Soil Nitrogen': 'nitrogen_total',
    'Soil Phosphorous': 'phosphorous_extractable',
    'Soil Potassium': 'potassium_extractable',
    'Soil pH': 'ph'
}

point = st.session_state['point']
vicinity = st.session_state['vicinity']

if 'ASSETS' not in st.session_state:
    st.session_state['ASSETS'] = isdasoil.get_isdasoil_assets()


# Show DataFrame
df = pd.DataFrame([], columns=['x_idx', 'y_idx'])

for dataset in DATASET_ID_MAPPING.keys():
    dataset_id = DATASET_ID_MAPPING[dataset]
    data_arr = isdasoil.get_point_data(dataset_id, point, vicinity)
    temp_df = pd.DataFrame(data_arr[0])
    temp_df = temp_df.stack()
    temp_df = temp_df.reset_index()
    temp_df.columns = ['x_idx', 'y_idx', dataset]
    df = df.merge(temp_df, how='outer', on=['x_idx', 'y_idx'])

# Join with FCC mapping
fcc_mapping_df = isdasoil.get_fcc_mapping()
df = df.merge(fcc_mapping_df, how='left', left_on='Fertility Capability Classification', right_on='fcc_value')
df = df.drop('fcc_value', axis=1)

res = functions.reverse_geocode(point)
df['country'] = res['address']['country']

df.to_csv('sample_isdasoil_data_' + str(point[0]) + '_' + str(point[1]) + '_.csv', index=False)
st.dataframe(df, width=1500)

option = st.selectbox('Select dataset to plot on map:', DATASET_ID_MAPPING.keys(), index=4)
dataset_id = DATASET_ID_MAPPING[option]

if option != 'Fertility Capability Classification':
    geo_json = isdasoil.get_point_geojson(dataset_id, point, vicinity)

    plot_df = df[['x_idx', 'y_idx', option]]
else:
    # Plot number of constraints instead
    option = 'num_constraints'
    df[option] = df[list(isdasoil.FCC_CONSTRAINTS_DICT.keys())].sum(axis=1)
    plot_df = df[['x_idx', 'y_idx', option]]

    temp_arr = plot_df.set_index(['x_idx', 'y_idx']).unstack(level=-1).values
    geo_json = isdasoil.get_point_geojson(dataset_id, point, vicinity, data_arr=temp_arr)

plot_df['id'] = plot_df['x_idx'].astype('str') + '|' + plot_df['y_idx'].astype('str')

# Plot map
zoom_start = 17 + int(vicinity / 1000)
africa_map = folium.Map(location=point, zoom_start=zoom_start)

folium.Choropleth(
    geo_data=geo_json,
    name=dataset_id,
    data=plot_df,
    columns=['id', option],
    key_on="feature.id",
    fill_color="Greens",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name=option
).add_to(africa_map)

folium.Marker(point, tooltip='Selected Point').add_to(africa_map)
folium.LayerControl().add_to(africa_map)
st_folium(africa_map)