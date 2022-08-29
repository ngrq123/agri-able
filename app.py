# from folium.plugins import Draw

import pandas as pd
import streamlit as st
import utils.extract_isdasoil as isdasoil


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


def main_page():
    st.markdown("# Main page 🎈")
    st.sidebar.markdown("# Main page 🎈")

def page2():
    st.markdown("# Tables ❄️")
    st.sidebar.markdown("# Tables ❄️")


page_names_to_funcs = {
    "Main Page": main_page,
    "Page 2": page2,
}

selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()