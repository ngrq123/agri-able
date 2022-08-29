import streamlit as st

col1, col2 = st.columns(2)

feature_dict = {
    'ph': 'pH',
    'potassium': 'Potassium',
    'phosphorus': 'Phosphorus'
}

with col1:
    st.markdown('Too High')
    for feature_key in feature_dict:
        feature = feature_dict[feature_key]
        with st.expander(feature, expanded=True):
            content = open('./data/adjs/' + feature_key + '_high_summary.md', 'r', encoding='utf8')
            content = content.read()
            st.markdown(content, unsafe_allow_html=True)

with col2:
    st.markdown('Too Low')
    for feature_key in feature_dict:
        feature = feature_dict[feature_key]
        with st.expander(feature, expanded=True):
            content = open('./data/adjs/' + feature_key + '_low_summary.md', 'r', encoding='utf8')
            content = content.read()
            st.markdown(content, unsafe_allow_html=True)