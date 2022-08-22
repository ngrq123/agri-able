# from folium.plugins import Draw
from streamlit_folium import st_folium
import folium
import pandas as pd

import utils.extract_isdasoil as isdasoil


def render_page():
    isdasoil.populate_assets()

    # Specify bounding box
    start_lat_lon = (-1.7622, 29.7138) 
    end_lat_lon = (-1.7897, 29.7419)
    midpoint_lat_lon = (
      start_lat_lon[0] + (end_lat_lon[0] - start_lat_lon[0]) / 2,
      start_lat_lon[1] + (end_lat_lon[1] - start_lat_lon[1]) / 2
    )

    fcc_arr, fcc_geojson, _ = isdasoil.get_bbox_data('fcc', start_lat_lon, end_lat_lon)

    fcc_df = pd.DataFrame(fcc_arr[0])
    fcc_df = fcc_df.stack().reset_index()
    fcc_df.columns = ['x_idx', 'y_idx', 'fcc']
    fcc_df['id'] = fcc_df['x_idx'].astype('str') + '|' + fcc_df['y_idx'].astype('str')

    # Plot map
    africa_map = folium.Map(location=midpoint_lat_lon, zoom_start=15)

    folium.Choropleth(
        geo_data=fcc_geojson,
        name='fcc',
        data=fcc_df,
        columns=['id', 'fcc'],
        key_on="feature.id",
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Fertility Capability Classification (FCC)"
    ).add_to(africa_map)

    # folium.Marker(midpoint_lat_lon, tooltip='Midpoint').add_to(africa_map)

    folium.LayerControl().add_to(africa_map)

    st_folium(africa_map)


if __name__ == '__main__':
    render_page()