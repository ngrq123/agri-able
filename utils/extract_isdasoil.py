# Reference: https://github.com/iSDA-Africa/isdasoil-tutorial

from pyproj import Transformer
from pystac import Catalog
import pandas as pd
import geojson
import numpy as np
import rasterio as rio
import streamlit as st


ASSETS = dict()
CONVERSION_FUNCS_DICT = {
    "x": np.vectorize(lambda x: x),
    "x/10": np.vectorize(lambda x: x/10, otypes=["float32"]),
    "x/100": np.vectorize(lambda x: x/100, otypes=["float32"]),
    "expm1(x/10)": np.vectorize(lambda x: np.expm1(x / 10), otypes=["float32"]),
    "%3000": np.vectorize(lambda x: int(x%3000), otypes=["int16"])
}


@st.cache
def populate_assets():
    print('Populating iSDAsoil assets...')
    catalog = Catalog.from_file("https://isdasoil.s3.amazonaws.com/catalog.json")

    for root, catalogs, items in catalog.walk():
        for item in items:
            for asset in item.assets.values():
                if asset.roles == ['data']:
                    # save all items to a dictionary as we go along
                    ASSETS[item.id] = item
    
    print('Populated iSDAsoil assets!')


def get_url(id):    
    return ASSETS[id].assets['image'].href 


def get_bbox_data(id, start_lat_lon, end_lat_lon):
    '''
    :param id: id of dataset
    :param start_lat_lon: upper left corner of the bounding box as lat, lon
    :param end_lat_lon: lower right corner of the bounding box as lat, lon
    :return: numpy array of the dataset, metadata required for writing back to tiff file
    '''

    file_location = get_url(id)

    with rio.open(file_location) as file:
        transformer = Transformer.from_crs("epsg:4326", file.crs)

        # convert the data from lat/lon to x,y coords of the source dataset crs
        start_coords = transformer.transform(start_lat_lon[0], start_lat_lon[1])
        end_coords = transformer.transform(end_lat_lon[0], end_lat_lon[1])
        # print('Bounds:', file.bounds)

        # get the location of the pixel at the given location (in lon/lat (x/y) order))
        start_coords= file.index(start_coords[0], start_coords[1])
        end_coords=file.index(end_coords[0], end_coords[1])

        window = rio.windows.Window(start_coords[1], start_coords[0], end_coords[1] - start_coords[1], end_coords[0] - start_coords[0])

        print('Getting data from file')
        arr = file.read(window=window)

        new_profile = file.profile.copy()

        # Get lon/lat
        transformer = Transformer.from_crs(file.crs, "epsg:4326")
        # grid_arr = np.zeros((arr.shape[1], arr.shape[2], 2))  # Last dim is 2 for lon/lat
        print('Populating GeoJSON')
        geo_json = []
        for x_idx in range(start_coords[0], end_coords[0]):
            for y_idx in range(start_coords[1], end_coords[1]):
                # Create polygon
                polygon_coords = []
                for offset in ['ul', 'll', 'lr', 'ur']:
                    coords = file.xy(x_idx, y_idx, offset=offset)
                    coords = transformer.transform(*coords)
                    polygon_coords.append([coords[1], coords[0]])
                polygon = geojson.Polygon([polygon_coords])

                # Offset indexes by file's index
                x_idx_offsetted = x_idx - start_coords[0]
                y_idx_offsetted = y_idx - start_coords[1]
                xy_idx_offsetted = str(x_idx_offsetted) + '|' + str(y_idx_offsetted)
                geo_json.append(geojson.Feature(geometry=polygon, id=xy_idx_offsetted, properties={'x_idx': x_idx_offsetted, 'y_idx': y_idx_offsetted}))
        geo_json = geojson.FeatureCollection(geo_json)
    
    new_profile.update({
        'height': window.height,
        'width': window.width,
        'count': file.count,
        'transform': file.window_transform(window)
    })

    arr = _back_transform(id, arr)

    return arr, geo_json, new_profile


def _back_transform(id, data):
    print('Transforming data')
    conversion = ASSETS[id].extra_fields['back-transformation']
    return CONVERSION_FUNCS_DICT[conversion](data)
