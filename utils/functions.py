import requests
import pandas as pd
import streamlit as st

def reverse_geocode(lat_lon):
    """
    Calls the Nominatim API to conduct reverse geocoding.
    See https://nominatim.org/release-docs/develop/api/Reverse/ for more.
    :param lat_lon: tuple of latitude and longitude of selected location
    :return: response: response in json format.
    """
    URL = 'https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lon}'
    r = requests.get(URL.format(lat=lat_lon[0],lon=lat_lon[1]))
    response = r.json()

    return response

def extract_country_weather(country_code, variable):
    """
    Given a country_code, extracts rainfall/temp data from csv and performs some preprocessing.
    :param country_code: String, Alpha-2 country code (e.g. RW for rwanda)
    :param variable: String, only either 'rainfall' or 'temp' accepted.
    :return:
    """
    if variable not in ['rainfall', 'temp']:
        raise Exception('not yet implemented')
    else:
        country_code = str.upper(country_code)
        df = pd.read_csv(f"data/africa_{variable}_cleaned_2021.csv")
        df = df[df['country_code_alpha2'] == country_code].iloc[:,-12:].reset_index(drop=True)
        df.columns = pd.to_datetime([str(i) + '/2021' for i in range(1, 13)]).date
        df.index=[variable]
        return df

def initialise_app():
    # Config 
    st.set_page_config(page_title='AWS-ASDI', 
                    layout='wide', 
                    initial_sidebar_state='expanded')

    if 'point' not in st.session_state:
        st.session_state['point'] = (-1.77595, 29.72785)

    if 'vicinity' not in st.session_state:
        st.session_state['vicinity'] = 300

    if 'is_selected' not in st.session_state:
        st.session_state['is_selected'] = False