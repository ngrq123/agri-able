# from folium.plugins import Draw
from folium.plugins import Draw
from shapely.geometry import LineString
from streamlit_folium import st_folium
import folium
import pandas as pd
import streamlit as st

import utils.extract_isdasoil as isdasoil
import utils.functions as functions

# Config 
st.set_page_config(page_title='AWS-ASDI', 
                   layout='wide', 
                   initial_sidebar_state='expanded')


DATASET_ID_MAPPING = {
    'Fertility Capability Classification': 'fcc',
    'Soil Nitrogen': 'nitrogen_total',
    'Soil Phosphorous': 'phosphorous_extractable',
    'Soil Potassium': 'potassium_extractable',
    'Soil pH': 'ph'
}


def render_page():
    
    # Specify initial bounding box
    start_lat_lon = (-1.7622, 29.7138) 
    end_lat_lon = (-1.7897, 29.7419)
    midpoint_lat_lon = LineString([start_lat_lon, end_lat_lon]).centroid
    midpoint_lat_lon = (midpoint_lat_lon.x, midpoint_lat_lon.y)

    col1, col2 = st.columns([1, 3])

    with col1:
        # Render map
        map = folium.Map(location=midpoint_lat_lon, width='50%', zoom_start=15)
        st.text('Click on your Location on the Map')
        selected_point = st_folium(map, width=1000, height=500)

    with col2:
        if selected_point['last_clicked']:
            point = (selected_point['last_clicked']['lat'], selected_point['last_clicked']['lng'])
            tooltip = 'Selected Point'    
        else:
            point = midpoint_lat_lon
            tooltip ='Default Point'

        res = functions.reverse_geocode(point)
        st.text(f"You selected: {res['display_name']}")
        map = folium.Map(location=point, zoom_start=15)
        folium.Marker(point, tooltip=tooltip).add_to(map)
        st_folium(map, width=1500, height=500)

    vicinity = st.slider('Select area (in metres): ', min_value=0, max_value=3000, value=300)

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

    df['country'] = res['address']['country']

    df.to_csv('sample_isdasoil_data.csv', index=False)
    st.dataframe(df, width=1500)

    option = st.selectbox('Select dataset to plot on map:', DATASET_ID_MAPPING.keys(), index=4)
    dataset_id = DATASET_ID_MAPPING[option]

    # data_arr, geojson, _ = isdasoil.get_bbox_data(dataset_id, start_lat_lon, end_lat_lon)
    geo_json = isdasoil.get_point_geojson(dataset_id, point, vicinity)

    df = pd.DataFrame(data_arr[0])
    df = df.stack().reset_index()
    df.columns = ['x_idx', 'y_idx', dataset_id]
    df['id'] = df['x_idx'].astype('str') + '|' + df['y_idx'].astype('str')

    # Plot map
    africa_map = folium.Map(location=point, zoom_start=15)

    folium.Choropleth(
        geo_data=geo_json,
        name=dataset_id,
        data=df,
        columns=['id', dataset_id],
        key_on="feature.id",
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=option
    ).add_to(africa_map)

    folium.Marker(point, tooltip='Selected Point').add_to(africa_map)
    folium.LayerControl().add_to(africa_map)
    st_folium(africa_map, width=1500)


if __name__ == '__main__':
    render_page()