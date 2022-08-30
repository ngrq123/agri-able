import streamlit as st


content = open('README.md', 'r', encoding='utf8')
content = content.read()  # .replace('./images/', 'https://github.com/ngrq123/agri-able/blob/main/images/')
st.markdown(content, unsafe_allow_html=True)