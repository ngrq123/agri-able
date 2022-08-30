import requests
import pandas as pd
import streamlit as st
import requests

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
        df = pd.read_csv(f"data/{variable}_forecasted.csv")
        df = df[df['country_code_alpha2'] == country_code].iloc[:,-12:].reset_index(drop=True)
        df.columns = pd.to_datetime(df.columns).date
        df.index=[variable]
        return df

def hover_line_chart(data,x,y,x_title, y_title, title):
    hover = alt.selection_single(
        fields=[x],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data, title=title).mark_line().encode(
            alt.X(x, title=x_title),
            alt.Y(y, title=y_title)
        )
    )
    points = lines.transform_filter(hover).mark_circle(size=65)

    # Draw a rule at the location of the selection
    tooltips = (
        alt.Chart(data)
        .mark_rule()
        .encode(
            x=x,
            y=y,
            opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
            tooltip=[
                alt.Tooltip(x, title=x_title),
                alt.Tooltip(y, title=y_title),
            ],
        )
        .add_selection(hover)
    )
    return (lines + points + tooltips).interactive()

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