# from folium.plugins import Draw
from streamlit_folium import st_folium
import folium
import pandas as pd
import streamlit as st

import utils.extract_isdasoil as isdasoil


def render_page():
    isdasoil.populate_assets()

    dataset_id_mapping = {
        'Fertility Capability Classification': 'fcc',
        'Soil Nitrogen': 'nitrogen_total',
        'Soil Phosphorous': 'phosphorous_extractable',
        'Soil Potassium': 'potassium_extractable',
        'Soil pH': 'ph'
    }

    option = st.selectbox('Select dataset:', dataset_id_mapping.keys())
    dataset_id = dataset_id_mapping[option]

    # Specify bounding box
    start_lat_lon = (-1.7622, 29.7138) 
    end_lat_lon = (-1.7897, 29.7419)
    midpoint_lat_lon = (
      start_lat_lon[0] + (end_lat_lon[0] - start_lat_lon[0]) / 2,
      start_lat_lon[1] + (end_lat_lon[1] - start_lat_lon[1]) / 2
    )

    data_arr, geojson, _ = isdasoil.get_bbox_data(dataset_id, start_lat_lon, end_lat_lon)

    df = pd.DataFrame(data_arr[0])
    df = df.stack().reset_index()
    df.columns = ['x_idx', 'y_idx', dataset_id]
    df['id'] = df['x_idx'].astype('str') + '|' + df['y_idx'].astype('str')

    # Plot map
    africa_map = folium.Map(location=midpoint_lat_lon, zoom_start=15)

    folium.Choropleth(
        geo_data=geojson,
        name=dataset_id,
        data=df,
        columns=['id', dataset_id],
        key_on="feature.id",
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=option
    ).add_to(africa_map)

    # folium.Marker(midpoint_lat_lon, tooltip='Midpoint').add_to(africa_map)

    folium.LayerControl().add_to(africa_map)

    st_folium(africa_map)


if __name__ == '__main__':
    render_page()